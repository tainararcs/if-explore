"""Contrato JSON da API do acervo.

Os campos são declarados em snake_case e saem em camelCase (`areaId`, `pageSize`),
como no tipo `Book` do frontend. Valores ausentes saem como `null`.
"""

from __future__ import annotations

import datetime as dt
from typing import Literal

from ninja import Schema
from pydantic import ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel

from catalog.models import Book, CopyStatus, Course, KnowledgeArea, LiteraryGenre
from catalog.services.discovery import MAX_EXCLUDED, MAX_QUERY_LENGTH, MIN_QUERY_LENGTH, normalize_query

ShelfKind = Literal["forYou", "becauseYouChose", "moreFromArea", "forPleasure"]


class CamelSchema(Schema):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


# ---- taxonomia
class AreaOut(CamelSchema):
    id: str
    name: str

    @classmethod
    def from_model(cls, area: KnowledgeArea) -> AreaOut:
        return cls(id=area.slug, name=area.name)


class CourseOut(CamelSchema):
    id: str
    name: str
    area_id: str
    level: str

    @classmethod
    def from_model(cls, course: Course) -> CourseOut:
        return cls(id=course.slug, name=course.name, area_id=course.area_id, level=course.level)


class GenreOut(CamelSchema):
    id: str
    name: str

    @classmethod
    def from_model(cls, genre: LiteraryGenre) -> GenreOut:
        return cls(id=genre.slug, name=genre.name)


# ---- livros
class CopiesOut(CamelSchema):
    """Exemplares do título. Ausente (`null` no livro) até a primeira leitura."""

    total: int
    #: Situação para o visitante (ver `CopyStatus`).
    status: CopyStatus
    #: Exemplares livres; só conhecido quando a consulta ao vivo é a leitura mais recente.
    available: int | None
    #: Quando a situação foi lida no PHL (em lote ou ao vivo).
    updated_at: dt.datetime

    @classmethod
    def from_model(cls, book: Book) -> CopiesOut | None:
        """Exemplares do livro, ou None se ainda não foram lidos."""
        times = [moment for moment in (book.copies_synced_at, book.copies_checked_at) if moment is not None]
        if not book.copy_status or book.copies_total is None or not times:
            return None
        live_is_latest = book.copies_checked_at is not None and (
            book.copies_synced_at is None or book.copies_checked_at >= book.copies_synced_at)
        return cls(total=book.copies_total, status=CopyStatus(book.copy_status),
                   available=book.copies_available if live_is_latest else None, updated_at=max(times))


class BookLinkOut(CamelSchema):
    label: str
    url: str


class BookSummaryOut(CamelSchema):
    """Livro como aparece em listas, prateleiras e resultados de busca."""

    id: str
    title: str
    subtitle: str | None
    authors: list[str]
    year: int | None
    area_id: str | None
    course_ids: list[str]
    genre_ids: list[str]
    subjects: list[str]
    synopsis: str | None
    #: CDD e cutter, usados para achar o livro na estante.
    call_number: str | None
    isbn: str | None
    publisher: str | None
    edition: str | None
    pages: int | None
    #: Tipo como o catálogo exibe ("Livro", "Periódico").
    document_type: str | None
    cover_url: str | None
    copies: CopiesOut | None

    @staticmethod
    def fields_from(book: Book) -> dict[str, object]:
        """Campos comuns a partir de um livro com as relações pré-carregadas
        (ver `catalog.services.books.with_relations`)."""
        return {
            "id": book.id, "title": book.title, "subtitle": book.subtitle or None,
            "authors": [link.author.name for link in book.bookauthor_set.all()],
            "year": book.year, "area_id": book.area_id,
            "course_ids": [course.slug for course in book.courses.all()],
            "genre_ids": [genre.slug for genre in book.genres.all()],
            "subjects": [subject.name for subject in book.subjects.all()],
            "synopsis": book.synopsis or None, "call_number": book.call_number or None,
            "isbn": book.isbn or None, "publisher": book.publisher or None,
            "edition": book.edition or None, "pages": book.pages,
            "document_type": book.document_type or None, "cover_url": book.cover_url or None,
            "copies": CopiesOut.from_model(book),
        }

    @classmethod
    def from_model(cls, book: Book) -> BookSummaryOut:
        return cls(**cls.fields_from(book))


