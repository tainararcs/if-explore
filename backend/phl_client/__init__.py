"""Cliente do catálogo PHL Elysio da biblioteca do campus.

O PHL não tem API: este pacote conversa com a interface HTTP do próprio OPAC e
entrega objetos Python com tipos previsíveis, usando só a biblioteca padrão.

    from phl_client import Library

    library = Library("https://biblioteca.barbacena.ifsudestemg.edu.br")

    for book in library.search(title="python", year=(2019, 2024)):
        print(book)                  # Django de A a Z — SILVA, Tiago (2021)

    book = library.book(isbn="978-65-86110-68-5")
    print(book.summary())            # tudo sobre o livro
    book.is_available, book.loans    # consultam o servidor na 1ª vez

Organização (cada módulo só depende dos anteriores): `errors`, `fields` (tabelas do
PHL), `text`, `isbn` e `query` (funções puras), `parsers` (páginas -> dados, sem
rede), `transport` (sessão, HTTP, cache), `client` (buscas de baixo nível),
`models` (Copy, Book, SearchResult) e `library` (a fachada).

A matrícula de quem está com um livro não é exposta pela API pública.
"""

from .client import PhlClient
from .errors import LibraryConnectionError, LibraryError
from .library import Library
from .models import Book, BookLink, Copy, SearchResult

__all__ = [
    "Book", "BookLink", "Copy", "Library", "LibraryConnectionError", "LibraryError",
    "PhlClient", "SearchResult",
]
