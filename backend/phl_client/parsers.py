"""Conversão das páginas do OPAC em dados. Não usam a rede e podem ser testados
com páginas de exemplo."""

from __future__ import annotations

import html
import re
import urllib.parse
from typing import NamedTuple, TypedDict

from .errors import LibraryError
from .fields import COPY_STATUS_BY_GIF, FIELDS, LINK_FIELDS, REPEATABLE_FIELDS, Record
from .text import first_text


class CopyRow(TypedDict, total=False):
    """Linha da tela de exemplares, com os textos como aparecem no OPAC."""

    accession_number: str
    note: str
    label: str
    status: str
    due_date: str
    #: Matrícula de quem está com o exemplar; só presente com include_borrower=True.
    borrower: str
    loans: str
    renewals: str


class CopyStatusItem(TypedDict):
    """Resumo dos exemplares de um título no formato 'decorado' do OPAC."""

    #: None quando o servidor não conseguiu mostrar o título.
    mfn: int | None
    #: Código do título; None quando o título não tem exemplar (o OPAC omite o link).
    title_id: str | None
    #: Total de exemplares (o "[N]" da página); 0 sem exemplar; None quando o PHL
    #: não conseguiu mostrar o título (ver `PhlClient.copy_statuses`).
    total: int | None
    #: Situações presentes, sem repetição, na ordem de `COPY_STATUS_BY_GIF`. Não
    #: diz quantos exemplares há em cada uma; ver `parse_copy_statuses`. É
    #: ["unknown"] quando o PHL não conseguiu mostrar o título.
    statuses: list[str]


class CopyStatusPage(NamedTuple):
    """Uma página do formato 'decorado', já convertida."""

    #: Total de títulos da busca ("n/total"), ou None se a página não mostra.
    total: int | None
    items: list[CopyStatusItem]
    #: True quando a página termina num erro fatal do WWWisis: os itens até ali
    #: valem, e o título seguinte (em ordem de MFN) é o que o servidor não mostrou.
    fatal_error: bool


class ReferenceItem(TypedDict):
    """Item do formato 'referencia' do OPAC."""

    mfn: int
    author: str
    title: str
    #: Referência bibliográfica (ABNT) já formatada pelo servidor.
    reference: str
    #: Número de exemplares aproximado (diverge da consulta de exemplares em poucos casos).
    approx_copies: int | None


def parse_records(page: str, base: str) -> list[Record]:
    """Página no formato de exportação 'phl' -> um registro por título.

    O formato imprime '<hr>001: valor<br>002: valor<br>...' por registro. Os nomes
    dos campos vêm de `FIELDS`; tags desconhecidas viram `field_<tag>`.

    Args:
        page: HTML devolvido pelo servidor.
        base: Endereço do site, usado para completar as URLs de capa e de links.
    """
    records: list[Record] = []
    for block in page.split("<hr>")[1:]:
        pairs = re.findall(r"(\d{3}):\s*(.*?)(?=<br>|$)", block.split("</td>")[0])
        if not pairs:
            continue
        record: Record = {}
        for tag, value in pairs:
            name = FIELDS.get(tag, "field_%s" % tag)
            if tag in LINK_FIELDS:
                url = _link_url(value, base)
                if url:
                    _store(record, name + "_url", url, repeatable=False)
            text = html.unescape(re.sub(r"<[^>]+>", "", value)).strip()
            if text:
                _store(record, name, text, repeatable=tag in REPEATABLE_FIELDS)
        cover = record.get("cover_image")
        if isinstance(cover, str):
            record["cover_image"] = base + cover
        fill_title_author(record)
        normalize_year(record)
        records.append(record)
    return records


def _store(record: Record, name: str, value: str, repeatable: bool) -> None:
    """Guarda o valor; campo repetível ou repetido no registro vira lista."""
    current = record.get(name)
    if isinstance(current, list):
        current.append(value)
    elif repeatable or current is not None:
        record[name] = ([] if current is None else [str(current)]) + [value]
    else:
        record[name] = value


def _link_url(value: str, base: str) -> str | None:
    """URL do <a href> de um campo de link, ou None se o link estiver quebrado.

    Há links quebrados no acervo ('href="...tccs/.pdf>' sem aspas de fechamento, ou
    arquivo sem nome). O cadastro grava 'http://', mas o servidor só responde em
    https: no mesmo host, usa o esquema do catálogo.
    """
    link = re.search(r'<a\s[^>]*href="([^"]+)"', value, re.I)
    url = html.unescape(link.group(1)).strip() if link else ""
    if not url or url.endswith("/.pdf"):
        return None
    parts = urllib.parse.urlsplit(urllib.parse.urljoin(base + "/", url))
    base_parts = urllib.parse.urlsplit(base)
    if parts.netloc == base_parts.netloc:
        parts = parts._replace(scheme=base_parts.scheme)
    return urllib.parse.quote(parts.geturl(), safe=":/?&=#%~+,;@")


def normalize_year(record: Record) -> None:
    """Preenche `year_number` com o primeiro ano plausível (int) ou None.

    O ano (064) é texto livre: só 83% tem 4 dígitos exatos; o resto são '[s.d.]',
    'jan.2014', '2.sem.2021', '2019/2020', '20110000', '[19..]'. Use `year_number`
    no lugar de int(record["year"]), que quebra em ~17% dos registros.
    """
    value = first_text(record.get("year")) or ""
    match = (re.search(r"(?<!\d)(1[5-9]\d\d|20\d\d)(?!\d)", value)
             or re.fullmatch(r"((?:1[5-9]|20)\d\d)0000", value))
    record["year_number"] = int(match.group(1)) if match else None


