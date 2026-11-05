"""Rotas da API do acervo (montadas em /api/ por `config.urls`).

As rotas só validam parâmetros, chamam os serviços e convertem o resultado nos
schemas; as regras ficam em `catalog.services`. Listas na query string usam a
chave repetida: `?area=technology&area=humanities`.
"""

from __future__ import annotations

from typing import Literal

from django.http import HttpRequest
from ninja import Query, Router
from ninja.errors import HttpError

from catalog.models import Book, Course, KnowledgeArea, LiteraryGenre, SyncKind, SyncRun, SyncStatus
from catalog.schemas import (
    AreaOut,
    BookDetailOut,
    BookPageOut,
    BookSummaryOut,
    CourseOut,
    GenreOut,
    ProfileIn,
    RecommendationsOut,
    RelatedOut,
    SameAuthorOut,
    ShelfOut,
    StatusOut,
    SyncOut,
)
from catalog.services import availability, books, recommendations

router = Router()

BookType = Literal["book", "ebook", "audiobook", "thesis", "periodical"]
MAX_IDS = 60
MAX_PAGE_SIZE = 100
MAX_QUERY_LENGTH = 200


def _summaries(ids: list[str]) -> list[BookSummaryOut]:
    return [BookSummaryOut.from_model(book) for book in books.load_in_order(ids)]


def _active_book(book_id: str) -> Book:
    book = books.with_relations(Book.objects.filter(id=book_id, is_active=True)).first()
    if book is None:
        raise HttpError(404, "livro não encontrado")
    return book


# ---- taxonomia
@router.get("/areas", response=list[AreaOut], by_alias=True, tags=["taxonomia"])
def list_areas(request: HttpRequest) -> list[AreaOut]:
    """Grandes áreas do conhecimento, na ordem de exibição."""
    return [AreaOut.from_model(area) for area in KnowledgeArea.objects.all()]


@router.get("/courses", response=list[CourseOut], by_alias=True, tags=["taxonomia"])
def list_courses(request: HttpRequest) -> list[CourseOut]:
    """Cursos do campus, por nível e nome."""
    return [CourseOut.from_model(course) for course in Course.objects.all()]


@router.get("/genres", response=list[GenreOut], by_alias=True, tags=["taxonomia"])
def list_genres(request: HttpRequest) -> list[GenreOut]:
    """Gêneros literários, na ordem de exibição."""
    return [GenreOut.from_model(genre) for genre in LiteraryGenre.objects.all()]


# ---- livros
@router.get("/books", response=BookPageOut, by_alias=True, tags=["livros"])
def list_books(
    request: HttpRequest,
    q: str = Query("", max_length=MAX_QUERY_LENGTH, description="Texto livre: título, autor, assunto, sinopse."),
    ids: list[str] = Query([], description="Livros pedidos, na ordem dada; ignora os demais parâmetros."),
    area: list[str] = Query([], description="Áreas (OU)."),
    course: list[str] = Query([], description="Cursos (OU)."),
    genre: list[str] = Query([], description="Gêneros (OU)."),
    type_: list[BookType] = Query([], alias="type", description="Tipos de documento (OU)."),
    available: bool | None = Query(None, description="Só com (true) ou sem (false) exemplar livre para "
                                   "empréstimo; títulos de situação incerta ou sem exemplar ficam fora dos dois."),
    prefer_area: list[str] = Query([], alias="preferArea", description="Áreas que vêm primeiro."),
    sort: books.SortOrder | None = Query(None, description="Padrão: relevance com q, popular sem."),
    page: int = Query(1, ge=1),
    page_size: int = Query(24, ge=1, le=MAX_PAGE_SIZE, alias="pageSize"),
) -> BookPageOut:
    """Busca e lista livros ativos, paginados."""
    if ids:
        if len(ids) > MAX_IDS:
            raise HttpError(422, "no máximo %d ids por consulta" % MAX_IDS)
        items = _summaries(ids)
        return BookPageOut(items=items, total=len(items), page=1, page_size=len(items))
    filters = books.BookFilters(area_ids=tuple(area), course_ids=tuple(course), genre_ids=tuple(genre),
                                types=tuple(type_), available=available)
    result = books.search(q, filters, sort=sort, prefer_area_ids=prefer_area, page=page, page_size=page_size)
    return BookPageOut(items=_summaries(result.ids), total=result.total, page=page, page_size=page_size)


