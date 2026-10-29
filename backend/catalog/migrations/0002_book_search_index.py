"""Índice de busca textual (FTS5) dos livros.

É uma tabela virtual do SQLite, sem modelo no ORM: a sincronização a reconstrói por
inteiro (`catalog.services.search_index`). `unicode61 remove_diacritics 2` ignora
acentos e caixa nos dois lados da busca; `prefix` acelera buscas por início de
palavra com 2 e 3 letras.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE VIRTUAL TABLE catalog_book_fts USING fts5(
                    book_id UNINDEXED,
                    title,
                    authors,
                    subjects,
                    synopsis,
                    extra,
                    tokenize = 'unicode61 remove_diacritics 2',
                    prefix = '2 3'
                )
            """,
            reverse_sql="DROP TABLE catalog_book_fts",
        ),
    ]