def fill_title_author(record: Record) -> None:
    """Preenche título e autor dos registros que não usam os campos 018/016.

    ~11% do acervo (fascículos NIV=s, artigos NIV=as/am) guarda o título em 030
    (série) ou 012 (título da parte) e o autor em 010 (autor da parte). Sem isso o
    título ficaria ausente em ~2200 registros. Mantém os campos originais e só
    preenche quando realmente ausentes.
    """
    if not record.get("title"):
        alternative = record.get("part_title") or record.get("series")
        if alternative:
            record["title"] = first_text(alternative)
    if not record.get("author"):
        alternative = record.get("part_author") or record.get("corporate_author")
        if alternative:
            record["author"] = alternative


def parse_copies(page: str, include_borrower: bool = False) -> list[CopyRow]:
    """Tela de situação de um título -> uma linha por exemplar.

    Cada exemplar vem numa tabela própria (marcada por FMX000152) e a situação é o
    nome do GIF. A tela mostra a matrícula de quem está com o livro; por ser dado
    pessoal, ela só é devolvida com `include_borrower=True`.
    """
    rows = []
    for block in page.split("FMX000152")[1:]:
        rows.extend(re.findall(r"<tr>(.*?)(?=<tr>|</table>)", block, re.S))
    copies: list[CopyRow] = []
    for row in rows:
        cells = [html.unescape(re.sub(r"<[^>]+>", "", cell)).strip()
                 for cell in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        gif = re.search(r"/img/(\d{3})\.gif", row)
        if not cells or not gif:
            continue
        cells += [""] * (8 - len(cells))
        copy: CopyRow = {
            "accession_number": cells[0], "note": cells[1], "label": cells[2],
            "status": COPY_STATUS_BY_GIF.get(gif.group(1), "unknown"),
            "due_date": cells[4], "loans": cells[6], "renewals": cells[7],
        }
        if include_borrower:
            copy["borrower"] = cells[5]
        copies.append(copy)
    return copies


_STATUS_ORDER = list(COPY_STATUS_BY_GIF.values())


def parse_copy_statuses(page: str) -> CopyStatusPage:
    """Página do formato 'decorado' -> total da busca, um item por título e se a
    página foi interrompida por um erro fatal do servidor.

    Cada título traz, ao lado do checkbox de seleção, um ícone por situação presente,
    o total de exemplares ("[N]") e o link da tela de exemplares, com o código do
    título. Título sem exemplar não tem nada disso e vem com `title_id` None.

    Os ícones misturam duas origens: 003 (emprestado) e 016 (reserva) vêm da
    circulação, os demais da situação cadastral do exemplar. Um exemplar emprestado
    continua aparecendo como 002 (disponível), então 002 junto de 003 não garante
    exemplar livre (ex.: título com um só exemplar, emprestado: 003 + 002, "[1]").

    Raises:
        LibraryError: Quando um título tem exemplares mas vem sem o código.
    """
    hits = re.search(r">\d+/(\d+)<", page)
    items: list[CopyStatusItem] = []
    for block in page.split('name="sel" value="MFN=')[1:]:
        mfn, _, rest = block.partition('"')
        cell = rest.split("</td>")[0]
        gifs = set(re.findall(r"/img/(\d{3})\.gif", cell))
        statuses = {COPY_STATUS_BY_GIF[gif] for gif in gifs if gif in COPY_STATUS_BY_GIF}
        total = re.search(r"\[(\d+)\]", cell)
        title_id = re.search(r"[?&]tit=(\d+)", cell)
        if (statuses or total) and not title_id:
            raise LibraryError("resposta do servidor em formato inesperado (título com exemplares sem código)")
        if not mfn.isdigit():
            raise LibraryError("resposta do servidor em formato inesperado (título sem MFN)")
        items.append({
            "mfn": int(mfn),
            "title_id": title_id.group(1) if title_id else None,
            "total": int(total.group(1)) if total else 0,
            "statuses": [status for status in _STATUS_ORDER if status in statuses],
        })
    fatal_error = page.rstrip().rsplit("\n", 1)[-1].startswith("WXIS|")
    return CopyStatusPage(int(hits.group(1)) if hits else None, items, fatal_error)


def parse_references(xml: str) -> tuple[int | None, list[ReferenceItem]]:
    """Página do formato 'referencia' (XML) -> (total em <hits> ou None, itens).

    Um registro sem <mfn> ou <ref> (resposta truncada ou corrompida) levanta erro em
    vez de ser pulado, o que desalinharia a paginação.

    Raises:
        LibraryError: Quando um registro vem sem <mfn> ou <ref>.
    """
    hits = re.search(r"<hits>(\d+)</hits>", xml)
    items: list[ReferenceItem] = []
    for raw in re.findall(r"<reg>(.*?)</reg>", xml, re.S):
        mfn = re.search(r"<mfn>\s*(\d+)", raw)
        ref = re.search(r"<ref>(.*?)</ref>", raw, re.S)
        if not (mfn and ref):
            raise LibraryError("resposta do servidor em formato inesperado (registro sem <mfn> ou <ref>)")

        def tag_text(tag: str, raw: str = raw) -> str:
            match = re.search(r"<%s>(.*?)</%s>" % (tag, tag), raw, re.S)
            return html.unescape(re.sub(r"<[^>]+>", "", match.group(1) if match else "")).strip()

        copies = re.search(r"<e>\s*(\d+)\s*Ex", raw)
        reference = re.sub(r"<e>.*?</e>|<[^>]+>", "", ref.group(1))
        items.append({
            "mfn": int(mfn.group(1)),
            "author": tag_text("a"),
            "title": tag_text("b").rstrip(": ").strip(),
            "reference": html.unescape(re.sub(r"\s+", " ", reference)).strip(),
            "approx_copies": int(copies.group(1)) if copies else None,
        })
    return (int(hits.group(1)) if hits else None), items