@router.get("/books/{book_id}", response=BookDetailOut, by_alias=True, tags=["livros"])
def get_book(request: HttpRequest, book_id: str) -> BookDetailOut:
    """Um livro completo. A disponibilidade é consultada no PHL se tiver mais de 15 min."""
    book = _active_book(book_id)
    if availability.refresh_if_stale(book):
        book = _active_book(book_id)
    return BookDetailOut.from_model(book)


@router.get("/books/{book_id}/related", response=RelatedOut, by_alias=True, tags=["livros"])
def get_related(request: HttpRequest, book_id: str) -> RelatedOut:
    """Outros livros de um autor em comum e os demais por afinidade."""
    result = recommendations.related(_active_book(book_id))
    same_author = None
    if result.same_author:
        author, author_ids = result.same_author
        same_author = SameAuthorOut(author=author, books=_summaries(author_ids))
    return RelatedOut(same_author=same_author, related=_summaries(result.related_ids))


# ---- recomendações
@router.post("/recommendations", response=RecommendationsOut, by_alias=True, tags=["recomendações"])
def get_recommendations(request: HttpRequest, profile: ProfileIn) -> RecommendationsOut:
    """Prateleiras da home para as preferências do visitante.

    É POST porque o perfil vai no corpo; não grava nada.
    """
    shelves = recommendations.home_shelves(recommendations.Profile(
        area_ids=tuple(profile.area_ids), course_ids=tuple(profile.course_ids),
        seed_book_ids=tuple(profile.seed_book_ids), genre_ids=tuple(profile.genre_ids)))
    loaded = {book.id: book for book in books.load_in_order(
        list(dict.fromkeys(book_id for shelf in shelves for book_id in shelf.book_ids)))}
    return RecommendationsOut(
        shelves=[ShelfOut(id=shelf.id, kind=shelf.kind, subject=shelf.subject,
                          books=[BookSummaryOut.from_model(loaded[i]) for i in shelf.book_ids if i in loaded])
                 for shelf in shelves],
        areas=[AreaOut.from_model(area) for area in KnowledgeArea.objects.filter(slug__in=profile.area_ids)],
    )


@router.get("/recommendations/candidates", response=list[BookSummaryOut], by_alias=True, tags=["recomendações"])
def get_candidates(
    request: HttpRequest,
    area: list[str] = Query([], description="Áreas escolhidas."),
    course: list[str] = Query([], description="Cursos escolhidos; vêm antes das áreas."),
    limit: int = Query(48, ge=1, le=MAX_PAGE_SIZE),
) -> list[BookSummaryOut]:
    """Títulos para o visitante escolher no onboarding."""
    return _summaries(recommendations.onboarding_candidates(area, course, limit))


# ---- status
def _last_sync(kind: SyncKind) -> SyncOut | None:
    run = SyncRun.objects.filter(kind=kind, status=SyncStatus.SUCCESS).first()
    if run is None or run.finished_at is None:
        return None
    return SyncOut(finished_at=run.finished_at, stats=run.stats)


@router.get("/status", response=StatusOut, by_alias=True, tags=["status"])
def get_status(request: HttpRequest) -> StatusOut:
    """Tamanho do acervo local e as últimas sincronizações com o PHL."""
    active = Book.objects.filter(is_active=True)
    return StatusOut(active_books=active.count(),
                     books_with_copies=active.exclude(copy_status="").count(),
                     catalog_sync=_last_sync(SyncKind.CATALOG))
