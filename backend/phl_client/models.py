"""Modelos com tipos previsíveis, prontos para uso: Copy, Book e SearchResult."""

from __future__ import annotations

import csv
import dataclasses
import datetime as dt
import json
import re
from collections.abc import Iterable
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

from .fields import (
    BIBLIOGRAPHIC_LEVELS, KNOWLEDGE_AREAS, LANGUAGES, LIBRARY_CODE, MEDIA, PLACEHOLDER_COVER_FILES, Record,
)
from .isbn import isbn_digits
from .parsers import CopyRow
from .text import clean_text, first_int, first_text, normalize, text_list, to_plain

if TYPE_CHECKING:
    from .library import Library

# Rótulo exibido para cada situação de exemplar.
COPY_STATUS_LABELS = {
    "available": "disponível", "on_loan": "emprestado", "in_library_use": "consulta local",
    "unavailable": "indisponível", "reserved": "reservado",
}
# Campos de link do registro e o rótulo usado quando o texto do link não ajuda.
LINK_RECORD_FIELDS = (
    ("document", "Documento"),
    ("authorization_document", "Termo de autorização"),
    ("presentation_document", "Apresentação"),
)


class BookLink(TypedDict):
    """Arquivo digital do título: PDF do TCC ou e-book, termo, apresentação."""

    label: str
    url: str


@dataclasses.dataclass(frozen=True)
class Copy:
    """Um exemplar físico. Não guarda quem está com ele (dado pessoal)."""

    accession_number: str
    label: str
    #: available | on_loan | in_library_use | unavailable | reserved | unknown
    status: str
    due_date: dt.date | None
    loans: int
    renewals: int
    note: str | None = None

    @classmethod
    def from_row(cls, row: CopyRow) -> Copy:
        """Cria o exemplar a partir de uma linha de `parse_copies`."""
        try:
            due_date = dt.datetime.strptime(row.get("due_date") or "", "%d/%m/%Y").date()
        except ValueError:
            due_date = None
        return cls(row.get("accession_number", ""), row.get("label", ""), row.get("status", "unknown"),
                   due_date, first_int(row.get("loans")) or 0, first_int(row.get("renewals")) or 0,
                   clean_text(row.get("note")))

    @property
    def is_available(self) -> bool:
        return self.status == "available"

    def __str__(self) -> str:
        status = COPY_STATUS_LABELS.get(self.status, self.status.replace("_", " "))
        due = " (devolução %s)" % self.due_date.strftime("%d/%m/%Y") if self.due_date else ""
        return "%-7s %-32s %s%s" % (self.accession_number, self.label, status, due)


