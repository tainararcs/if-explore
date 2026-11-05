"""Sincronização e índice de busca, com o PHL substituído por páginas salvas."""

import datetime as dt
from collections.abc import Iterator

from django.test import TestCase
from django.utils import timezone

from catalog.models import Author, Book, CopyStatus, SyncKind, SyncRun, SyncStatus
from catalog.services import search_index
from catalog.services.availability import refresh_copies
from catalog.services.sync import SyncError, apply_snapshot, sync_catalog
from phl_client import Library, LibraryError
from phl_client.fields import Record
from phl_client.parsers import CopyRow, CopyStatusItem, parse_copies, parse_records
from phl_client.tests import BASE_URL, fixture

PYTHON_BOOK, DJANGO_BOOK, TCC = "102231235013", "103020853083", "8121210140072"


def snapshot_records() -> list[Record]:
    """Os 9 títulos das páginas salvas: 5 de informática, 1 TCC e 3 fascículos."""
    return [record for name in ("export.html", "export_tcc.html", "export_serial.html")
            for record in parse_records(fixture(name), BASE_URL)]


def status_items() -> list[CopyStatusItem]:
    """Situação em lote dos títulos do snapshot. O TCC fica de fora, como os títulos
    sem exemplar no formato decorado."""
    def item(mfn: int, title_id: str | None, total: int, statuses: list[str]) -> CopyStatusItem:
        return {"mfn": mfn, "title_id": title_id, "total": total, "statuses": statuses}

    ids = [str(record["title_id"]) for record in snapshot_records()]
    others = [item(i, title_id, 1, ["unavailable"]) for i, title_id in enumerate(ids)
              if title_id not in (PYTHON_BOOK, DJANGO_BOOK, TCC)]
    return [item(100, PYTHON_BOOK, 3, ["available", "on_loan"]), item(101, DJANGO_BOOK, 2, ["available"]),
            item(102, None, 0, []), *others]


class FakeLibrary(Library):
    """Library que responde com páginas salvas e registra os títulos consultados."""

    def __init__(self, failing: dict[str, Exception] | None = None) -> None:
        super().__init__(BASE_URL, connect=False, pause=0)
        self.failing = failing or {}
        self.checked: list[str] = []
        self.phl.search_all = self._search_all  # type: ignore[method-assign]
        self.phl.copy_statuses = self._copy_statuses  # type: ignore[method-assign]
        self.phl.copies = self._copies  # type: ignore[method-assign]

    def _search_all(self, *args: object, **kwargs: object) -> Iterator[Record]:
        yield from snapshot_records()

    def _copy_statuses(self, *args: object, **kwargs: object) -> Iterator[CopyStatusItem]:
        if "copy_statuses" in self.failing:
            raise self.failing["copy_statuses"]
        yield from status_items()

    def _copies(self, title_id: str, *args: object, **kwargs: object) -> list[CopyRow]:
        self.checked.append(title_id)
        if title_id in self.failing:
            raise self.failing[title_id]
        return parse_copies(fixture("status_on_loan.html"))


