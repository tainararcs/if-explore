"""Funções puras: texto, ISBN, URL e preparo de consultas."""

import datetime as dt
import unittest

from phl_client.isbn import isbn10_to_13, isbn13_to_10, isbn_digits, isbn_search_forms
from phl_client.query import clean_query, parse_catalog_url, require_expression
from phl_client.text import clean_text, first_int, parse_date, text_list, to_plain


class TextTests(unittest.TestCase):
    def test_clean_text_collapses_spaces_and_joins_lists(self) -> None:
        self.assertEqual(clean_text("São   Paulo "), "São Paulo")
        self.assertEqual(clean_text(["a", "", "b"]), "a / b")
        self.assertIsNone(clean_text("   "))
        self.assertIsNone(clean_text(None))

    def test_text_list_always_returns_list(self) -> None:
        self.assertEqual(text_list(None), [])
        self.assertEqual(text_list("x  y"), ["x y"])
        self.assertEqual(text_list(["a", " ", "b"]), ["a", "b"])

    def test_first_int(self) -> None:
        self.assertEqual(first_int("505 p."), 505)
        self.assertIsNone(first_int("[s.n.]"))

    def test_to_plain_uses_link_urls(self) -> None:
        self.assertEqual(to_plain(["a", "b"]), "a; b")
        self.assertEqual(to_plain([{"label": "TCC", "url": "https://x/a.pdf"}]), "https://x/a.pdf")
        self.assertEqual(to_plain(3), 3)

    def test_parse_date_formats(self) -> None:
        self.assertEqual(parse_date("2026-09-01", "since"), dt.date(2026, 9, 1))
        self.assertEqual(parse_date("01/09/2026", "since"), dt.date(2026, 9, 1))
        with self.assertRaisesRegex(ValueError, "since"):
            parse_date("setembro", "since")


class IsbnTests(unittest.TestCase):
    def test_conversions(self) -> None:
        self.assertEqual(isbn_digits("978-85-7608-384-9"), "9788576083849")
        self.assertEqual(isbn10_to_13("8576083841"), "9788576083849")
        self.assertEqual(isbn13_to_10("9788576083849"), "8576083841")
        self.assertIsNone(isbn13_to_10("9798576083840"))

    def test_search_forms_cover_both_lengths_and_the_cataloged_hyphenation(self) -> None:
        forms, targets = isbn_search_forms("8576083841")
        self.assertEqual(targets, {"9788576083849", "8576083841"})
        self.assertIn("978-85-7608-384-9", forms)
        self.assertIn("85-7608-384-1", forms)


class QueryTests(unittest.TestCase):
    def test_parse_site_only_url(self) -> None:
        info = parse_catalog_url("biblioteca.x.br")
        self.assertEqual(info["cgi"], "https://biblioteca.x.br/cgi-bin/wxis.exe")
        self.assertIsNone(info["script_dir"])
        self.assertIsNone(info["cipar"])

    def test_parse_full_browser_url(self) -> None:
        info = parse_catalog_url("https://x.br/cgi-bin/wxis.exe?IsisScript=phl82.xis&cipar=phl82.cip&lang=por")
        self.assertEqual((info["script_dir"], info["cipar"], info["lang"]), ("phl82", "phl82.cip", "por"))

    def test_parse_rejects_invalid_urls(self) -> None:
        for url in ("", "ftp://x.br"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                parse_catalog_url(url)

    def test_clean_query(self) -> None:
        cases = {
            "Fowler, Martin": "Fowler Martin",
            "agro*": "agro$",
            "“aspas” — travessão": "aspas travessão",
            "ASP.NET C# D'Imperio": "ASP.NET C# D'Imperio",
            "$ ** x": "x",
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(clean_query(raw, "and"), expected)

    def test_clean_query_keeps_operators_in_expression_mode(self) -> None:
        self.assertEqual(clean_query("PYTHON + JAVA", "exp"), "PYTHON + JAVA")

    def test_require_expression_blocks_empty_and_huge(self) -> None:
        for expression in (None, "", "   ", "x" * 4001):
            with self.subTest(length=len(expression or "")), self.assertRaises(ValueError):
                require_expression(expression)
        self.assertEqual(require_expression("$"), "$")


if __name__ == "__main__":
    unittest.main()
