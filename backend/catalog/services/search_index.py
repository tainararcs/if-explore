"""Índice de busca textual (FTS5) dos livros ativos.

A tabela `catalog_book_fts` é criada pela migração 0002. O índice é reconstruído
por inteiro a cada sincronização do catálogo: ~20 mil linhas levam poucos segundos
e evitam ter de manter gatilhos de atualização.
"""

from __future__ import annotations

import re
import unicodedata

from django.db import connection

from catalog.models import Author, Book, BookAuthor, Subject

FTS_TABLE = "catalog_book_fts"
# Pesos do bm25 por coluna: book_id (não indexada), título, autores, assuntos,
# sinopse, extra (editora, série, ISBN, CDD, créditos, curso do TCC).
BM25_WEIGHTS = (0.0, 10.0, 6.0, 3.0, 1.0, 1.0)


def rebuild() -> int:
    """Reconstrói o índice com os livros ativos.

    Deve rodar na mesma transação que alterou os livros, para que a API nunca veja
    um índice fora de sincronia.

    Returns:
        Quantos livros foram indexados.
    """
    book, book_author, author, subject = (Book._meta.db_table, BookAuthor._meta.db_table,
                                          Author._meta.db_table, Subject._meta.db_table)
    book_subject = Book.subjects.through._meta.db_table
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM {FTS_TABLE}")
        cursor.execute(f"""
            INSERT INTO {FTS_TABLE} (book_id, title, authors, subjects, synopsis, extra)
            SELECT b.id,
                   b.title || ' ' || b.subtitle,
                   (SELECT group_concat(a.name, ' ') FROM {book_author} ba
                      JOIN {author} a ON a.id = ba.author_id WHERE ba.book_id = b.id),
                   (SELECT group_concat(s.name, ' ') FROM {book_subject} bs
                      JOIN {subject} s ON s.id = bs.subject_id WHERE bs.book_id = b.id),
                   b.synopsis,
                   b.publisher || ' ' || b.series || ' ' || b.isbn || ' ' || b.cdd || ' '
                       || b.contributors || ' ' || b.tcc_course
              FROM {book} b
             WHERE b.is_active
        """)
        return cursor.rowcount


def to_match_query(text: str) -> str | None:
    """Converte o texto digitado numa consulta FTS5: todas as palavras, cada uma
    também como início de palavra ("algoritm" acha "algoritmos").

    As palavras vão entre aspas, então operadores e pontuação digitados não viram
    sintaxe do FTS5.

    Returns:
        A consulta, ou None quando não sobra nenhuma palavra.
    """
    words = re.findall(r"\w+", text)
    terms = ['"%s"*' % word.replace('"', '""') if len(word) >= 2 else '"%s"' % word for word in words]
    return " AND ".join(terms) or None


def ranked_ids(text: str, limit: int = 50, offset: int = 0) -> list[str]:
    """Ids dos livros ativos que casam com o texto, do mais relevante ao menos (bm25)."""
    query = to_match_query(text)
    return [] if query is None else _ranked(query, limit, offset)


# Palavras que não ajudam a achar livros num pedido em linguagem natural
# ("quero algo sobre ..."), já sem acentos e em minúsculas.
REQUEST_STOPWORDS = frozenset("""
    a o as os um uma uns umas de da do das dos e ou em na no nas nos ao aos com sem por pelo pela
    para pra pro que qual quais quem como mas mais muito muita pouco bem tem ter ser sobre sob
    entre ate apos isso isto esse essa este esta aquele aquela meu minha seu sua eu voce me mim
    algo alguma algum livro livros leitura leituras ler quero queria gostaria preciso procuro busco
    indique indica recomende recomenda sugira sugere sugestao sugestoes tema temas assunto assuntos
    coisa coisas tipo bom boa bons boas legal interessante favor obrigado obrigada
""".split())


def _normalize(word: str) -> str:
    return "".join(char for char in unicodedata.normalize("NFKD", word.lower())
                   if not unicodedata.combining(char))


def any_term_query(text: str) -> str | None:
    """Converte um pedido em linguagem natural numa consulta FTS5 que casa com
    **qualquer** palavra relevante, cada uma também como início de palavra.

    Diferente de `to_match_query` (todas as palavras), serve para juntar candidatos:
    o bm25 ainda põe primeiro os livros que casam com mais palavras. Palavras
    curtas e as de `REQUEST_STOPWORDS` são ignoradas.

    Returns:
        A consulta, ou None quando não sobra nenhuma palavra relevante.
    """
    words = [word for word in re.findall(r"\w+", text)
             if len(word) >= 3 and _normalize(word) not in REQUEST_STOPWORDS]
    terms = list(dict.fromkeys('"%s"*' % word.replace('"', '""') for word in words))
    return " OR ".join(terms) or None


def ranked_any_ids(text: str, limit: int = 30) -> list[str]:
    """Ids dos livros ativos que casam com alguma palavra relevante do pedido
    (`any_term_query`), do mais relevante ao menos (bm25)."""
    query = any_term_query(text)
    return [] if query is None else _ranked(query, limit, 0)


def _ranked(query: str, limit: int, offset: int) -> list[str]:
    weights = ", ".join(str(weight) for weight in BM25_WEIGHTS)
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT book_id FROM {FTS_TABLE} WHERE {FTS_TABLE} MATCH %s "
            f"ORDER BY bm25({FTS_TABLE}, {weights}) LIMIT %s OFFSET %s",
            [query, limit, offset],
        )
        return [row[0] for row in cursor.fetchall()]
