"""Modelos e fachada, com o servidor substituído por páginas salvas."""

import csv
import datetime as dt
import json
import tempfile
import unittest
from collections.abc import Callable, Mapping
from pathlib import Path

from phl_client import Book, Copy, Library, SearchResult
from phl_client.fields import Record
from phl_client.parsers import parse_copies, parse_records

from . import BASE_URL, fixture


def tcc_book() -> Book:
    return Book.from_record(parse_records(fixture("export_tcc.html"), BASE_URL)[0])


class FakeServerLibrary(Library):
    """Library cujo cliente responde com fixtures em vez de ir à rede."""

    def __init__(self) -> None:
        super().__init__(BASE_URL, connect=False, pause=0)
        self.phl.script_dir, self.phl.session = "phl82", "/tmp/fileTEST"
        self.requests: list[Mapping[str, str | None]] = []
        self.phl.request = self._respond  # type: ignore[method-assign]

    def _respond(self, params: Mapping[str, str | None]) -> str:
        self.requests.append(params)
        pages = {"decorado": "decorated.html", "phl": "export.html", "status_tit": "status_on_loan.html",
                 "referencia": "reference.html"}
        return fixture(pages[str(params["opc"])])


class BookTests(unittest.TestCase):
    def test_from_record_book(self) -> None:
        book = Book.from_record(parse_records(fixture("export.html"), BASE_URL)[0])
        self.assertEqual(book.id, "102231235013")
        self.assertEqual(book.full_title, "Programação em Python 3: uma introdução completa à linguagem python")
        self.assertEqual(book.authors, ["SUMMERFIELD, Mark"])
        self.assertEqual(book.contributors, "Trad. por: Fabiane Fiorini")
        self.assertEqual((book.year, book.pages, book.isbn), (2009, 505, "9788576083849"))
        self.assertEqual(book.call_number, "005.13 S955p")
        self.assertEqual(book.area, "Engenharias")
        self.assertEqual(book.bibliographic_level, "monograph")
        self.assertEqual(book.course_codes, ["24", "117"])
        self.assertEqual(book.cataloged_at, dt.date(2011, 2, 23))
        self.assertTrue(book.synopsis and book.synopsis.startswith("Rápida introdução"))

    def test_tcc_links_and_notes(self) -> None:
        book = tcc_book()
        self.assertEqual(book.tcc_course, "Nutrição")
        self.assertEqual(len(book.links), 1)
        self.assertEqual(book.links[0]["label"], "TCC")
        # rótulo de link quebrado não vira nota
        self.assertEqual(book.notes, [])

    def test_staff_note_without_link_becomes_note(self) -> None:
        record: Record = {"title_id": "1", "title": "X", "general_notes": "Acompanha 01 CD",
                          "authorization_document": "NÃO POSSUI IMAGEM!"}
        self.assertEqual(Book.from_record(record).notes, ["Acompanha 01 CD", "NÃO POSSUI IMAGEM!"])

    def test_course_codes_drop_typed_text(self) -> None:
        record: Record = {"title_id": "1", "title": "X", "course": ["24", "LINGUAGEM DE PROGRAMAÇÃO", "07"]}
        self.assertEqual(Book.from_record(record).course_codes, ["24", "07"])

    def test_impossible_entry_date_is_none(self) -> None:
        record: Record = {"title_id": "1", "title": "X", "standardized_date": "20111131"}
        self.assertIsNone(Book.from_record(record).cataloged_at)

    def test_placeholder_cover_is_no_cover(self) -> None:
        placeholder: Record = {"title_id": "1", "title": "X",
                               "cover_image": BASE_URL + "/phl82/img/capas/Capas_Livros_25/z.jpg"}
        self.assertIsNone(Book.from_record(placeholder).cover_url)
        real: Record = {"title_id": "1", "title": "X", "cover_image": BASE_URL + "/phl82/img/capas/x/998.jpg"}
        self.assertEqual(Book.from_record(real).cover_url, real["cover_image"])

    def test_to_dict_is_json_ready(self) -> None:
        data = tcc_book().to_dict()
        self.assertNotIn("raw", data)
        self.assertEqual(data["cataloged_at"], None)
        json.dumps(data)

    def test_network_properties_need_a_library(self) -> None:
        with self.assertRaises(RuntimeError):
            _ = tcc_book().copies


