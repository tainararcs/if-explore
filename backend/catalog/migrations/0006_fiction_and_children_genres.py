"""Gêneros Ficção e Infantojuvenil.

Ficção vem da forma literária da CDD (8x3 e B869.3) ou do assunto "ficção".
Infantojuvenil vem da CDD 028.5, usada pela biblioteca na coleção LIJ, ou de
assuntos como "literatura infantojuvenil" e "teatro infantil". As palavras-chave
evitam "infantil" sozinho, que também casaria com "educação infantil".
"""

from django.db import migrations

GENRES = [
    # (slug, nome, ordem, palavras-chave de assunto, prefixos de CDD)
    ("fiction", "Ficção", 13, ["ficcao"],
     ["B869.3", "813", "823", "833", "843", "853", "863", "869.3", "873", "883"]),
    ("children-youth", "Infantojuvenil", 14,
     ["infanto", "literatura infantil", "literatura juvenil", "teatro infantil", "teatro brasileiro infantil",
      "poesia infantil"],
     ["028.5", "B028.5"]),
]


def seed(apps, schema_editor):
    LiteraryGenre = apps.get_model("catalog", "LiteraryGenre")
    for slug, name, order, keywords, cdd_prefixes in GENRES:
        LiteraryGenre.objects.update_or_create(slug=slug, defaults={
            "name": name, "order": order, "subject_keywords": keywords, "cdd_prefixes": cdd_prefixes})


def unseed(apps, schema_editor):
    apps.get_model("catalog", "LiteraryGenre").objects.filter(slug__in=[g[0] for g in GENRES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0005_book_explanation"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
