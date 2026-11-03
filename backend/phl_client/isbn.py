"""ISBN: normalização, conversão 10/13 e as formas usadas na busca. Funções puras."""

from __future__ import annotations

import re


def isbn_digits(value: object) -> str:
    """Só os dígitos (e o X final) de um ISBN."""
    return re.sub(r"[^0-9Xx]", "", str(value or "")).upper()


def isbn10_to_13(digits: str) -> str:
    base = "978" + digits[:9]
    check = (10 - sum(int(c) * (3 if i % 2 else 1) for i, c in enumerate(base)) % 10) % 10
    return base + str(check)


def isbn13_to_10(digits: str) -> str | None:
    """ISBN-10 equivalente, ou None quando o prefixo não é 978."""
    if not digits.startswith("978"):
        return None
    core = digits[3:12]
    check = (11 - sum((10 - i) * int(c) for i, c in enumerate(core)) % 11) % 11
    return core + ("X" if check == 10 else str(check))


def hyphenations(digits: str) -> set[str]:
    """Todas as hifenizações plausíveis (grupo de 1 a 5 dígitos, editor de 1 a 7).

    O catálogo guarda o ISBN como foi digitado (metade com hífen, metade sem) e a
    busca só encontra a forma exata.
    """
    prefix = digits[:3] if len(digits) == 13 else ""
    body, check = digits[len(prefix):-1], digits[-1]
    forms = set()
    for group in range(1, 6):
        for publisher in range(1, 8):
            if len(body) - group - publisher < 1:
                continue
            parts = [body[:group], body[group:group + publisher], body[group + publisher:], check]
            forms.add("-".join(([prefix] if prefix else []) + parts))
    return forms


def isbn_search_forms(digits: str) -> tuple[set[str], set[str]]:
    """Formas para buscar e dígitos-alvo de um ISBN de 10 ou 13 dígitos.

    Args:
        digits: ISBN já normalizado por `isbn_digits`.

    Returns:
        As formas com e sem hífen, em 10 e 13 dígitos, e os dígitos aceitos no resultado.
    """
    digits13 = isbn10_to_13(digits) if len(digits) == 10 else digits
    digits10 = digits if len(digits) == 10 else isbn13_to_10(digits)
    targets = {digits13} | ({digits10} if digits10 else set())
    forms = set(targets)
    for form in targets:
        forms |= hyphenations(form)
    return forms, targets