@dataclasses.dataclass(eq=False, repr=False)
class Book:
    """Um título do acervo, com tipos previsíveis.

    `authors`, `subjects`, `contents_notes`, `notes`, `languages`, `course_codes` e
    `links` são sempre listas; `year` e `pages` são int ou None; `cataloged_at` é date
    ou None; texto ausente é None. `raw` guarda o registro original do PHL.

    `copies`, `reference`, `available_count`, `is_available` e `loans` consultam o
    servidor na primeira vez e ficam guardados no objeto.
    """

    id: str
    title: str
    subtitle: str | None
    authors: list[str]
    #: Tradução, ilustração, orientação ("Trad. por: Fabiane Fiorini").
    contributors: str | None
    publisher: str | None
    city: str | None
    country: str | None
    #: Ano de publicação já convertido; None quando o catálogo traz '[s.d.]' e afins.
    year: int | None
    edition: str | None
    volume: str | None
    series: str | None
    pages: int | None
    physical_description: str | None
    #: Só os dígitos.
    isbn: str | None
    issn: str | None
    issue: str | None
    volume_year: str | None
    cdd: str | None
    cutter: str | None
    subjects: list[str]
    #: Notas de conteúdo: em muitos livros a sinopse da editora, em outros o sumário.
    contents_notes: list[str]
    #: Notas gerais e da equipe ("Acompanha 01 CD").
    notes: list[str]
    #: Observação interna do cadastro ("Livro sem condições de uso, baixa em 24/09/26").
    remarks: str | None
    languages: list[str]
    #: Suporte no cadastro; "Folheto" é o padrão em ~60% do acervo, não o formato real.
    medium: str | None
    #: Área do conhecimento (CNPq) por extenso.
    area: str | None
    #: Tipo de documento como o catálogo exibe ("Livro", "Periódico").
    document_type: str | None
    #: monograph | serial | serial_article | monograph_part
    bibliographic_level: str | None
    #: Cursos cuja bibliografia inclui o título, pelos códigos do PHL.
    course_codes: list[str]
    #: Nome do curso, só em TCCs ("Nutrição").
    tcc_course: str | None
    links: list[BookLink]
    cover_url: str | None
    #: Quando o registro entrou no catálogo (não é o ano de publicação).
    cataloged_at: dt.date | None
    raw: Record
    _library: Library | None = dataclasses.field(default=None, compare=False)

    @classmethod
    def from_record(cls, record: Record, library: Library | None = None) -> Book:
        """Cria o livro a partir de um registro de `parse_records`.

        Args:
            record: Registro com `title_id`.
            library: Usada pelas propriedades que consultam o servidor; sem ela, só os
                dados locais funcionam.
        """
        # O 065 é a data de entrada em ~92% dos registros; em ~6% é só o ano (AAAA0000).
        date_text = first_text(record.get("standardized_date")) or ""
        try:
            cataloged_at = (dt.date(int(date_text[:4]), int(date_text[4:6]), int(date_text[6:]))
                            if re.fullmatch(r"\d{8}", date_text) and date_text[6:] != "00" else None)
        except ValueError:
            cataloged_at = None
        isbns = [digits for digits in map(isbn_digits, text_list(record.get("isbn"))) if digits]
        year = record.get("year_number")

        def link_label(field: str, default: str) -> str:
            # o texto do link é "TCC (Clique aqui)": o rótulo fica só "TCC"
            text = re.sub(r"(?i)clique aqui", "", clean_text(record.get(field)) or "")
            return text.strip("() ") or default

        links: list[BookLink] = [{"label": link_label(field, default), "url": url}
                                 for field, default in LINK_RECORD_FIELDS
                                 for url in text_list(record.get(field + "_url"))]
        # Sem link, o 092 é uma nota da equipe ("Acompanha CD", "NÃO POSSUI IMAGEM!"),
        # exceto quando é o rótulo de um link quebrado ("Termo de Autorização").
        staff_notes = [] if record.get("authorization_document_url") else [
            note for note in text_list(record.get("authorization_document"))
            if not normalize(note).startswith("termo de autorizacao")]
        return cls(
            id=str(record["title_id"]),
            title=clean_text(record.get("title")) or "(sem título)",
            subtitle=clean_text(record.get("subtitle")),
            authors=text_list(record.get("author")),
            contributors=clean_text(record.get("credits")),
            publisher=clean_text(record.get("publisher")),
            city=clean_text(record.get("city")),
            country=clean_text(record.get("country")),
            year=year if isinstance(year, int) else None,
            edition=clean_text(record.get("edition")),
            volume=clean_text(record.get("volume")),
            series=clean_text(record.get("series")),
            pages=first_int(record.get("pages")),
            physical_description=clean_text(record.get("physical_description")),
            isbn=isbns[0] if isbns else None,
            issn=clean_text(record.get("issn")),
            issue=clean_text(record.get("issue")),
            volume_year=clean_text(record.get("volume_year")),
            cdd=clean_text(record.get("classification")),
            cutter=clean_text(record.get("cutter")),
            subjects=text_list(record.get("subjects")),
            contents_notes=text_list(record.get("contents_notes")),
            notes=text_list(record.get("general_notes")) + staff_notes,
            remarks=clean_text(record.get("remarks")),
            languages=list(dict.fromkeys(LANGUAGES.get(code, code)
                                         for code in text_list(record.get("language_code")))),
            medium=MEDIA.get(first_text(record.get("medium_code")) or ""),
            area=KNOWLEDGE_AREAS.get(first_text(record.get("knowledge_area")) or ""),
            document_type=clean_text(record.get("document_type")),
            bibliographic_level=BIBLIOGRAPHIC_LEVELS.get(first_text(record.get("bibliographic_level")) or ""),
            # ~30 registros têm texto digitado no campo de curso (sinopses, assuntos):
            # só códigos numéricos são cursos.
            course_codes=[code for code in text_list(record.get("course")) if code.isdigit()],
            tcc_course=clean_text(record.get("tcc_course")),
            links=links,
            cover_url=_cover_url(record),
            cataloged_at=cataloged_at,
            raw=record,
            _library=library,
        )

    # ---- derivados (sem rede)
    @property
    def full_title(self) -> str:
        return "%s: %s" % (self.title, self.subtitle) if self.subtitle else self.title

    @property
    def call_number(self) -> str:
        """Número de chamada (CDD e cutter), usado para achar o livro na estante."""
        return " ".join(part for part in (self.cdd, self.cutter) if part)

    @property
    def synopsis(self) -> str | None:
        """As notas de conteúdo num texto só."""
        return " ".join(self.contents_notes) or None

    # ---- consultam o servidor (1ª vez)
    def _require_library(self) -> Library:
        if self._library is None:
            raise RuntimeError("livro criado sem Library: não há como consultar o servidor")
        return self._library

    @cached_property
    def copies(self) -> list[Copy]:
        return [Copy.from_row(row) for row in self._require_library().phl.copies(self.id, LIBRARY_CODE)]

    @cached_property
    def reference(self) -> str | None:
        """Referência bibliográfica pronta, gerada pelo servidor."""
        return self._require_library().phl.abnt_reference(self.id)

    @property
    def available_count(self) -> int:
        return sum(copy.is_available for copy in self.copies)

    @property
    def is_available(self) -> bool:
        return self.available_count > 0

    @property
    def loans(self) -> int:
        """Total de empréstimos já feitos (só o total: não há datas nem quem pegou)."""
        return sum(copy.loans for copy in self.copies)

    # ---- apresentação
    def to_dict(self, include_copies: bool = False) -> dict[str, object]:
        """Dicionário pronto para JSON.

        Args:
            include_copies: Inclui `copies`, `available_count` e `loans` (consulta o servidor).
        """
        data: dict[str, object] = {name: getattr(self, name) for name in (
            "id", "title", "subtitle", "authors", "contributors", "publisher", "city", "country",
            "year", "edition", "volume", "series", "pages", "physical_description", "isbn", "issn",
            "issue", "volume_year", "cdd", "cutter", "subjects", "languages", "medium", "area",
            "document_type", "bibliographic_level", "course_codes", "tcc_course", "links",
            "cover_url", "synopsis", "notes", "remarks")}
        data["cataloged_at"] = self.cataloged_at.isoformat() if self.cataloged_at else None
        if include_copies:
            data["copies"] = [dict(dataclasses.asdict(copy),
                                   due_date=copy.due_date.isoformat() if copy.due_date else None)
                              for copy in self.copies]
            data["available_count"], data["loans"] = self.available_count, self.loans
        return data

    def summary(self) -> str:
        """Ficha em texto com tudo sobre o livro (consulta o servidor: exemplares e referência)."""
        data = self.to_dict()
        data["reference"] = self.reference
        lines = [self.full_title, "─" * min(80, len(self.full_title))]
        lines += ["%-14s %s" % (name + ":", to_plain(value)) for name, value in data.items()
                  if value not in (None, "", []) and name not in ("title", "subtitle")]
        copies = self.copies
        lines.append("exemplares:   %d (%d disponíveis, %d empréstimo(s) no total)"
                     % (len(copies), self.available_count, self.loans))
        return "\n".join(lines + ["  " + str(copy) for copy in copies])

    def __str__(self) -> str:
        return "%s — %s%s" % (self.title, "; ".join(self.authors) or "s/ autor",
                              " (%d)" % self.year if self.year else "")

    def __repr__(self) -> str:
        return "Book(id=%r, title=%r, year=%r)" % (self.id, self.title, self.year)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Book) and other.id == self.id

    def __hash__(self) -> int:
        return hash(self.id)


