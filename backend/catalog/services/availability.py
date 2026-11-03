"""Disponibilidade ao vivo, consultada quando alguém abre a página de um livro."""

from __future__ import annotations

import logging
import threading
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from catalog.models import Book
from catalog.services.sync import refresh_copies
from phl_client import Library, LibraryError

logger = logging.getLogger(__name__)

_library: Library | None = None
_library_lock = threading.Lock()


def live_library() -> Library:
    """Cliente do PHL compartilhado entre requisições, criado na primeira vez.

    Reaproveitar a sessão evita uma requisição extra por consulta; sem pausa e com
    tempo limite curto, porque há uma pessoa esperando a página.
    """
    global _library
    with _library_lock:
        if _library is None:
            _library = Library(settings.PHL_CATALOG_URL, pause=0, cache=0,
                               timeout=settings.PHL_LIVE_TIMEOUT, connect=False)
        return _library


def is_stale(book: Book) -> bool:
    """True quando os exemplares nunca foram verificados ou passaram da validade."""
    max_age = timedelta(minutes=settings.COPIES_LIVE_MAX_AGE_MINUTES)
    return book.copies_checked_at is None or timezone.now() - book.copies_checked_at > max_age


def refresh_if_stale(book: Book) -> bool:
    """Atualiza os exemplares do livro no PHL se estiverem velhos.

    Se o PHL falhar, mantém o dado guardado: a página não deve quebrar porque o
    catálogo do campus está lento ou fora do ar.

    Returns:
        True quando o livro foi atualizado (recarregue-o do banco).
    """
    if not is_stale(book):
        return False
    try:
        refresh_copies(live_library(), book.id)
    except LibraryError as error:
        logger.warning("disponibilidade ao vivo de %s indisponível: %s", book.id, error)
        return False
    return True
