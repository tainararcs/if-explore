"""Índice de busca textual (FTS5) dos livros ativos.

A tabela `catalog_book_fts` é criada pela migração 0002. O índice é reconstruído
por inteiro a cada sincronização do catálogo: ~20 mil linhas levam poucos segundos
e evitam ter de manter gatilhos de atualização.
"""

from __future__ import annotations

import re

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
    if query is None:
        return []
    weights = ", ".join(str(weight) for weight in BM25_WEIGHTS)
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT book_id FROM {FTS_TABLE} WHERE {FTS_TABLE} MATCH %s "
            f"ORDER BY bm25({FTS_TABLE}, {weights}) LIMIT %s OFFSET %s",
            [query, limit, offset],
        )
        return [row[0] for row in cursor.fetchall()]
