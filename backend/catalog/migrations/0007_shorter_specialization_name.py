"""Nome mais curto para a especialização em áreas naturais protegidas.

O nome completo não cabia num chip do onboarding; o nível (pós-graduação) já
aparece no título do grupo.
"""

from django.db import migrations

SLUG = "protected-areas-specialization"
SHORT_NAME = "Especialização em Áreas Naturais Protegidas"
FULL_NAME = "Especialização em Planejamento e Gestão de Áreas Naturais Protegidas"


def rename(apps, schema_editor):
    apps.get_model("catalog", "Course").objects.filter(slug=SLUG).update(name=SHORT_NAME)


def restore(apps, schema_editor):
    apps.get_model("catalog", "Course").objects.filter(slug=SLUG).update(name=FULL_NAME)


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0006_fiction_and_children_genres"),
    ]

    operations = [
        migrations.RunPython(rename, restore),
    ]
