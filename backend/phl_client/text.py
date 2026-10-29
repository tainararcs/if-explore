"""Utilitários de texto, números e datas. Não usam a rede."""

from __future__ import annotations

import datetime as dt
import re
import unicodedata

from .fields import RecordValue


def normalize(text: object) -> str:
    """Minúsculas e sem acento, para comparar textos."""
    return unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode().lower()


def first_text(value: RecordValue) -> str | None:
    """Primeiro texto de um valor do registro; listas devolvem o primeiro item."""
    if isinstance(value, list):
        return value[0] if value else None
    return value if isinstance(value, str) else None


def clean_text(value: RecordValue) -> str | None:
    """Texto com espaços colapsados ('São  Paulo'); lista vira 'a / b'; vazio vira None."""
    if value is None:
        return None
    if isinstance(value, list):
        value = " / ".join(item for item in value if item)
    return " ".join(str(value).split()) or None


def text_list(value: RecordValue) -> list[str]:
    """Sempre uma lista de textos com espaços colapsados, sem itens vazios."""
    items = [] if value is None else value if isinstance(value, list) else [value]
    return [" ".join(str(item).split()) for item in items if str(item).strip()]


def to_plain(value: object) -> object:
    """Lista vira texto 'a; b' (links viram a URL), para CSV, tabela e ficha."""
    if isinstance(value, list):
        return "; ".join(
            str(item["url"]) if isinstance(item, dict) else str(item) for item in value
        )
    return value


def first_int(value: RecordValue) -> int | None:
    """Primeiro número inteiro encontrado no texto ('505 p.' -> 505)."""
    match = re.search(r"\d+", str(value if value is not None else ""))
    return int(match.group()) if match else None


def parse_date(value: object, name: str) -> dt.date:
    """Converte date, datetime, 'AAAA-MM-DD' ou 'DD/MM/AAAA' em date.

    Args:
        value: Data informada pelo chamador.
        name: Nome do parâmetro, usado na mensagem de erro.

    Raises:
        ValueError: Quando o formato não é reconhecido.
    """
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    for date_format in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return dt.datetime.strptime(str(value).strip(), date_format).date()
        except ValueError:
            pass
    raise ValueError("%s inválida: %r (use 'AAAA-MM-DD', 'DD/MM/AAAA' ou date)" % (name, value))
