"""Situação de um título para o visitante (funções puras, sem banco)."""

from unittest import TestCase

from catalog.models import CopyStatus
from catalog.services.copy_status import from_batch, from_copies
from phl_client.parsers import parse_copy_statuses
from phl_client.tests import fixture


class FromBatchTests(TestCase):
    def test_real_page(self) -> None:
        items = parse_copy_statuses(fixture("decorated_statuses.html")).items
        self.assertEqual({item["title_id"]: from_batch(item["statuses"], item["total"]) for item in items}, {
            "000002": CopyStatus.AVAILABLE,
            "000007": CopyStatus.IN_LIBRARY_USE,
            "000038": CopyStatus.UNAVAILABLE,
            None: CopyStatus.NO_COPIES,
            # 003 + 002 com um só exemplar: o "disponível" é o próprio exemplar emprestado
            "000673": CopyStatus.ON_LOAN,
            "004120": CopyStatus.ON_LOAN,
            # 4 exemplares, um emprestado: pode haver livre, ou não
            "004366": CopyStatus.UNCERTAIN,
            "4092610290646": CopyStatus.ON_LOAN,
        })

    def test_loan_with_several_copies_is_uncertain(self) -> None:
        self.assertEqual(from_batch(["available", "reserved"], 3), CopyStatus.UNCERTAIN)

    def test_title_the_phl_could_not_show_is_uncertain(self) -> None:
        self.assertEqual(from_batch(["unknown"], None), CopyStatus.UNCERTAIN)

    def test_library_use_wins_when_nothing_is_free(self) -> None:
        self.assertEqual(from_batch(["available", "on_loan", "in_library_use"], 1), CopyStatus.IN_LIBRARY_USE)


class FromCopiesTests(TestCase):
    def test_exact_statuses(self) -> None:
        cases = {
            (): CopyStatus.NO_COPIES,
            ("on_loan", "available"): CopyStatus.AVAILABLE,
            ("on_loan", "in_library_use"): CopyStatus.IN_LIBRARY_USE,
            ("on_loan", "unavailable"): CopyStatus.ON_LOAN,
            ("reserved",): CopyStatus.ON_LOAN,
            ("unavailable", "unknown"): CopyStatus.UNAVAILABLE,
        }
        for statuses, expected in cases.items():
            with self.subTest(statuses=statuses):
                self.assertEqual(from_copies(statuses), expected)