class CopyTests(unittest.TestCase):
    def test_from_row(self) -> None:
        available, on_loan = (Copy.from_row(row) for row in parse_copies(fixture("status_on_loan.html")))
        self.assertTrue(available.is_available)
        self.assertEqual((on_loan.status, on_loan.due_date, on_loan.loans, on_loan.note),
                         ("on_loan", dt.date(2026, 11, 5), 7, "Capa danificada"))
        self.assertIn("devolução 05/11/2026", str(on_loan))


class SearchResultTests(unittest.TestCase):
    def test_markdown_and_unknown_column(self) -> None:
        result = SearchResult([tcc_book()])
        table = result.to_markdown(("title", "links"), width=20)
        self.assertIn("| 1 | Comparação dos efei… | https://biblioteca.… |", table)
        with self.assertRaises(ValueError):
            SearchResult().to_markdown(("titulo",))

    def test_save_csv_and_json(self) -> None:
        result = SearchResult([tcc_book()])
        with tempfile.TemporaryDirectory() as folder:
            with result.save(Path(folder) / "r.csv").open(encoding="utf-8-sig") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(rows[0]["authors"], "CARVALHO, Ana Paula de Abreu; MELO, Janessandra Maria de")
            self.assertEqual(json.loads((result.save(Path(folder) / "r.json")).read_text("utf-8"))[0]["id"],
                             "8121210140072")
            with self.assertRaises(ValueError):
                result.save(Path(folder) / "r.txt")


class LibraryTests(unittest.TestCase):
    def test_single_criterion_search_is_truncated_by_limit(self) -> None:
        library = FakeServerLibrary()
        result = library.search(title="python", limit=5)
        self.assertEqual((len(result), result.total, result.truncated), (5, 13, True))
        self.assertEqual(library.requests[0]["tag"], "12,13,18,19,25,30,34,181,182")
        self.assertEqual(library.requests[1]["rpp"], "5")

    def test_network_properties_use_the_library(self) -> None:
        book = FakeServerLibrary().search(title="python", limit=1)[0]
        self.assertEqual((len(book.copies), book.available_count, book.loans), (2, 1, 9))
        self.assertTrue(book.is_available)
        self.assertTrue(book.to_dict(include_copies=True)["copies"])

    def test_argument_validation_happens_before_the_network(self) -> None:
        library = FakeServerLibrary()
        invalid_calls: list[Callable[[], object]] = [
            lambda: library.search(),
            lambda: library.search(title="python", limit=0),
            lambda: library.search(title="  ,; "),
            lambda: library.search(isbn="123"),
            lambda: library.search(year=(1990, "2000")),  # type: ignore[arg-type]
            lambda: library.search(year=3000),
            lambda: library.search(area="ciencias"),
            lambda: library.search(document_type="livro"),
            lambda: library.search(classification="005;drop"),
            lambda: library.book(),
            lambda: library.book("1", isbn="8576083841"),
            lambda: library.book("a b"),
            lambda: library.new_arrivals(until="2026-01-01"),
            lambda: library.new_arrivals("2026-02-01", "2026-01-01"),
        ]
        for index, call in enumerate(invalid_calls):
            with self.subTest(call=index), self.assertRaises(ValueError):
                call()
        self.assertEqual(library.requests, [])

    def test_choice_helpers(self) -> None:
        self.assertEqual(Library._choose("engenharias", {"3": "Engenharias"}, "área"), "3")
        self.assertEqual(Library._choose("saude", {"4": "Ciências da Saúde"}, "área"), "4")
        self.assertEqual(Library._document_type("Personal computer"), "personal_computer")
        self.assertEqual(Library._document_type("e-book"), "ebook")


if __name__ == "__main__":
    unittest.main()