class SnapshotTests(TestCase):
    def setUp(self) -> None:
        self.stats = apply_snapshot(snapshot_records(), min_ratio=0.9)

    def test_creates_books_with_derived_taxonomy(self) -> None:
        self.assertEqual(self.stats["created"], 9)
        book = Book.objects.get(id=PYTHON_BOOK)
        self.assertEqual(book.title, "Programação em Python 3")
        self.assertEqual(book.area_id, "technology")
        self.assertEqual(set(book.courses.values_list("slug", flat=True)), {"internet-systems", "information-systems"})
        self.assertEqual(book.call_number, "005.13 S955p")
        tcc = Book.objects.get(id=TCC)
        self.assertEqual(tcc.area_id, "health-sciences")
        self.assertEqual(list(tcc.courses.values_list("slug", flat=True)), ["nutrition"])
        self.assertEqual(tcc.links[0]["label"], "TCC")
        self.assertIsNone(Book.objects.get(id="8040720094815").area)

    def test_authors_keep_order_and_are_shared(self) -> None:
        tcc = Book.objects.get(id=TCC)
        self.assertEqual([a.name for a in tcc.authors.order_by("bookauthor__position")],
                         ["CARVALHO, Ana Paula de Abreu", "MELO, Janessandra Maria de"])
        deitel = Author.objects.get(normalized_name="deitel, h. m")
        self.assertEqual(deitel.books.count(), 1)

    def test_search_index_is_accent_insensitive_and_ranked(self) -> None:
        self.assertEqual(self.stats["indexed"], 9)
        self.assertEqual(search_index.ranked_ids("programacao python")[0], PYTHON_BOOK)
        self.assertEqual(search_index.ranked_ids("óleo CARTAMO"), [TCC])
        self.assertEqual(search_index.ranked_ids("djang"), [DJANGO_BOOK])
        self.assertEqual(search_index.ranked_ids('"; DROP TABLE x --'), [])

    def test_resync_keeps_copies_and_deactivates_missing(self) -> None:
        Book.objects.filter(id=PYTHON_BOOK).update(copies_total=3, copies_available=1, loans_total=40)
        later = timezone.now() + dt.timedelta(days=1)
        records = [r for r in snapshot_records() if r["title_id"] != DJANGO_BOOK]
        stats = apply_snapshot(records, min_ratio=0.8, now=later)
        self.assertEqual((stats["created"], stats["deactivated"]), (0, 1))
        self.assertFalse(Book.objects.get(id=DJANGO_BOOK).is_active)
        python = Book.objects.get(id=PYTHON_BOOK)
        self.assertEqual((python.copies_total, python.loans_total, python.synced_at), (3, 40, later))
        self.assertNotIn(DJANGO_BOOK, search_index.ranked_ids("python"))

    def test_batch_statuses(self) -> None:
        stats = apply_snapshot(snapshot_records(), status_items(), min_ratio=0.9)
        self.assertEqual((stats["available"], stats["uncertain"], stats["no_copies"]), (1, 1, 1))
        python, django, tcc = (Book.objects.get(id=i) for i in (PYTHON_BOOK, DJANGO_BOOK, TCC))
        self.assertEqual((python.copies_total, python.copy_statuses, python.copy_status),
                         (3, ["available", "on_loan"], CopyStatus.UNCERTAIN))
        self.assertEqual((django.copy_status, django.copies_total), (CopyStatus.AVAILABLE, 2))
        # ausente da leitura em lote: o decorado omite o código dos títulos sem exemplar
        self.assertEqual((tcc.copy_status, tcc.copies_total, tcc.copy_statuses), (CopyStatus.NO_COPIES, 0, []))
        self.assertIsNotNone(python.copies_synced_at)

    def test_batch_keeps_live_counts(self) -> None:
        Book.objects.filter(id=PYTHON_BOOK).update(copies_available=1, loans_total=40,
                                                   copies_checked_at=timezone.now())
        apply_snapshot(snapshot_records(), status_items(), min_ratio=0.9)
        python = Book.objects.get(id=PYTHON_BOOK)
        self.assertEqual((python.copies_available, python.loans_total), (1, 40))
        self.assertIsNotNone(python.copies_checked_at)

    def test_truncated_statuses_are_refused(self) -> None:
        with self.assertRaises(SyncError):
            apply_snapshot(snapshot_records(), status_items()[:3], min_ratio=0.9)
        self.assertEqual(Book.objects.exclude(copy_status="").count(), 0)

    def test_truncated_snapshot_is_refused(self) -> None:
        with self.assertRaises(SyncError):
            apply_snapshot(snapshot_records()[:2], min_ratio=0.9)
        self.assertEqual(Book.objects.filter(is_active=True).count(), 9)


class SyncRunTests(TestCase):
    def test_sync_catalog_records_the_run(self) -> None:
        run = sync_catalog(FakeLibrary())
        self.assertEqual((run.kind, run.status, run.stats["books"]), (SyncKind.CATALOG, SyncStatus.SUCCESS, 9))
        self.assertEqual(Book.objects.get(id=DJANGO_BOOK).copy_status, CopyStatus.AVAILABLE)

    def test_status_failure_applies_nothing(self) -> None:
        library = FakeLibrary({"copy_statuses": LibraryError("situação dos exemplares cortada")})
        with self.assertRaises(LibraryError):
            sync_catalog(library)
        self.assertEqual(Book.objects.count(), 0)
        self.assertEqual(SyncRun.objects.get().status, SyncStatus.FAILED)

    def test_concurrent_run_is_refused(self) -> None:
        SyncRun.objects.create(kind=SyncKind.CATALOG)
        with self.assertRaises(SyncError):
            sync_catalog(FakeLibrary())


class LiveCopiesTests(TestCase):
    def setUp(self) -> None:
        apply_snapshot(snapshot_records(), status_items(), min_ratio=0.9)

    def test_refresh_copies_stores_exact_counts(self) -> None:
        library = FakeLibrary()
        summary = refresh_copies(library, PYTHON_BOOK)
        self.assertEqual(library.checked, [PYTHON_BOOK])
        self.assertEqual((summary.total, summary.available, summary.loans), (2, 1, 9))
        book = Book.objects.get(id=PYTHON_BOOK)
        self.assertEqual((book.copies_total, book.copies_available, book.loans_total), (2, 1, 9))
        # o lote dizia "incerta"; a tela de exemplares resolve
        self.assertEqual((book.copy_status, book.copy_statuses), (CopyStatus.AVAILABLE, ["available", "on_loan"]))
        self.assertIsNotNone(book.copies_checked_at)
