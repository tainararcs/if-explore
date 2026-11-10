"""Admin do acervo.

A taxonomia é editável: é onde a biblioteca confirma o mapeamento dos cursos e
ajusta as regras de gênero. Livros e sincronizações são só leitura, porque vêm do
PHL e seriam sobrescritos na próxima sincronização. As explicações geradas por
IA podem ser apagadas (uma nova é gerada na próxima visita ao livro), não editadas.
"""

from django.contrib import admin
from django.http import HttpRequest

from catalog.models import Book, BookExplanation, Course, KnowledgeArea, LiteraryGenre, SyncRun

NEXT_SYNC_NOTE = "As mudanças valem para os livros a partir da próxima sincronização do catálogo."


@admin.register(KnowledgeArea)
class KnowledgeAreaAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "order", "cnpq_codes"]
    list_editable = ["order"]
    fieldsets = [(None, {"fields": ["slug", "name", "order", "cnpq_codes"], "description": NEXT_SYNC_NOTE})]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["name", "level", "area", "phl_codes", "tcc_names", "mapping_confirmed"]
    list_editable = ["mapping_confirmed"]
    list_filter = ["mapping_confirmed", "level", "area"]
    search_fields = ["name", "slug"]
    fieldsets = [
        (None, {"fields": ["slug", "name", "area", "level"]}),
        ("Reconhecimento no PHL", {
            "fields": ["phl_codes", "tcc_names", "mapping_confirmed"],
            "description": "O PHL não publica os nomes dos cursos: os códigos foram inferidos pelos "
                           "assuntos dos livros e precisam ser confirmados. " + NEXT_SYNC_NOTE,
        }),
    ]


@admin.register(LiteraryGenre)
class LiteraryGenreAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "order", "subject_keywords", "cdd_prefixes"]
    list_editable = ["order"]
    fieldsets = [
        (None, {"fields": ["slug", "name", "order"]}),
        ("Regras", {
            "fields": ["subject_keywords", "cdd_prefixes", "author_keywords"],
            "description": "O livro entra no gênero quando a CDD começa com um dos prefixos, ou quando um "
                           "assunto contém uma das palavras-chave e a CDD é literária (8xx). Com autores "
                           "preenchidos, um deles também precisa casar. " + NEXT_SYNC_NOTE,
        }),
    ]


class ReadOnlyAdmin(admin.ModelAdmin):
    """Admin só de consulta."""

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: object | None = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: object | None = None) -> bool:
        return False


@admin.register(Book)
class BookAdmin(ReadOnlyAdmin):
    list_display = ["title", "year", "area", "document_type", "copy_status", "copies_total",
                    "copies_available", "loans_total", "is_active"]
    list_filter = ["is_active", "copy_status", "area", "genres", "courses"]
    search_fields = ["id", "title", "isbn"]
    show_full_result_count = False


@admin.register(BookExplanation)
class BookExplanationAdmin(ReadOnlyAdmin):
    list_display = ["book", "model", "created_at"]
    search_fields = ["book__id", "book__title"]
    list_select_related = ["book"]

    def has_delete_permission(self, request: HttpRequest, obj: object | None = None) -> bool:
        return super(ReadOnlyAdmin, self).has_delete_permission(request, obj)


@admin.register(SyncRun)
class SyncRunAdmin(ReadOnlyAdmin):
    list_display = ["kind", "status", "started_at", "finished_at", "stats"]
    list_filter = ["kind", "status"]
