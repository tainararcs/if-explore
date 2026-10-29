"""Ponto de entrada do cliente: a fachada `Library`."""

from __future__ import annotations

import datetime as dt
import re

from .client import MAX_PAGE_SIZE, PhlClient, SearchFilters
from .fields import DOCUMENT_TYPES, KNOWLEDGE_AREAS, LANGUAGES, LIBRARY_CODE, Record
from .isbn import isbn_digits
from .models import Book, SearchResult
from .query import clean_query
from .text import normalize, parse_date

YearRange = tuple[int, int]
# Cada critério de busca vira (expressão, modo, filtros) e resulta num conjunto de títulos.
Query = tuple[str, str, SearchFilters]


class Library:
    """Consulta o acervo de uma biblioteca PHL Elysio.

    Regras: um livro devolve `Book` ou None; uma busca devolve `SearchResult` (uma
    lista, vazia se nada foi achado); argumento inválido levanta ValueError; servidor
    ou URL com problema levanta `LibraryError`. As respostas ficam em cache e há uma
    pausa entre chamadas, para ser gentil com o servidor do campus.

    Attributes:
        phl: O cliente de baixo nível, para o que esta API não cobre (busca crua,
            índices, prefixos ISIS, referências em lote).
    """

    def __init__(self, url: str, *, pause: float = 0.5, timeout: int = 60, cache: int = 120,
                 connect: bool = True):
        """
        Args:
            url: Site do catálogo (`https://biblioteca.exemplo.br`) ou a URL completa que
                o navegador mostra (`.../wxis.exe?IsisScript=phl82.xis&...`).
            pause: Segundos de espera entre requisições.
            timeout: Segundos até desistir de uma requisição.
            cache: Segundos que respostas idênticas ficam guardadas (0 desliga).
            connect: False adia a abertura da sessão até a primeira consulta.
        """
        self.phl = PhlClient(url, pause=pause, timeout=timeout, cache_ttl=cache)
        if connect:
            self.phl.open_session()

    def __repr__(self) -> str:
        return "Library(%r)" % self.phl.base

    def book(self, book_id: str | None = None, *, isbn: str | None = None,
             accession_number: int | str | None = None) -> Book | None:
        """Um livro pelo código do título, pelo ISBN (com ou sem hífen, 10 ou 13
        dígitos) ou pelo tombo de um exemplar. Consulta o servidor.

        Returns:
            O livro, ou None se não existir.

        Raises:
            ValueError: Quando não é informado exatamente um dos três identificadores.
        """
        if sum(value is not None for value in (book_id, isbn, accession_number)) != 1:
            raise ValueError("informe exatamente um: book_id=..., isbn=... ou accession_number=...")
        record: Record | None = None
        if book_id is not None:
            if not re.fullmatch(r"[A-Za-z0-9]+", str(book_id).strip()):
                raise ValueError("book_id inválido: %r (só letras e dígitos)" % (book_id,))
            record = next(iter(self.phl.search("TIT=%s" % str(book_id).strip(), mode="exp", per_page=1)), None)
        elif isbn is not None:
            record = next(iter(self.phl.by_isbn(isbn)), None)
        elif accession_number is not None:
            record = self.phl.by_accession_number(accession_number)
        # O acervo tem um registro-esqueleto sem o campo 002; sem este teste ele viraria
        # KeyError('title_id') em vez de "não encontrado".
        return Book.from_record(record, self) if record and record.get("title_id") else None

    def search(self, text: str | None = None, *, title: str | None = None, author: str | None = None,
               subject: str | None = None, publisher: str | None = None, isbn: str | None = None,
               year: int | YearRange | None = None, course: int | str | None = None,
               area: int | str | None = None, classification: str | None = None,
               document_type: str | None = None, language: int | str | None = None,
               expression: str | None = None, limit: int | None = 50) -> SearchResult:
        """Busca por critérios combinados: todos precisam valer. Consulta o servidor.

        Critérios de texto (todas as palavras, sem diferença de acento ou caixa, com a
        pontuação ignorada): `text` (qualquer campo, como a caixa de busca do site),
        `title`, `author`, `subject` e `publisher`.

        Args:
            isbn: Com ou sem hífen, ISBN-10 ou 13.
            year: Ano de publicação, 2021 ou (2019, 2024). O servidor não busca por ele:
                o filtro é feito aqui, e usá-lo sozinho baixa o acervo inteiro (~10 s).
            course: Código do curso na bibliografia (ex.: 24).
            area: Área do CNPq, de 1 a 9 ou pelo nome ("engenharias", "saude").
            classification: CDD por prefixo: "005" traz 005, 005.1, 005.133...
            document_type: Chave de DOCUMENT_TYPES ("book", "periodical", "thesis"...).
            language: Código de 1 a 9 ou o nome ("portugues", "ingles").
            expression: Expressão ISIS crua para OU/E/EXCETO: "PYTHON + JAVA",
                "MATEMATICA ^ ALGEBRA".
            limit: Máximo de livros (None traz todos); `total` e `truncated` dizem se
                algo ficou de fora.

        A ordem é a do catálogo (o servidor não ordena por relevância).

        Raises:
            ValueError: Quando um argumento é inválido ou nenhum critério é informado.
        """
        if limit is not None and (isinstance(limit, bool) or not isinstance(limit, int) or limit < 1):
            raise ValueError("limit deve ser um inteiro >= 1 ou None: %r" % (limit,))
        year_range = self._year_range(year) if year is not None else None
        if isbn is not None and len(isbn_digits(isbn)) not in (10, 13):
            raise ValueError("ISBN deve ter 10 ou 13 dígitos: %r" % (isbn,))
        filters: SearchFilters = {}
        if document_type is not None:
            filters["document_type"] = self._document_type(document_type)
        if language is not None:
            filters["language"] = self._choose(language, LANGUAGES, "idioma")
        queries: list[Query] = []
        for label, value, field in (("text", text, None), ("title", title, "title"),
                                    ("author", author, "author"), ("subject", subject, "subject"),
                                    ("publisher", publisher, "publisher")):
            if value is None:
                continue
            if isinstance(value, bool) or not isinstance(value, (str, int)):
                raise ValueError("%s deve ser texto (recebi %s): %r" % (label, type(value).__name__, value))
            if not clean_query(str(value), "and"):
                raise ValueError("%s sem conteúdo pesquisável: %r" % (label, value))
            query_filters: SearchFilters = filters.copy()
            if field:
                query_filters["field"] = field
            queries.append((str(value), "and", query_filters))
        if expression is not None:
            if not isinstance(expression, str) or not expression.strip():
                raise ValueError("expression deve ser um texto não vazio: %r" % (expression,))
            queries.append((expression, "exp", filters.copy()))
        if course is not None:
            if isinstance(course, bool) or not re.fullmatch(r"[0-9A-Za-z]+", str(course).strip()):
                raise ValueError("course inválido: %r (informe o código, ex.: 24)" % (course,))
            queries.append(("%sCUR=%s" % (LIBRARY_CODE, str(course).strip()), "exp", filters.copy()))
        if area is not None:
            area_code = self._choose(area, KNOWLEDGE_AREAS, "área")
            queries.append(("%sATE=%s" % (LIBRARY_CODE, area_code), "exp", filters.copy()))
        if classification is not None:
            if not re.fullmatch(r"[0-9A-Za-z.\-/ ]+", str(classification).strip()):
                raise ValueError("classification inválida: %r (ex.: '005.13')" % (classification,))
            queries.append(("CLA=%s$" % str(classification).strip(), "exp", filters.copy()))
        if not queries and isbn is None:
            # `year=` sem outro critério baixa o acervo todo (~10 s) e filtra aqui, porque o
            # servidor não busca por ano de publicação.
            if not (year_range or filters):
                raise ValueError("informe ao menos um critério (title=, author=, year=, ...); "
                                 "para o acervo inteiro: search(expression='$', limit=None)")
            queries.append(("$", "exp", filters.copy()))

        if len(queries) == 1 and isbn is None and not year_range:   # caminho rápido
            query_expression, mode, query_filters = queries[0]
            count = self.phl.count(query_expression, mode, **query_filters)
            records = list(self.phl.search_all(query_expression, mode, limit=min(limit or count, count),
                                               **query_filters)) if count else []
            books = [Book.from_record(record, self) for record in records if record.get("title_id")]
            # não conta o registro sem id, que é descartado
            truncated = limit is not None and count > limit
            return SearchResult(books, total=count if truncated else len(books), truncated=truncated)

        # Vários critérios: interseção dos títulos de cada um, começando pelo menor conjunto.
        # Baixa o conjunto completo de cada critério (~8 s se casar com o acervo todo); o
        # teto prático são dois critérios largos. Melhoria possível: filtrar o menor
        # conjunto por TIT= em lotes.
        candidates: dict[str, Record] | None = None
        if isbn is not None:
            candidates = {str(record["title_id"]): record for record in self.phl.by_isbn(isbn)
                          if record.get("title_id")}
        # key=contagem: sem ela, critérios de mesma contagem fariam o sorted comparar os
        # dicts de filtros (TypeError).
        counts = sorted(((self.phl.count(e, m, **f), e, m, f) for e, m, f in queries), key=lambda item: item[0])
        if counts and counts[0][0] == 0:
            return SearchResult()
        for count, query_expression, mode, query_filters in counts:
            if candidates is not None and not candidates:
                break
            found = {str(record["title_id"]): record
                     for record in self.phl.search_all(query_expression, mode, limit=count,
                                                       page_size=MAX_PAGE_SIZE, **query_filters)
                     if record.get("title_id")}
            candidates = found if candidates is None else {
                key: value for key, value in candidates.items() if key in found}
        books = [Book.from_record(record, self) for record in (candidates or {}).values()]
        if year_range:
            books = [book for book in books
                     if book.year is not None and year_range[0] <= book.year <= year_range[1]]
        return SearchResult(books[:limit], total=len(books), truncated=limit is not None and len(books) > limit)

    def new_arrivals(self, since: str | dt.date | None = None,
                     until: str | dt.date | None = None) -> SearchResult:
        """Novidades do acervo, do mais novo ao mais antigo. Consulta o servidor.

        Sem argumentos, é o feed "Aquisições do Mês" do próprio OPAC. Com `since` (e
        `until`, que por padrão é hoje), são os registros com data de entrada no
        período; registros sem data de entrada completa ficam de fora. As datas
        aceitam 'AAAA-MM-DD', 'DD/MM/AAAA' ou date.

        Raises:
            ValueError: Datas inválidas, `until` sem `since` ou `since` depois de `until`.
        """
        if since is None:
            if until is not None:
                raise ValueError("com 'until' informe também 'since'")
            records = self.phl.monthly_acquisitions()
        else:
            start = parse_date(since, "since")
            end = parse_date(until, "until") if until is not None else dt.date.today()
            if start > end:
                raise ValueError("'since' (%s) é depois de 'until' (%s)" % (start, end))
            records = self.phl.cataloged_between(start.strftime("%Y%m%d"), end.strftime("%Y%m%d"))
        books = [Book.from_record(record, self) for record in records if record.get("title_id")]
        if since is not None:
            # ~40 registros têm data impossível no catálogo ('20073110', '20111131',
            # '201000609'): passam no filtro do servidor (comparação de texto) mas não
            # viram data. Sem isto entrariam no resultado com cataloged_at=None.
            books = [book for book in books if book.cataloged_at is not None]
        books.sort(key=lambda book: book.cataloged_at or dt.date.min, reverse=True)
        return SearchResult(books)

    def suggest(self, term: str) -> list[str]:
        """"Você quis dizer?": entradas do índice parecidas com o termo. Cobre erro no
        fim da palavra, não no meio de uma frase. Consulta o servidor."""
        return self.phl.suggest(term)

    # ---- validação dos argumentos de search()
    @staticmethod
    def _year_range(year: int | YearRange) -> YearRange:
        if isinstance(year, bool):
            raise ValueError("year inválido: %r" % (year,))
        if isinstance(year, int):
            first, last = year, year
        elif (isinstance(year, (tuple, list)) and len(year) == 2
              and all(isinstance(item, int) and not isinstance(item, bool) for item in year)):
            first, last = min(year), max(year)
        else:
            raise ValueError("year deve ser um int (2021) ou um intervalo (2019, 2024): %r" % (year,))
        if not 1000 <= first <= last <= 2100:
            raise ValueError("year fora do intervalo plausível (1000-2100): %r" % (year,))
        return first, last

    @staticmethod
    def _choose(value: int | str, options: dict[str, str], name: str) -> str:
        """Código (chave de `options`) a partir do próprio código ou do nome, sem
        acento; um trecho do nome vale quando é único."""
        wanted = normalize(str(value).strip())
        if wanted in options:
            return wanted
        found = ([code for code, label in options.items() if normalize(label) == wanted]
                 or [code for code, label in options.items() if wanted and wanted in normalize(label)])
        if len(found) == 1:
            return found[0]
        raise ValueError("%s %r %s. Opções: %s" % (name, value, "ambíguo" if found else "desconhecido",
                                                   ", ".join(sorted(options.values()))))

    @staticmethod
    def _document_type(value: str) -> str:
        # "e-book", "personal computer" e "personal_computer" valem igual: ignora hífen, espaço e _
        wanted = re.sub(r"[-_ ]", "", normalize(str(value).strip()))
        for key in DOCUMENT_TYPES:
            if re.sub(r"[-_ ]", "", key) == wanted:
                return key
        raise ValueError("document_type %r desconhecido. Opções: %s" % (value, ", ".join(sorted(DOCUMENT_TYPES))))
