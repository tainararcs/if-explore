"""URL do catálogo e preparo das expressões de busca. Funções puras."""

from __future__ import annotations

import re
import unicodedata
import urllib.parse
from typing import TypedDict

MAX_EXPRESSION_LENGTH = 4000


class CatalogUrl(TypedDict):
    """Partes da URL de um catálogo PHL."""

    base: str
    cgi: str
    #: Diretório dos scripts (ex.: "phl82"); None quando precisa ser descoberto.
    script_dir: str | None
    cipar: str | None
    lang: str


def parse_catalog_url(url: str) -> CatalogUrl:
    """Decompõe a URL de um catálogo PHL.

    Aceita a URL completa que o navegador mostra
    (`https://x.br/cgi-bin/wxis.exe?IsisScript=phl82.xis&cipar=phl82.cip&lang=por`)
    ou só o endereço do site (`x.br`, `https://x.br/`); nesse caso a versão dos
    scripts é descoberta ao abrir a sessão.

    Raises:
        ValueError: Quando a URL é vazia ou não é http(s).
    """
    text = str(url or "").strip()
    if not text:
        raise ValueError("URL vazia")
    if "://" not in text:
        text = "https://" + text
    parts = urllib.parse.urlsplit(text)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise ValueError("URL inválida: %r (use http(s)://endereco-do-catalogo)" % url)
    base = "%s://%s" % (parts.scheme, parts.netloc)
    path = parts.path if "wxis" in parts.path.lower() else "/cgi-bin/wxis.exe"
    query = urllib.parse.parse_qs(parts.query)
    script = (query.get("IsisScript") or [""])[0]
    match = re.match(r"[A-Za-z0-9_]+", script)
    script_dir = match.group() if match else None
    cipar = (query.get("cipar") or [""])[0] or (script_dir + ".cip" if script_dir else None)
    return {"base": base, "cgi": base + path, "script_dir": script_dir, "cipar": cipar,
            "lang": (query.get("lang") or ["por"])[0]}


def clean_query(expression: str, mode: str) -> str:
    """Prepara o texto digitado para o ISIS.

    Pontuação colada em palavra zera a busca: 'Fowler, Martin' (como vem numa
    referência ABNT), 'fowler.' ou 'fowler;' dão 0 resultados, enquanto 'Martin
    Fowler' acha 4. Fora do modo 'exp' (onde o usuário escreve operadores de
    propósito), portanto:

    * aplica NFKC: acento decomposto (macOS, PDF) e caracteres largos viram os normais;
    * troca por espaço símbolos e pontuação não ASCII (aspas curvas, travessão, emoji)
      e caracteres de controle, que o servidor (só latin-1) trocaria por '?';
    * tira a pontuação das bordas das palavras; vírgula, ponto e vírgula e dois-pontos
      viram espaço; 'agro*' vira 'agro$' (truncamento do ISIS);
    * descarta palavras feitas só de '$'/'*', que sozinhas casariam o acervo inteiro.

    A pontuação interna ('ASP.NET', 'C#', "D'Imperio") é preservada. O '+' não é
    tocado: é o operador OU e não há como escapá-lo. No modo 'exp' só normaliza para NFC.
    """
    expression = unicodedata.normalize("NFC" if mode == "exp" else "NFKC", str(expression))
    if mode == "exp":
        return expression
    expression = "".join(
        " " if ord(c) < 32 or ord(c) == 127 or (not c.isascii() and not c.isalnum()) else c
        for c in expression
    )
    expression = re.sub(r"[,;:!?\[\]/()\\]", " ", expression)
    words = []
    for word in expression.split():
        word = word.strip(",.;:!?[]/'-\"")
        if word.endswith("*"):
            word = word.rstrip("*") + "$"
        if word.strip("$"):
            words.append(word)
    return " ".join(words)


def require_expression(expression: str | None) -> str:
    """Barra expressões vazias e longas demais antes de consultar o servidor.

    O ISIS trata exp="" como "sem filtro" (casa tudo) e devolve registros
    arbitrários sem avisar; isso já causou um bug real (buscar o livro de id ""
    devolvia um livro ao acaso). Consultas enormes recebem HTTP 414.

    Raises:
        ValueError: Quando a expressão é vazia ou passa do limite.
    """
    if expression is None or not str(expression).strip():
        raise ValueError("expressão de busca vazia: o ISIS trata '' como 'sem filtro' e "
                         "devolve registros arbitrários em vez de nada. Use '$' (com "
                         "mode=\"exp\") se a intenção é mesmo buscar tudo.")
    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise ValueError("consulta longa demais (%d caracteres; máximo %d)"
                         % (len(expression), MAX_EXPRESSION_LENGTH))
    return expression
