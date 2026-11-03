"""Exceções do cliente PHL."""


class LibraryError(RuntimeError):
    """Problema com o catálogo: URL que não é PHL, resposta de erro do servidor etc."""


class LibraryConnectionError(LibraryError):
    """Servidor inacessível, sem resposta ou com HTTP de erro.

    É subclasse de `LibraryError`: `except LibraryError` captura as duas.
    """
