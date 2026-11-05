"""Disponibilidade ao vivo, consultada quando alguém abre a página de um livro.

É a única fonte da contagem exata de exemplares livres e dos empréstimos: a
sincronização só lê a situação resumida, em lote.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

from catalog.models import Book
from catalog.services import copy_status
from phl_client import Copy, Library, LibraryError
from phl_client.fields import COPY_STATUS_BY_GIF

logger = logging.getLogger(__name__)

_library: Library | None = None
_library_lock = threading.Lock()


@dataclass(frozen=True)
class CopiesSummary:
    total: int
    available: int
    loans: int


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


def refresh_copies(library: Library, book_id: str, now: datetime | None = None) -> CopiesSummary:
    """Consulta os exemplares de um título no PHL (1 requisição) e grava no livro
    o total, as situações, a contagem de livres e os empréstimos.

    Raises:
        LibraryError: O PHL falhou (inclui `LibraryConnectionError`).
    """
    copies = [Copy.from_row(row) for row in library.phl.copies(book_id)]
    statuses = [copy.status for copy in copies]
    summary = CopiesSummary(len(copies), sum(copy.is_available for copy in copies),
                            sum(copy.loans for copy in copies))
    Book.objects.filter(id=book_id).update(
        copies_total=summary.total, copies_available=summary.available, loans_total=summary.loans,
        copy_statuses=[status for status in COPY_STATUS_BY_GIF.values() if status in statuses],
        copy_status=copy_status.from_copies(statuses), copies_checked_at=now or timezone.now())
    return summary


def is_stale(book: Book) -> bool:
    """True quando os exemplares nunca foram consultados ao vivo ou passaram da validade."""
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
