"""Cliente de baixo nível do OPAC: busca crua, exemplares, referências e índices."""

from __future__ import annotations

import re
import time
from collections.abc import Iterable, Iterator
from typing import TypedDict, Unpack

from .fields import AUTHORITY_INDEXES, DOCUMENT_TYPES, LIBRARY_CODE, SEARCH_FIELD_TAGS, Record
from .isbn import isbn_digits, isbn_search_forms
from .parsers import CopyRow, ReferenceItem, parse_copies, parse_records, parse_references
from .query import clean_query, require_expression
from .text import first_text, normalize, text_list
from .transport import Transport

# Maior página aceita numa requisição: testada ao vivo com o acervo inteiro
# (~25 mil registros, ~8 s, sem duplicatas).
MAX_PAGE_SIZE = 25000
# Quantos anos entram num único OU de DTP= em `cataloged_between`.
YEARS_PER_QUERY = 200


class SearchFilters(TypedDict, total=False):
    """Filtros aceitos pelas buscas do OPAC."""

    #: Grupo de campos (chave de SEARCH_FIELD_TAGS) ou tags cruas ("62").
    field: str
    #: Tipo de documento (chave de DOCUMENT_TYPES) ou código do filtro tip=.
    document_type: str
    #: Código de idioma (chave de LANGUAGES).
    language: str
    #: Código de suporte (chave de MEDIA).
    medium: str


