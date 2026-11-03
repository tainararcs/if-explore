"""Regras de área, curso e gênero (funções puras, sem banco)."""

from unittest import TestCase

from catalog.services.classification import (
    CourseRule,
    GenreRule,
    cdd_digits,
    resolve_area,
    resolve_courses,
    resolve_genres,
)

CNPQ = {"1": "exact-sciences", "3": "technology", "4": "health-sciences", "6": "applied-social-sciences",
        "8": "languages-arts"}


class AreaTests(TestCase):
    def test_cdd_digits_drops_brazilian_prefix(self) -> None:
        self.assertEqual(cdd_digits("B869.3"), "8693")
        self.assertEqual(cdd_digits("005.133 PYTHON"), "005133")
        self.assertEqual(cdd_digits(""), "")

    def test_computing_cdd_wins_over_cnpq(self) -> None:
        self.assertEqual(resolve_area("6", "005.13", CNPQ), "technology")

    def test_cnpq_code_when_cdd_is_not_computing(self) -> None:
        self.assertEqual(resolve_area("4", "613.2", CNPQ), "health-sciences")

    def test_cdd_fallback_without_useful_cnpq(self) -> None:
        cases = {"B869.3": "languages-arts", "641.5": "health-sciences", "664.02": "agricultural-sciences",
                 "796.33": "health-sciences", "370.1": "humanities", "574": "biological-sciences",
                 "510": "exact-sciences"}
        for cdd, area in cases.items():
            with self.subTest(cdd=cdd):
                self.assertEqual(resolve_area("9", cdd, CNPQ), area)

    def test_no_data_means_no_area(self) -> None:
        self.assertIsNone(resolve_area("", "", CNPQ))


class CourseTests(TestCase):
    RULES = (
        CourseRule("internet-systems", frozenset({"24"}), frozenset()),
        CourseRule("it-technician", frozenset({"7", "07"}), frozenset()),
        CourseRule("nutrition", frozenset({"92"}), frozenset({"nutricao"})),
    )

    def test_by_phl_code(self) -> None:
        self.assertEqual(resolve_courses(["24", "07"], "", self.RULES), ["internet-systems", "it-technician"])

    def test_by_tcc_course_ignoring_accents_and_case(self) -> None:
        self.assertEqual(resolve_courses([], " NUTRIÇÃO ", self.RULES), ["nutrition"])

    def test_unknown_codes(self) -> None:
        self.assertEqual(resolve_courses(["4"], "", self.RULES), [])


class GenreTests(TestCase):
    RULES = (
        GenreRule("romance", ("romance",), (), ()),
        GenreRule("biography", ("biografia", "memorias"), ("92",), ()),
        GenreRule("comics", ("quadrinhos",), ("741.5",), ()),
        GenreRule("short-stories", ("conto",), (), ()),
        GenreRule("brazilian-classics", (), ("B869",), ("assis, machado",)),
    )

    def test_subject_keyword_in_literary_cdd(self) -> None:
        self.assertEqual(resolve_genres(["ROMANCE AMERICANO"], "813", [], self.RULES), ["romance"])

    def test_keyword_matches_word_start_only(self) -> None:
        self.assertEqual(resolve_genres(["CONTOS"], "B869.3", [], self.RULES), ["short-stories"])
        self.assertEqual(resolve_genres(["DESCONTOS"], "B869.3", [], self.RULES), [])

    def test_subject_keyword_ignored_outside_literature(self) -> None:
        self.assertEqual(resolve_genres(["MEMÓRIAS"], "004.5", [], self.RULES), [])

    def test_cdd_prefix_works_outside_literature(self) -> None:
        self.assertEqual(resolve_genres([], "741.5", [], self.RULES), ["comics"])
        self.assertEqual(resolve_genres([], "920.71", [], self.RULES), ["biography"])

    def test_author_condition(self) -> None:
        self.assertIn("brazilian-classics", resolve_genres([], "B869.3", ["ASSIS, Machado de"], self.RULES))
        self.assertNotIn("brazilian-classics", resolve_genres([], "B869.3", ["SILVA, Ana"], self.RULES))
