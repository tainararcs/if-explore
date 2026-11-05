"""Conversão de páginas reais do OPAC em registros, exemplares e referências."""

import unittest

from phl_client.errors import LibraryError
from phl_client.fields import Record
from phl_client.parsers import (
    fill_title_author,
    normalize_year,
    parse_copies,
    parse_copy_statuses,
    parse_records,
    parse_references,
)

from . import BASE_URL, fixture


class ParseRecordsTests(unittest.TestCase):
    def test_book_record_fields(self) -> None:
        records = parse_records(fixture("export.html"), BASE_URL)
        self.assertEqual(len(records), 5)
        book = records[0]
        self.assertEqual(book["title_id"], "102231235013")
        self.assertEqual(book["title"], "Programação em Python 3")
        self.assertEqual(book["subjects"], ["LINGUAGEM DE PROGRAMAÇÃO", "PYTHON"])
        self.assertEqual(book["course"], ["24", "117"])
        self.assertEqual(book["year_number"], 2009)
        cover = book["cover_image"]
        self.assertIsInstance(cover, str)
        self.assertTrue(str(cover).startswith(BASE_URL + "/phl82/img/capas/"))

    def test_link_fields_keep_the_url_over_https(self) -> None:
        record = parse_records(fixture("export_tcc.html"), BASE_URL)[0]
        self.assertEqual(record["document"], "TCC (Clique aqui)")
        url = str(record["document_url"])
        self.assertTrue(url.startswith(BASE_URL + "/phl82/img/tccs/TCC%20002_"))
        self.assertTrue(url.endswith(".pdf"))
        self.assertEqual(record["tcc_course"], "Nutrição")
        # o termo de autorização deste TCC tem o href quebrado: fica só o texto
        self.assertNotIn("authorization_document_url", record)
        self.assertEqual(record["authorization_document"], "Termo de Autorização")

    def test_serial_issue_fields(self) -> None:
        records = parse_records(fixture("export_serial.html"), BASE_URL)
        self.assertEqual([r["bibliographic_level"] for r in records], ["s", "s", "s"])
        self.assertTrue(all(r.get("title") for r in records))

    def test_page_without_records(self) -> None:
        self.assertEqual(parse_records("<html>nada</html>", BASE_URL), [])


class RecordNormalizationTests(unittest.TestCase):
    def test_year_number_from_free_text(self) -> None:
        cases = {"[s.d.]": None, "jan.2014": 2014, "2019/2020": 2019, "20110000": 2011,
                 "[19..]": None, "1983": 1983}
        for text, expected in cases.items():
            record: Record = {"year": text}
            normalize_year(record)
            with self.subTest(text=text):
                self.assertEqual(record["year_number"], expected)

    def test_title_and_author_fallbacks_for_articles(self) -> None:
        record: Record = {"part_title": "Um artigo", "part_author": ["SILVA, A."]}
        fill_title_author(record)
        self.assertEqual(record["title"], "Um artigo")
        self.assertEqual(record["author"], ["SILVA, A."])


class ParseCopiesTests(unittest.TestCase):
    def test_available_copy(self) -> None:
        self.assertEqual(parse_copies(fixture("status.html")), [{
            "accession_number": "14665", "note": "", "label": "005.13 / S955p/37729",
            "status": "available", "due_date": "", "loans": "2", "renewals": "1"}])

    def test_borrower_only_on_request(self) -> None:
        page = fixture("status_on_loan.html")
        hidden, shown = parse_copies(page), parse_copies(page, include_borrower=True)
        self.assertEqual([c["status"] for c in hidden], ["available", "on_loan"])
        self.assertNotIn("borrower", hidden[1])
        self.assertEqual(shown[1]["borrower"], "0000000")
        self.assertEqual(hidden[1]["due_date"], "05/11/2026")


class ParseCopyStatusesTests(unittest.TestCase):
    def test_statuses_and_totals_per_title(self) -> None:
        total, items, fatal_error = parse_copy_statuses(fixture("decorated_statuses.html"))
        self.assertEqual((total, fatal_error), (8, False))
        by_title = {item["title_id"]: (item["total"], item["statuses"]) for item in items}
        self.assertEqual(by_title, {
            "000002": (1, ["available"]),
            "000007": (1, ["in_library_use"]),
            "000038": (1, ["unavailable"]),
            None: (0, []),
            # um só exemplar, emprestado: o OPAC mostra 003 e também 002
            "000673": (1, ["available", "on_loan"]),
            "004120": (1, ["on_loan", "unavailable"]),
            "004366": (4, ["available", "on_loan", "in_library_use", "unavailable"]),
            "4092610290646": (1, ["available", "on_loan", "reserved"]),
        })
        self.assertEqual(items[3]["mfn"], 342)

    def test_title_with_copies_but_no_code_raises(self) -> None:
        page = 'name="sel" value="MFN=1"> Selecionar&nbsp;<img src="/phl82/img/002.gif">&nbsp; [1] </td>'
        with self.assertRaises(LibraryError):
            parse_copy_statuses(page)

    def test_page_without_titles(self) -> None:
        self.assertEqual(parse_copy_statuses("<html>nada</html>"), (None, [], False))

    def test_page_interrupted_by_a_fatal_error(self) -> None:
        page = fixture("decorated_statuses.html").split("<!-- FMX000090 -->")[0]
        cut = page[:page.index('value="MFN=657"')].rsplit("<table", 1)[0]
        total, items, fatal_error = parse_copy_statuses(cut + "\n\nWXIS|fatal error|unavoidable|dbxopen: _tbo.cnt (2)|\n")
        self.assertEqual((total, len(items), fatal_error), (8, 4, True))


class ParseReferencesTests(unittest.TestCase):
    def test_reference_items(self) -> None:
        total, items = parse_references(fixture("reference.html"))
        self.assertEqual(total, 13)
        self.assertEqual(items[0]["mfn"], 43862)
        self.assertEqual(items[0]["title"], "Programação em Python 3")
        self.assertTrue(items[0]["reference"].startswith("SUMMERFIELD, Mark. Programação em Python 3:"))
        self.assertEqual(items[0]["approx_copies"], 1)

    def test_corrupted_item_raises(self) -> None:
        with self.assertRaises(LibraryError):
            parse_references("<hits>1</hits><reg><ref>sem mfn</ref></reg>")


if __name__ == "__main__":
    unittest.main()