def _cover_url(record: Record) -> str | None:
    """URL da capa, ou None quando o cadastro aponta para a imagem "sem capa"."""
    url = clean_text(record.get("cover_image"))
    if url and url.rsplit("/", 1)[-1].lower() in PLACEHOLDER_COVER_FILES:
        return None
    return url


# Atributos públicos de Book aceitos como colunas em SearchResult.to_markdown.
BOOK_COLUMNS = frozenset(
    [field.name for field in dataclasses.fields(Book) if not field.name.startswith("_") and field.name != "raw"]
    + [name for name, value in vars(Book).items()
       if not name.startswith("_") and isinstance(value, (property, cached_property))]
)


class SearchResult(list[Book]):
    """Lista de `Book` com o total da busca.

    `total` diz quantos livros correspondem ao todo; `truncated` é True quando o
    limite deixou algum de fora. Fatiar devolve uma `list` comum, sem esses atributos.
    """

    def __init__(self, books: Iterable[Book] = (), *, total: int | None = None, truncated: bool = False):
        super().__init__(books)
        self.total = len(self) if total is None else total
        self.truncated = truncated

    def __repr__(self) -> str:
        return "<SearchResult: %d livro(s)%s>" % (
            len(self), ", truncado (total %s)" % self.total if self.truncated else "")

    def to_markdown(self, columns: Iterable[str] = ("title", "authors", "year", "publisher"),
                    width: int = 60) -> str:
        """Tabela Markdown com atributos de `Book` como colunas.

        Colunas como `available_count` consultam o servidor, uma requisição por livro.

        Raises:
            ValueError: Quando uma coluna não é atributo de `Book`, mesmo com a lista vazia.
        """
        columns = list(columns)
        for column in columns:
            if column not in BOOK_COLUMNS:
                raise ValueError("coluna %r desconhecida. Opções: %s" % (column, ", ".join(sorted(BOOK_COLUMNS))))

        def cell(value: object) -> str:
            plain = to_plain(value)
            text = "—" if plain in (None, "") else str(plain).replace("|", "\\|").replace("\n", " ")
            return text if len(text) <= width else text[:width - 1] + "…"

        headers = {"title": "Título", "authors": "Autor(es)", "isbn": "ISBN", "cdd": "CDD",
                   "pages": "Págs.", "id": "Código"}
        lines = ["| # | " + " | ".join(headers.get(c, c.capitalize()) for c in columns) + " |",
                 "|--:|" + "---|" * len(columns)]
        lines += ["| %d | %s |" % (i, " | ".join(cell(getattr(book, c)) for c in columns))
                  for i, book in enumerate(self, 1)]
        return "\n".join(lines)

    def save(self, path: str | Path) -> Path:
        """Grava em .csv (abre no Excel) ou .json, conforme a extensão.

        Raises:
            ValueError: Quando a extensão não é .csv nem .json.
        """
        path, rows = Path(path), [book.to_dict() for book in self]
        if path.suffix.lower() == ".json":
            path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        elif path.suffix.lower() == ".csv":
            with path.open("w", newline="", encoding="utf-8-sig") as file:
                writer = csv.DictWriter(file, fieldnames=list(rows[0]) if rows else ["id"])
                writer.writeheader()
                writer.writerows({key: to_plain(value) for key, value in row.items()} for row in rows)
        else:
            raise ValueError("use uma extensão .csv ou .json: %r" % str(path))
        return path
