"""Relacionados, prateleiras da home e candidatos do onboarding.

Mesmas regras que o frontend usava com o acervo fictício (`related-books.ts`,
`recommendation-service.ts`, `onboarding-draft.ts`), agora calculadas no banco
sobre o acervo real. Só entram tipos que fazem sentido recomendar (livros, e-books,
audiolivros e TCCs). Em empates, vêm primeiro os livros com capa e os mais
emprestados.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from itertools import zip_longest

from django.db import connection
from django.db.models import (
    Case,
    Count,
    Exists,
    F,
    FloatField,
    IntegerField,
    OuterRef,
    QuerySet,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import Coalesce

from catalog.models import Book, BookAuthor, Course, KnowledgeArea, LiteraryGenre
from catalog.services.books import DOCUMENT_TYPES

RECOMMENDABLE_TYPES = tuple(DOCUMENT_TYPES[key] for key in ("book", "ebook", "audiobook", "thesis"))
SHELF_SIZE = 12
MIN_SHELF_SIZE = 3
MAX_SEED_SHELVES = 3
REQUIRED_SEED_BOOKS = 3
# Candidatos avaliados por afinidade antes de cortar nas prateleiras.
MAX_AFFINITY_CANDIDATES = 200


@dataclass(frozen=True)
class Profile:
    """Preferências do visitante (ids já validados contra o banco não são exigidos)."""

    area_ids: tuple[str, ...] = ()
    course_ids: tuple[str, ...] = ()
    seed_book_ids: tuple[str, ...] = ()
    genre_ids: tuple[str, ...] = ()


@dataclass
class Shelf:
    id: str
    kind: str
    subject: str | None
    book_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Related:
    same_author: tuple[str, list[str]] | None
    related_ids: list[str]


def recommendable() -> QuerySet[Book]:
    """Livros ativos dos tipos que entram nas recomendações."""
    return Book.objects.filter(is_active=True, document_type__in=RECOMMENDABLE_TYPES)


def _tie_breakers() -> list[object]:
    has_cover = Case(When(cover_url="", then=Value(0)), default=Value(1), output_field=IntegerField())
    return [has_cover.desc(), F("copies_total").desc(nulls_last=True), "id"]


# ---- afinidade entre livros
def affinity_ranking(book: Book, *, min_score: int = 1, limit: int = MAX_AFFINITY_CANDIDATES) -> list[tuple[str, int]]:
    """Livros parecidos com `book`, do mais ao menos parecido.

    Pontos: cada autor em comum 3, cada assunto em comum 2, algum gênero em comum 1,
    mesma área 1. Só entram livros com autor ou assunto em comum; o próprio livro
    fica de fora.

    Returns:
        (id, pontos) dos livros com pontuação acima de `min_score`.
    """
    book_author, book_table = BookAuthor._meta.db_table, Book._meta.db_table
    book_subject, book_genre = Book.subjects.through._meta.db_table, Book.genres.through._meta.db_table
    types = ", ".join(["%s"] * len(RECOMMENDABLE_TYPES))
    with connection.cursor() as cursor:
        cursor.execute(f"""
            WITH shared AS (
                SELECT ba.book_id, 3 AS points FROM {book_author} ba
                 WHERE ba.author_id IN (SELECT author_id FROM {book_author} WHERE book_id = %s)
                UNION ALL
                SELECT bs.book_id, 2 FROM {book_subject} bs
                 WHERE bs.subject_id IN (SELECT subject_id FROM {book_subject} WHERE book_id = %s)
            ), scored AS (
                SELECT book_id, sum(points) AS points FROM shared WHERE book_id <> %s GROUP BY book_id
            )
            SELECT b.id,
                   s.points
                   + CASE WHEN EXISTS (SELECT 1 FROM {book_genre} g WHERE g.book_id = b.id AND g.literarygenre_id IN
                         (SELECT literarygenre_id FROM {book_genre} WHERE book_id = %s)) THEN 1 ELSE 0 END
                   + CASE WHEN b.area_id IS NOT NULL AND b.area_id = %s THEN 1 ELSE 0 END AS score
              FROM scored s JOIN {book_table} b ON b.id = s.book_id
             WHERE b.is_active AND b.document_type IN ({types})
             ORDER BY score DESC, b.cover_url = '', b.copies_total IS NULL, b.copies_total DESC, b.id
        """, [book.id, book.id, book.id, book.id, book.area_id, *RECOMMENDABLE_TYPES])
        ranking = [(row[0], int(row[1])) for row in cursor.fetchall()]
    return [(book_id, score) for book_id, score in ranking if score > min_score][:limit]


def related(book: Book) -> Related:
    """Prateleiras de relacionados de um livro: outros livros do primeiro autor que
    tenha ao menos dois entre os parecidos, e os demais por afinidade."""
    ranked = [book_id for book_id, _ in affinity_ranking(book, min_score=0)]
    authors = list(BookAuthor.objects.filter(book=book).order_by("position").select_related("author"))
    books_by_author: dict[int, list[str]] = {}
    for link in BookAuthor.objects.filter(book_id__in=ranked, author_id__in=[a.author_id for a in authors]):
        books_by_author.setdefault(link.author_id, []).append(link.book_id)
    same_author = None
    author_books: set[str] = set()
    for link in authors:
        others = set(books_by_author.get(link.author_id, []))
        if len(others) >= 2:
            author_books = others
            same_author = (link.author.name, [book_id for book_id in ranked if book_id in others][:SHELF_SIZE])
            break
    return Related(same_author, [book_id for book_id in ranked if book_id not in author_books][:SHELF_SIZE])


# ---- home
def _profile_score(queryset: QuerySet[Book], profile: Profile, seed_subject_ids: Sequence[int]) -> QuerySet[Book]:
    """Anota `score`: curso 4, área 2, gênero 1,5 e 1 por assunto em comum com os escolhidos."""
    courses = Book.courses.through.objects.filter(book_id=OuterRef("pk"), course_id__in=profile.course_ids)
    genres = Book.genres.through.objects.filter(book_id=OuterRef("pk"), literarygenre_id__in=profile.genre_ids)
    shared_subjects = (Book.subjects.through.objects
                       .filter(book_id=OuterRef("pk"), subject_id__in=seed_subject_ids)
                       .values("book_id").annotate(count=Count("*")).values("count"))
    return queryset.annotate(score=(
        Case(When(Exists(courses), then=Value(4.0)), default=Value(0.0), output_field=FloatField())
        + Case(When(area_id__in=profile.area_ids, then=Value(2.0)), default=Value(0.0), output_field=FloatField())
        + Case(When(Exists(genres), then=Value(1.5)), default=Value(0.0), output_field=FloatField())
        + Coalesce(Subquery(shared_subjects, output_field=FloatField()), Value(0.0))
    ))


def _seed_subject_ids(seed_book_ids: Sequence[str]) -> list[int]:
    return list(Book.subjects.through.objects.filter(book_id__in=seed_book_ids)
                .values_list("subject_id", flat=True).distinct())


def profile_ranked_ids(profile: Profile, limit: int) -> list[str]:
    """Livros recomendáveis mais próximos das preferências (mesma pontuação da
    prateleira "para você"), sem os títulos escolhidos; vazio sem afinidade."""
    pool = recommendable().exclude(id__in=profile.seed_book_ids)
    scored = _profile_score(pool, profile, _seed_subject_ids(profile.seed_book_ids)).filter(score__gt=0)
    return list(scored.order_by("-score", *_tie_breakers()).values_list("id", flat=True)[:limit])


def home_shelves(profile: Profile) -> list[Shelf]:
    """Prateleiras da home: "para você", "porque você escolheu" (até 3 títulos),
    "mais da área" e "por prazer" (gêneros). Só ficam as com pelo menos 3 livros, e
    os títulos escolhidos não aparecem."""
    seeds = list(Book.objects.filter(is_active=True, id__in=profile.seed_book_ids))
    seeds.sort(key=lambda book: profile.seed_book_ids.index(book.id))
    seed_subject_ids = _seed_subject_ids([book.id for book in seeds])
    pool = recommendable().exclude(id__in=profile.seed_book_ids)
    scored = _profile_score(pool, profile, seed_subject_ids)

    def top(queryset: QuerySet[Book], *ordering: object) -> list[str]:
        return list(queryset.order_by(*ordering, *_tie_breakers()).values_list("id", flat=True)[:SHELF_SIZE])

    shelves = [Shelf("for-you", "forYou", None, top(scored.filter(score__gt=0), "-score"))]
    excluded = set(profile.seed_book_ids)
    for seed in seeds[:MAX_SEED_SHELVES]:
        ids = [book_id for book_id, _ in affinity_ranking(seed, min_score=1) if book_id not in excluded]
        shelves.append(Shelf("because-%s" % seed.id, "becauseYouChose", seed.title, ids[:SHELF_SIZE]))
    for area in KnowledgeArea.objects.filter(slug__in=profile.area_ids):
        shelves.append(Shelf("area-%s" % area.slug, "moreFromArea", area.name,
                             top(scored.filter(area=area), "-score")))
    for genre in LiteraryGenre.objects.filter(slug__in=profile.genre_ids):
        shelves.append(Shelf("genre-%s" % genre.slug, "forPleasure", genre.name, top(pool.filter(genres=genre))))
    return [shelf for shelf in shelves if len(shelf.book_ids) >= MIN_SHELF_SIZE]


# ---- onboarding
def onboarding_candidates(area_ids: Sequence[str], course_ids: Sequence[str], limit: int) -> list[str]:
    """Títulos para o visitante escolher no onboarding.

    O limite é dividido entre as áreas escolhidas e as dos cursos marcados, e as
    áreas se intercalam na lista: assim nenhuma área fica sem títulos quando o
    visitante filtra por ela. Dentro de cada área, vêm primeiro os livros dos
    cursos marcados. Se sobrarem menos de 3, completa com os demais.
    """
    course_areas = Course.objects.filter(slug__in=course_ids).values_list("area_id", flat=True)
    groups = list(dict.fromkeys([*area_ids, *course_areas]))
    ids: list[str] = []
    if groups:
        per_group = math.ceil(limit / len(groups))
        courses = Book.courses.through.objects.filter(book_id=OuterRef("pk"), course_id__in=course_ids)
        by_group = [
            list(recommendable().filter(area_id=area)
                 .annotate(score=Case(When(Exists(courses), then=Value(1)), default=Value(0),
                                      output_field=IntegerField()))
                 .order_by("-score", *_tie_breakers()).values_list("id", flat=True)[:per_group])
            for area in groups
        ]
        ids = list(dict.fromkeys(book_id for round_ in zip_longest(*by_group) for book_id in round_ if book_id))
        ids = ids[:limit]
    if len(ids) >= REQUIRED_SEED_BOOKS:
        return ids
    rest = recommendable().exclude(id__in=ids).order_by(*_tie_breakers()).values_list("id", flat=True)
    return ids + list(rest[:limit - len(ids)])
