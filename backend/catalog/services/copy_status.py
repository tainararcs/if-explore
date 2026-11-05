"""Situação de um título para o visitante (`CopyStatus`), a partir das situações
dos exemplares.

Funções puras: não consultam o banco e são testadas sem ele.
"""

from __future__ import annotations

from collections.abc import Collection

from catalog.models import CopyStatus


def _without_free_copy(statuses: Collection[str]) -> CopyStatus:
    """Situação quando já se sabe que nenhum exemplar está livre."""
    if "in_library_use" in statuses:
        return CopyStatus.IN_LIBRARY_USE
    if "on_loan" in statuses or "reserved" in statuses:
        return CopyStatus.ON_LOAN
    return CopyStatus.UNAVAILABLE


def from_batch(statuses: Collection[str], total: int | None) -> CopyStatus:
    """Situação a partir do resumo do formato decorado (situações presentes e total).

    Nesse resumo, um exemplar emprestado ou reservado continua aparecendo como
    disponível. Por isso "disponível" só vale quando não há empréstimo nem reserva;
    com eles, um título de um só exemplar certamente não tem exemplar livre, e os
    demais ficam incertos até a consulta ao vivo.

    Args:
        statuses: Situações presentes (`CopyStatusItem.statuses`); "unknown" quando
            o PHL não conseguiu mostrar o título.
        total: Total de exemplares do título; None quando desconhecido.
    """
    if total is None or "unknown" in statuses:
        return CopyStatus.UNCERTAIN
    if total == 0 and not statuses:
        return CopyStatus.NO_COPIES
    circulating = "on_loan" in statuses or "reserved" in statuses
    if "available" in statuses:
        if not circulating:
            return CopyStatus.AVAILABLE
        if total > 1:
            return CopyStatus.UNCERTAIN
    return _without_free_copy(statuses)


def from_copies(statuses: Collection[str]) -> CopyStatus:
    """Situação a partir da tela de exemplares, com a situação exata de cada um.

    Args:
        statuses: Situação de cada exemplar (`Copy.status`), uma por exemplar.
    """
    if not statuses:
        return CopyStatus.NO_COPIES
    if "available" in statuses:
        return CopyStatus.AVAILABLE
    return _without_free_copy(statuses)