class PhlClient(Transport):
    """Cliente de baixo nível do OPAC, que devolve registros do PHL já com os campos
    nomeados. É o `library.phl` de uma `Library`; prefira a `Library` no dia a dia.

    O parâmetro `mode` segue o protocolo do OPAC: "and" (todas as palavras, com o
    texto limpo por `clean_query`) ou "exp" (expressão ISIS crua, com operadores).
    """

    # ---- busca
    def _search_params(self, expression: str, mode: str = "and", per_page: int = 50,
                       start: int = 1, output_format: str = "phl",
                       **filters: Unpack[SearchFilters]) -> dict[str, str | None]:
        params: dict[str, str | None] = {
            "IsisScript": self.script, "opc": output_format, "pft": output_format,
            "bool": mode, "exp": expression, "rpp": str(per_page), "from": str(start),
        }
        if "field" in filters:
            params["tag"] = SEARCH_FIELD_TAGS.get(filters["field"], filters["field"])
        if "document_type" in filters:
            params["tip"] = DOCUMENT_TYPES.get(filters["document_type"], filters["document_type"])
        if "language" in filters:
            params["idm"] = filters["language"]
        if "medium" in filters:
            params["spt"] = filters["medium"]
        return params

    @staticmethod
    def _prepare(expression: str | None, mode: str) -> str:
        return require_expression(None if expression is None else clean_query(expression, mode))

    def count(self, expression: str, mode: str = "and", **filters: Unpack[SearchFilters]) -> int:
        """Total de registros de uma expressão (lê o 'n/total' do formato decorado)."""
        expression = self._prepare(expression, mode)
        page = self.request(self._search_params(expression, mode, per_page=1,
                                                output_format="decorado", **filters))
        match = re.search(r">\d+/(\d+)<", page)
        return int(match.group(1)) if match else 0

    def search(self, expression: str, mode: str = "and", per_page: int = 50, start: int = 1,
               **filters: Unpack[SearchFilters]) -> list[Record]:
        """Uma página de resultados, já convertida em registros."""
        expression = self._prepare(expression, mode)
        page = self.request(self._search_params(expression, mode, per_page=per_page,
                                                start=start, **filters))
        return parse_records(page, self.base)

    def search_all(self, expression: str, mode: str = "and", page_size: int = 5000,
                   limit: int | None = None, **filters: Unpack[SearchFilters]) -> Iterator[Record]:
        """Itera sobre todos os resultados, paginando com `from`.

        Poucas requisições grandes são mais gentis com o CGI (um processo por
        requisição) que muitas pequenas; ver `MAX_PAGE_SIZE`.

        Args:
            page_size: Registros por requisição.
            limit: Máximo de registros; None conta o total no servidor antes.

        Raises:
            ValueError: Quando `page_size` é menor que 1.
        """
        if page_size < 1:
            raise ValueError("page_size deve ser >= 1 (recebi %r)" % (page_size,))
        total = limit if limit is not None else self.count(expression, mode, **filters)
        read = 0
        while read < total:
            batch = self.search(expression, mode, per_page=min(page_size, total - read),
                                start=read + 1, **filters)
            if not batch:
                break
            yield from batch
            read += len(batch)

    def by_mfns(self, mfns: Iterable[int | str], batch_size: int = 50) -> list[Record]:
        """Vários registros de uma vez: 'MFN=a + MFN=b + ...' (OU do ISIS)."""
        mfn_list, records = list(mfns), []
        for i in range(0, len(mfn_list), batch_size):
            batch = mfn_list[i:i + batch_size]
            records.extend(self.search(" + ".join("MFN=%s" % mfn for mfn in batch),
                                       mode="exp", per_page=len(batch)))
        return records

    def by_isbn(self, isbn: str) -> list[Record]:
        """Registros com esse ISBN, em qualquer formato de entrada.

        A busca simples só acha o ISBN escrito exatamente como foi cadastrado. Aqui o
        ISBN é normalizado, ganha as formas de 10 e 13 dígitos e todas as hifenizações
        plausíveis, tudo numa requisição (OU), e o resultado é conferido no cliente
        (dígitos iguais), sem falso positivo.

        Raises:
            ValueError: Quando o ISBN não tem 10 nem 13 dígitos.
        """
        digits = isbn_digits(isbn)
        if len(digits) not in (10, 13):
            raise ValueError("ISBN deve ter 10 ou 13 dígitos (recebi %d)" % len(digits))
        forms, targets = isbn_search_forms(digits)
        expression = " + ".join('"%s"' % form for form in sorted(forms))
        return [record for record in self.search(expression, mode="exp", per_page=50)
                if any(isbn_digits(value) in targets for value in text_list(record.get("isbn")))]

    def by_accession_number(self, accession_number: int | str) -> Record | None:
        """Título a que pertence um exemplar, pelo número de tombo (prefixo TBO=).

        Raises:
            ValueError: Quando o tombo não é numérico.
        """
        number = str(accession_number).strip()
        if not number.isdigit():
            raise ValueError("tombo deve ser numérico (recebi %r)" % (accession_number,))
        records = self.search("TBO=%s" % number, mode="exp", per_page=1)
        return records[0] if records else None

    # ---- feeds e datas
    def monthly_acquisitions(self) -> list[Record]:
        """Feed "Aquisições do Mês" do menu do OPAC.

        opc=sdi ignora o formato pedido e devolve sempre o HTML decorado; dele saem os
        MFN, e os registros são buscados no formato phl.
        """
        page = self.request({"IsisScript": self.script, "cipar": self.cipar, "opc": "sdi",
                             "pft": "decorado", "lang": "por"})
        return self.by_mfns(dict.fromkeys(re.findall(r'value="MFN=(\d+)"', page)))

    def cataloged_between(self, start: str, end: str | None = None,
                          **filters: Unpack[SearchFilters]) -> list[Record]:
        """Registros com data de entrada no catálogo entre duas datas (aaaammdd, inclusive).

        O campo 065 (`standardized_date`) não é a data de publicação (um livro de 1994
        aparece com 20080709): é a data em que o registro foi criado ou salvo. O índice
        DTP= só guarda o ano dessa data, então a busca é por ano e o dia é filtrado
        aqui. O 065 mistura dois usos: em 92% dos registros é a data de entrada
        completa; em ~6% é o ano de publicação no formato AAAA0000 (ex.: 20210000).
        Datas terminadas em "00" não são data de entrada e ficam de fora. Não é igual a
        `monthly_acquisitions()`: lá o servidor usa outro critério (provavelmente a
        aquisição dos exemplares).
        """
        start = str(start).replace("-", "")
        end = str(end).replace("-", "") if end else time.strftime("%Y%m%d")
        years = list(range(int(start[:4]), int(end[:4]) + 1))
        records: list[Record] = []
        for i in range(0, len(years), YEARS_PER_QUERY):
            expression = " + ".join("DTP=%d" % year for year in years[i:i + YEARS_PER_QUERY])
            records.extend(self.search_all(expression, mode="exp", **filters))

        def entry_date(record: Record) -> str:
            return first_text(record.get("standardized_date")) or ""

        return sorted((record for record in records
                       if not entry_date(record).endswith("00") and start <= entry_date(record) <= end),
                      key=entry_date)

    # ---- exemplares e referências
    def copies(self, title_id: str, library: str = LIBRARY_CODE,
               include_borrower: bool = False) -> list[CopyRow]:
        """Situação de cada exemplar (tombo, etiqueta, situação, devolução, empréstimos).

        A tela do OPAC mostra a matrícula de quem está com o livro; por ser dado
        pessoal, o campo `borrower` só vem com `include_borrower=True`.
        """
        return parse_copies(self.request({"IsisScript": self.script, "opc": "status_tit",
                                          "tit": title_id, "acv": library}), include_borrower)

    def references(self, expression: str = "$", mode: str = "exp", page_size: int = 5000,
                   limit: int | None = None, **filters: Unpack[SearchFilters]) -> Iterator[ReferenceItem]:
        """Itera referências bibliográficas já formatadas pelo servidor.

        É o formato mais leve do OPAC (opc=referencia, XML): ~4000 registros em ~1,6 s.
        Traz o total em <hits>, pagina por `from` e renderiza até os registros-esqueleto
        (sem campo 001). O número de exemplares é aproximado (divergiu da consulta de
        exemplares em 3 de 20264 títulos) e não traz o `title_id`, só o MFN.
        """
        expression = self._prepare(expression, mode)
        start, total = 1, None
        while total is None or start <= total:
            if limit is not None and start > limit:
                return
            requested = page_size if limit is None else min(page_size, limit - start + 1)
            hits, items = parse_references(self.request(self._search_params(
                expression, mode, per_page=requested, start=start, output_format="referencia",
                **filters)))
            if total is None:
                total = hits or 0
            if not items:
                return
            yield from items
            start += len(items)

    def abnt_reference(self, title_id: str) -> str | None:
        """Referência bibliográfica pronta ('POLYA, G. A arte de resolver problemas: ...
        Rio de Janeiro: Interciência, 1994. 179 p.'), ou None se o título não existe."""
        item = next(iter(self.references("TIT=%s" % title_id, limit=1)), None)
        return (item["reference"] or None) if item else None

    # ---- índices de autoridade
    def browse_index(self, index: str, prefix: str) -> list[str]:
        """Entradas de um índice de autoridade (assuntos, autores, títulos...), 10 por vez,
        a partir de `prefix`."""
        page = self.request({"IsisScript": "%s/%s" % (self.script.split("/")[0],
                                                       AUTHORITY_INDEXES.get(index, index)),
                             "exp": prefix})
        return [line.strip() for line in re.sub(r"<[^>]+>", "", page).splitlines() if line.strip()]

    def suggest(self, term: str, index: str = "all", attempts: int = 6) -> list[str]:
        """"Você quis dizer?" sobre um índice de autoridade.

        O índice é um cursor de B-tree: um erro depois do ponto certo ('chiavenatto',
        que ordena depois de 'chiavenato') cai depois da entrada correta e não a
        encontra. Por isso o termo é encurtado até achar entradas que comecem com o
        prefixo (sem acento nem caixa).

        Returns:
            As entradas parecidas, ou [] se nada parecido existe.

        Raises:
            ValueError: Quando o termo é vazio.
        """
        term = str(term).strip()
        if not term:
            raise ValueError("termo vazio")
        for size in range(len(term), max(1, len(term) // 2) - 1, -1)[:attempts]:
            prefix = term[:size]
            found = [entry for entry in self.browse_index(index, prefix)
                     if normalize(entry).startswith(normalize(prefix))]
            if found:
                return found
        return []
