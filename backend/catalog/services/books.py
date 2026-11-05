"""Consultas de livros: filtros, busca textual com relevância e carga em ordem."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from django.db import connection
from django.db.models import Case, Exists, F, IntegerField, OuterRef, Prefetch, QuerySet, Value, When
from django.db.models.functions import Upper

from catalog.models import Book, BookAuthor, CopyStatus
from catalog.services import search_index

SortOrder = Literal["relevance", "popular", "recent", "title"]

# Títulos com exemplar, mas nenhum livre para empréstimo (filtro available=false).
UNAVAILABLE_STATUSES = (CopyStatus.IN_LIBRARY_USE, CopyStatus.ON_LOAN, CopyStatus.UNAVAILABLE)
# Filtro `type` da API -> tipo de documento como o catálogo grava.
DOCUMENT_TYPES = {
    "book": "Livro",
    "ebook": "E-book",
    "audiobook": "Audio Livro",
    "thesis": "Teses, dissertações, monografias, tcc",
    "periodical": "Periódico",
}


@dataclass(frozen=True)
class BookFilters:
    """Filtros de listagem. Valores do mesmo filtro se somam (OU); filtros diferentes
    precisam valer juntos (E)."""

    area_ids: tuple[str, ...] = ()
    course_ids: tuple[str, ...] = ()
    genre_ids: tuple[str, ...] = ()
    #: Chaves de DOCUMENT_TYPES.
    types: tuple[str, ...] = ()
    #: True: só com exemplar disponível; False: só sem; None: todos.
    available: bool | None = None


@dataclass(frozen=True)
class BookPage:
    ids: list[str]
    total: int


def with_relations(queryset: QuerySet[Book]) -> QuerySet[Book]:
    """Pré-carrega autores (em ordem), assuntos, cursos e gêneros, usados pelos schemas."""
    authors = Prefetch("bookauthor_set", queryset=BookAuthor.objects.select_related("author").order_by("position"))
    return queryset.prefetch_related(authors, "subjects", "courses", "genres")


def load_in_order(ids: Sequence[str]) -> list[Book]:
    """Livros ativos com as relações, na ordem dos ids; ids ausentes são ignorados."""
    books = {book.id: book for book in with_relations(Book.objects.filter(is_active=True, id__in=ids))}
    return [books[book_id] for book_id in ids if book_id in books]


def filtered(filters: BookFilters) -> QuerySet[Book]:
    """Livros ativos que atendem aos filtros."""
    queryset = Book.objects.filter(is_active=True)
    if filters.area_ids:
        queryset = queryset.filter(area_id__in=filters.area_ids)
    if filters.course_ids:
        queryset = queryset.filter(Exists(Book.courses.through.objects.filter(
            book_id=OuterRef("pk"), course_id__in=filters.course_ids)))
    if filters.genre_ids:
        queryset = queryset.filter(Exists(Book.genres.through.objects.filter(
            book_id=OuterRef("pk"), literarygenre_id__in=filters.genre_ids)))
    if filters.types:
        queryset = queryset.filter(document_type__in=[DOCUMENT_TYPES[key] for key in filters.types])
    if filters.available is True:
        queryset = queryset.filter(copy_status=CopyStatus.AVAILABLE)
    elif filters.available is False:
        queryset = queryset.filter(copy_status__in=UNAVAILABLE_STATUSES)
    return queryset


def search(text: str, filters: BookFilters, *, sort: SortOrder | None = None,
           prefer_area_ids: Sequence[str] = (), page: int = 1, page_size: int = 24) -> BookPage:
    """Uma página de ids de livros.

    Com texto, busca no índice FTS5 (título, autores, assuntos, sinopse e extras) e,
    por padrão, ordena por relevância (bm25). Sem texto, lista pelos filtros e, por
    padrão, ordena pelos que têm mais exemplares (a biblioteca compra mais
    exemplares dos títulos mais procurados, como a bibliografia dos cursos). Em qualquer caso, `prefer_area_ids` põe os
    livros dessas áreas primeiro, como o frontend faz com as áreas do visitante.

    Args:
        text: Texto digitado; vazio ou só pontuação lista sem busca textual.
        sort: Ordem; None escolhe a padrão. "relevance" só faz sentido com texto.
        page: Página, a partir de 1.
        page_size: Livros por página.
    """
    match = search_index.to_match_query(text) if text.strip() else None
    sort = sort or ("relevance" if match else "popular")
    offset = (page - 1) * page_size
    if match is None:
        return _list_page(filtered(filters), sort, prefer_area_ids, offset, page_size)
    return _search_page(match, filtered(filters), sort, prefer_area_ids, offset, page_size)


def _list_page(queryset: QuerySet[Book], sort: SortOrder, prefer_area_ids: Sequence[str],
               offset: int, limit: int) -> BookPage:
    ordering = {
        "relevance": [F("copies_total").desc(nulls_last=True), Upper("title")],
        "popular": [F("copies_total").desc(nulls_last=True), Upper("title")],
        "recent": [F("cataloged_at").desc(nulls_last=True), Upper("title")],
        "title": [Upper("title"), "id"],
    }[sort]
    if prefer_area_ids:
        queryset = queryset.annotate(preferred=Case(When(area_id__in=prefer_area_ids, then=Value(1)),
                                                    default=Value(0), output_field=IntegerField()))
        ordering = ["-preferred", *ordering]
    total = queryset.count()
    ids = list(queryset.order_by(*ordering, "id").values_list("id", flat=True)[offset:offset + limit])
    return BookPage(ids, total)


def _search_page(match: str, queryset: QuerySet[Book], sort: SortOrder, prefer_area_ids: Sequence[str],
                 offset: int, limit: int) -> BookPage:
    """Busca textual: junta o índice FTS5 aos livros filtrados pelo ORM."""
    fts, book = search_index.FTS_TABLE, Book._meta.db_table
    filtered_sql, filtered_params = queryset.values("id").query.sql_with_params()
    where = f"{fts} MATCH %s AND b.id IN ({filtered_sql})"
    params: list[object] = [match, *filtered_params]
    weights = ", ".join(str(weight) for weight in search_index.BM25_WEIGHTS)
    order = {
        "relevance": f"bm25({fts}, {weights})",
        "popular": "b.copies_total IS NULL, b.copies_total DESC, upper(b.title)",
        "recent": "b.cataloged_at IS NULL, b.cataloged_at DESC, upper(b.title)",
        "title": "upper(b.title)",
    }[sort]
    order_params: list[object] = []
    if prefer_area_ids:
        placeholders = ", ".join(["%s"] * len(prefer_area_ids))
        order = f"CASE WHEN b.area_id IN ({placeholders}) THEN 0 ELSE 1 END, {order}"
        order_params = list(prefer_area_ids)
    join = f"FROM {fts} JOIN {book} b ON b.id = {fts}.book_id WHERE {where}"
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT count(*) {join}", params)
        total = cursor.fetchone()[0]
        cursor.execute(f"SELECT b.id {join} ORDER BY {order}, b.id LIMIT %s OFFSET %s",
                       [*params, *order_params, limit, offset])
        ids = [row[0] for row in cursor.fetchall()]
    return BookPage(ids, total)
