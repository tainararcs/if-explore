"""Conversão das páginas do OPAC em dados. Não usam a rede e podem ser testados
com páginas de exemplo."""

from __future__ import annotations

import html
import re
import urllib.parse
from typing import TypedDict

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
