"""Link para a ficha de um livro no catálogo oficial da biblioteca (PHL)."""

from __future__ import annotations

import logging

from catalog.services import availability
from phl_client import LibraryError

logger = logging.getLogger(__name__)


def record_url(book_id: str) -> str:
    """Endereço da ficha do livro no OPAC, com uma sessão nova (1 requisição ao PHL).

    O OPAC não tem link fixo por título, então o endereço é gerado na hora em que
    a pessoa clica. Se o PHL falhar, devolve a página inicial do catálogo: o link
    continua levando ao catálogo em vez de quebrar.
    """
    phl = availability.live_library().phl
    try:
        return phl.record_page_url(book_id)
    except (LibraryError, ValueError) as error:
        logger.warning("ficha de %s no catálogo indisponível: %s", book_id, error)
        return phl.home_url
