"""Sincronização do acervo com o PHL.

`sync_catalog` baixa o snapshot dos metadados (2 requisições: contagem e página
única) e a situação resumida dos exemplares em lote (5 requisições do formato
decorado, ver `phl_client.client.STATUS_TITLE_PREFIXES`, mais ~6 enquanto o PHL
tiver o registro defeituoso que derruba esse formato), ~1,5 min no total, e aplica
tudo numa transação. Roda a cada 6 h.

A contagem exata de exemplares livres e os empréstimos só vêm da consulta ao vivo
da página do livro (`catalog.services.availability`).
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TypeVar

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from catalog.models import (
    Author,
    Book,
    BookAuthor,
    CopyStatus,
    Course,
    KnowledgeArea,
    LiteraryGenre,
    Subject,
    SyncKind,
    SyncRun,
    SyncStatus,
)
from catalog.services import copy_status, search_index
from catalog.services.classification import (
    CourseRule,
    GenreRule,
    resolve_area,
    resolve_courses,
    resolve_genres,
)
from phl_client import Book as PhlBook
from phl_client import Library
from phl_client.client import MAX_PAGE_SIZE
from phl_client.fields import Record
from phl_client.parsers import CopyStatusItem
from phl_client.text import first_text, normalize

logger = logging.getLogger(__name__)

# Campos do snapshot. Os exemplares ficam de fora: ver `COPY_BATCH_FIELDS`.
SNAPSHOT_FIELDS = [
    "title", "subtitle", "contributors", "publisher", "city", "country", "year", "edition", "volume",
    "series", "pages", "physical_description", "isbn", "issn", "issue", "volume_year", "cdd", "cutter",
    "synopsis", "notes", "remarks", "languages", "medium", "cnpq_area", "document_type",
    "bibliographic_level", "phl_course_codes", "tcc_course", "links", "cover_url", "cataloged_at", "raw",
    "area", "is_active", "synced_at",
]
# Campos da situação em lote, gravados só quando o snapshot traz os exemplares. A
# contagem exata e os empréstimos (`copies_available`, `loans_total`) vêm só da
# consulta ao vivo e nunca são sobrescritos pela sincronização.
COPY_BATCH_FIELDS = ["copies_total", "copy_statuses", "copy_status", "copies_synced_at"]
BATCH_SIZE = 500
# Uma execução "em andamento" mais antiga que isto é considerada abandonada
# (processo morto) e não impede uma nova.
STALE_RUN_AFTER = timedelta(hours=12)

NamedModel = TypeVar("NamedModel", Author, Subject)


class SyncError(Exception):
    """A sincronização não pôde ser aplicada (snapshot suspeito, outra em andamento)."""


@dataclass(frozen=True)
class Taxonomy:
    """Regras de classificação carregadas do banco."""

    cnpq_to_area: dict[str, str]
    area_slugs: frozenset[str]
    courses: tuple[CourseRule, ...]
    genres: tuple[GenreRule, ...]

    @classmethod
    def load(cls) -> Taxonomy:
        areas = list(KnowledgeArea.objects.all())
        return cls(
            cnpq_to_area={str(code): area.slug for area in areas for code in area.cnpq_codes},
            area_slugs=frozenset(area.slug for area in areas),
            courses=tuple(CourseRule(course.slug, frozenset(map(str, course.phl_codes)),
                                     frozenset(normalize(name.strip()) for name in course.tcc_names))
                          for course in Course.objects.all()),
            genres=tuple(GenreRule(genre.slug, tuple(normalize(k) for k in genre.subject_keywords),
                                   tuple(p.strip().upper() for p in genre.cdd_prefixes),
                                   tuple(normalize(a) for a in genre.author_keywords))
                         for genre in LiteraryGenre.objects.all()),
        )


def make_library() -> Library:
    """Cliente do PHL configurado pelo settings, sem cache (cada execução quer dados novos)."""
    return Library(settings.PHL_CATALOG_URL, pause=settings.PHL_PAUSE, cache=0, connect=False)


# ---- snapshot do catálogo
def sync_catalog(library: Library | None = None, *, min_ratio: float | None = None) -> SyncRun:
    """Baixa o acervo inteiro e a situação dos exemplares e aplica o snapshot.
    Registra a execução em `SyncRun`.

    Se qualquer parte do download falhar, nada é aplicado: a próxima execução tenta
    de novo.

    Raises:
        SyncError: Outra sincronização do catálogo em andamento, ou snapshot suspeito.
        LibraryError: O PHL falhou (a execução fica registrada como falha).
    """
    run = _start_run(SyncKind.CATALOG)
    started = time.monotonic()
    try:
        library = library or make_library()
        records = list(library.phl.search_all("$", mode="exp", page_size=MAX_PAGE_SIZE))
        statuses = list(library.phl.copy_statuses())
        stats = apply_snapshot(records, statuses,
                               min_ratio=settings.CATALOG_SYNC_MIN_RATIO if min_ratio is None else min_ratio)
    except Exception as error:
        _finish_run(run, SyncStatus.FAILED, error=str(error))
        raise
    stats["seconds"] = round(time.monotonic() - started, 1)
    _finish_run(run, SyncStatus.SUCCESS, stats)
    return run


def apply_snapshot(records: Sequence[Record], copy_statuses: Sequence[CopyStatusItem] | None = None, *,
                   min_ratio: float, now: datetime | None = None) -> dict[str, int]:
    """Grava um snapshot do PHL: cria e atualiza livros, grava a situação dos
    exemplares, refaz autores, assuntos, cursos e gêneros, desativa os títulos que
    saíram e reconstrói o índice de busca.

    Tudo numa transação: a API continua vendo a versão anterior até o fim.

    Args:
        records: Registros de `PhlClient.search_all`.
        copy_statuses: Itens de `PhlClient.copy_statuses`; None mantém os exemplares
            gravados. Título do snapshot sem item fica sem exemplar: o formato
            decorado omite o código justamente dos títulos sem exemplar.
        min_ratio: Fração mínima dos títulos ativos que o snapshot precisa ter, e
            dos registros do snapshot que a leitura dos exemplares precisa ter.
        now: Instante da sincronização (testes).

    Raises:
        SyncError: Quando o snapshot ou a leitura dos exemplares tem bem menos
            títulos que o esperado (resposta truncada).
    """
    books = list({book.id: book for book in (PhlBook.from_record(record) for record in records
                                             if record.get("title_id"))}.values())
    active = Book.objects.filter(is_active=True).count()
    if active and len(books) < active * min_ratio:
        raise SyncError("snapshot com %d títulos, menos de %.0f%% dos %d ativos: parece truncado; nada foi aplicado"
                        % (len(books), min_ratio * 100, active))
    if copy_statuses is not None and len(copy_statuses) < len(records) * min_ratio:
        raise SyncError("situação dos exemplares com %d títulos, menos de %.0f%% dos %d do snapshot: "
                        "parece truncada; nada foi aplicado" % (len(copy_statuses), min_ratio * 100, len(records)))
    taxonomy = Taxonomy.load()
    now = now or timezone.now()
    existing = set(Book.objects.values_list("id", flat=True))
    rows = [_to_model(book, taxonomy, now) for book in books]
    update_fields = SNAPSHOT_FIELDS
    if copy_statuses is not None:
        by_id = {item["title_id"]: item for item in copy_statuses if item["title_id"]}
        for row in rows:
            _set_copy_batch(row, by_id.get(row.id), now)
        update_fields = SNAPSHOT_FIELDS + COPY_BATCH_FIELDS

    with transaction.atomic():
        author_ids = _upsert_names(Author, (name for book in books for name in book.authors))
        subject_ids = _upsert_names(Subject, (name for book in books for name in book.subjects))
        Book.objects.bulk_create(rows, batch_size=BATCH_SIZE, update_conflicts=True, unique_fields=["id"],
                                 update_fields=update_fields)
        _replace_relations(books, taxonomy, author_ids, subject_ids, now)
        deactivated = Book.objects.filter(is_active=True, synced_at__lt=now).update(is_active=False)
        indexed = search_index.rebuild()

    created = sum(book.id not in existing for book in books)
    stats = {"records": len(records), "books": len(books), "created": created,
             "updated": len(books) - created, "deactivated": deactivated, "indexed": indexed}
    if copy_statuses is not None:
        for status in (CopyStatus.AVAILABLE, CopyStatus.UNCERTAIN, CopyStatus.NO_COPIES):
            stats[status.value] = sum(row.copy_status == status for row in rows)
    logger.info("catálogo sincronizado: %s", stats)
    return stats


def _upsert_names(model: type[NamedModel], names: Iterable[str]) -> dict[str, int]:
    """Garante uma linha por nome normalizado e devolve nome normalizado -> id."""
    by_normalized: dict[str, str] = {}
    for name in names:
        by_normalized.setdefault(normalize(name), name)
    model.objects.bulk_create([model(name=name, normalized_name=key) for key, name in by_normalized.items()],
                              batch_size=BATCH_SIZE, ignore_conflicts=True)
    return dict(model.objects.values_list("normalized_name", "id"))


def _to_model(book: PhlBook, taxonomy: Taxonomy, now: datetime) -> Book:
    area = resolve_area(first_text(book.raw.get("knowledge_area")) or "", book.cdd or "", taxonomy.cnpq_to_area)
    return Book(
        id=book.id, title=book.title, subtitle=book.subtitle or "", contributors=book.contributors or "",
        publisher=book.publisher or "", city=book.city or "", country=book.country or "", year=book.year,
        edition=book.edition or "", volume=book.volume or "", series=book.series or "", pages=book.pages,
        physical_description=book.physical_description or "", isbn=book.isbn or "", issn=book.issn or "",
        issue=book.issue or "", volume_year=book.volume_year or "", cdd=book.cdd or "",
        cutter=book.cutter or "", synopsis=book.synopsis or "", notes=book.notes, remarks=book.remarks or "",
        languages=book.languages, medium=book.medium or "",
        cnpq_area=first_text(book.raw.get("knowledge_area")) or "", document_type=book.document_type or "",
        bibliographic_level=book.bibliographic_level or "", phl_course_codes=book.course_codes,
        tcc_course=book.tcc_course or "", links=list(book.links), cover_url=book.cover_url or "",
        cataloged_at=book.cataloged_at, raw=book.raw,
        area_id=area if area in taxonomy.area_slugs else None, is_active=True, synced_at=now,
    )


def _set_copy_batch(book: Book, item: CopyStatusItem | None, now: datetime) -> None:
    """Preenche a situação em lote de um livro; sem item, o título não tem exemplar."""
    total, statuses = (item["total"], item["statuses"]) if item else (0, [])
    book.copies_total, book.copy_statuses = total, statuses
    book.copy_status = copy_status.from_batch(statuses, total)
    book.copies_synced_at = now


def _replace_relations(books: Sequence[PhlBook], taxonomy: Taxonomy, author_ids: dict[str, int],
                       subject_ids: dict[str, int], now: datetime) -> None:
    """Refaz autores, assuntos, cursos e gêneros dos livros deste snapshot.

    Os livros do snapshot são os de `synced_at == now`; filtrar por eles evita
    passar ~20 mil ids numa cláusula IN.
    """
    book_subjects, book_courses, book_genres = Book.subjects.through, Book.courses.through, Book.genres.through
    for model in (BookAuthor, book_subjects, book_courses, book_genres):
        model.objects.filter(book__synced_at=now).delete()

    authors, subjects, courses, genres = [], [], [], []
    for book in books:
        author_keys = list(dict.fromkeys(normalize(name) for name in book.authors))
        authors += [BookAuthor(book_id=book.id, author_id=author_ids[key], position=position)
                    for position, key in enumerate(author_keys)]
        subjects += [book_subjects(book_id=book.id, subject_id=subject_ids[key])
                     for key in dict.fromkeys(normalize(name) for name in book.subjects)]
        courses += [book_courses(book_id=book.id, course_id=slug)
                    for slug in resolve_courses(book.course_codes, book.tcc_course or "", taxonomy.courses)]
        genres += [book_genres(book_id=book.id, literarygenre_id=slug)
                   for slug in resolve_genres(book.subjects, book.cdd or "", book.authors, taxonomy.genres)]
    for model, rows in ((BookAuthor, authors), (book_subjects, subjects), (book_courses, courses),
                        (book_genres, genres)):
        model.objects.bulk_create(rows, batch_size=BATCH_SIZE)


# ---- registro das execuções
def _start_run(kind: SyncKind) -> SyncRun:
    """Registra o início, recusando se outra execução do mesmo tipo está em andamento."""
    with transaction.atomic():
        running = SyncRun.objects.filter(kind=kind, status=SyncStatus.RUNNING,
                                         started_at__gte=timezone.now() - STALE_RUN_AFTER).first()
        if running:
            raise SyncError("já há uma sincronização de %s em andamento (iniciada em %s)"
                            % (kind.label.lower(), running.started_at))
        return SyncRun.objects.create(kind=kind)


def _finish_run(run: SyncRun, status: SyncStatus, stats: dict[str, int | float] | None = None,
                error: str = "") -> None:
    run.status, run.finished_at, run.error = status, timezone.now(), error
    if stats is not None:
        run.stats = stats
    run.save(update_fields=["status", "finished_at", "stats", "error"])