class BookDetailOut(BookSummaryOut):
    """Livro completo, para a página do título."""

    contributors: str | None
    city: str | None
    country: str | None
    volume: str | None
    series: str | None
    physical_description: str | None
    issn: str | None
    issue: str | None
    languages: list[str]
    notes: list[str]
    #: Arquivos digitais: PDF do TCC ou e-book, termo de autorização, apresentação.
    links: list[BookLinkOut]
    tcc_course: str | None
    cataloged_at: dt.date | None
    #: Empréstimos já feitos, somando os exemplares; null até a consulta ao vivo.
    loans: int | None

    @classmethod
    def from_model(cls, book: Book) -> BookDetailOut:
        return cls(
            **cls.fields_from(book),
            contributors=book.contributors or None, city=book.city or None,
            country=book.country or None, volume=book.volume or None, series=book.series or None,
            physical_description=book.physical_description or None, issn=book.issn or None,
            issue=book.issue or None, languages=book.languages, notes=book.notes,
            links=[BookLinkOut(label=link["label"], url=link["url"]) for link in book.links],
            tcc_course=book.tcc_course or None, cataloged_at=book.cataloged_at, loans=book.loans_total,
        )


class BookPageOut(CamelSchema):
    items: list[BookSummaryOut]
    total: int
    page: int
    page_size: int


class SameAuthorOut(CamelSchema):
    author: str
    books: list[BookSummaryOut]


class RelatedOut(CamelSchema):
    """Leituras relacionadas: outros livros de um autor em comum (quando há ao menos
    dois) e os demais por afinidade."""

    same_author: SameAuthorOut | None
    related: list[BookSummaryOut]


# ---- recomendações
class ProfileIn(CamelSchema):
    """Preferências do visitante, como o frontend guarda no navegador. Ids
    desconhecidos são ignorados."""

    area_ids: list[str] = Field(default_factory=list, max_length=20)
    course_ids: list[str] = Field(default_factory=list, max_length=40)
    seed_book_ids: list[str] = Field(default_factory=list, max_length=20)
    genre_ids: list[str] = Field(default_factory=list, max_length=20)


class ShelfOut(CamelSchema):
    """Prateleira; `subject` completa o título (livro, área ou gênero) quando o tipo exige."""

    id: str
    kind: ShelfKind
    subject: str | None
    books: list[BookSummaryOut]


class RecommendationsOut(CamelSchema):
    shelves: list[ShelfOut]
    #: Áreas escolhidas, usadas na saudação e no filtro.
    areas: list[AreaOut]


# ---- descoberta com IA
class DiscoveryIn(CamelSchema):
    """Pedido em texto livre e, opcionalmente, as preferências salvas e os livros
    já sugeridos (para pedir outras sugestões)."""

    query: str = Field(min_length=MIN_QUERY_LENGTH, max_length=MAX_QUERY_LENGTH)
    profile: ProfileIn | None = None
    exclude_ids: list[str] = Field(default_factory=list, max_length=MAX_EXCLUDED)

    @field_validator("query")
    @classmethod
    def _normalized_query(cls, value: str) -> str:
        query = normalize_query(value)
        if len(query) < MIN_QUERY_LENGTH:
            raise ValueError("o pedido precisa ter pelo menos %d caracteres" % MIN_QUERY_LENGTH)
        return query


class DiscoveryItemOut(CamelSchema):
    book: BookSummaryOut
    #: Por que o livro atende ao pedido; null na seleção por regras.
    reason: str | None


class DiscoveryOut(CamelSchema):
    #: "ai": escolhido pelo Gemini; "rules": a IA não respondeu e a seleção é por regras.
    source: Literal["ai", "rules"]
    #: Frase da IA para o visitante; null na seleção por regras.
    message: str | None
    items: list[DiscoveryItemOut]


class ExplanationOut(CamelSchema):
    """Explicação simplificada gerada por IA; `text` é null quando não há."""

    text: str | None
    generated_at: dt.datetime | None


# ---- status
class SyncOut(CamelSchema):
    finished_at: dt.datetime
    stats: dict[str, float]


class StatusOut(CamelSchema):
    active_books: int
    #: Títulos com a situação dos exemplares já lida no PHL.
    books_with_copies: int
    #: Última sincronização concluída do catálogo; null se nunca houve.
    catalog_sync: SyncOut | None
