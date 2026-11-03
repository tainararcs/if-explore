"""Rotas da API com o acervo das páginas salvas. O PHL nunca é acessado: a
disponibilidade ao vivo usa uma Library falsa."""

import datetime as dt
import json
from typing import Any
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from catalog.models import Book
from catalog.services.sync import apply_snapshot
from phl_client import LibraryConnectionError

from .test_sync import DJANGO_BOOK, PYTHON_BOOK, TCC, FakeLibrary, snapshot_records

SERIAL = "8040720094815"


class ApiTestCase(TestCase):
    def setUp(self) -> None:
        apply_snapshot(snapshot_records(), min_ratio=0.9)
        self.library = FakeLibrary()
        live = patch("catalog.services.availability.live_library", return_value=self.library)
        live.start()
        self.addCleanup(live.stop)

    def get(self, url: str, status: int = 200) -> Any:
        response = self.client.get(url, HTTP_HOST="localhost")
        self.assertEqual(response.status_code, status, response.content)
        return response.json()

    def post(self, url: str, body: dict[str, object], status: int = 200) -> Any:
        response = self.client.post(url, json.dumps(body), content_type="application/json", HTTP_HOST="localhost")
        self.assertEqual(response.status_code, status, response.content)
        return response.json()


class TaxonomyTests(ApiTestCase):
    def test_lists(self) -> None:
        areas, courses, genres = self.get("/api/areas"), self.get("/api/courses"), self.get("/api/genres")
        self.assertEqual((len(areas), len(courses), len(genres)), (8, 25, 12))
        self.assertEqual(areas[0], {"id": "exact-sciences", "name": "Ciências Exatas e da Terra"})
        nutrition = next(course for course in courses if course["id"] == "nutrition")
        self.assertEqual(nutrition, {"id": "nutrition", "name": "Bacharelado em Nutrição",
                                     "areaId": "health-sciences", "level": "undergraduate"})


class BookListTests(ApiTestCase):
    def test_text_search_with_camel_case_contract(self) -> None:
        page = self.get("/api/books?q=programacao%20python")
        self.assertEqual(page["items"][0]["id"], PYTHON_BOOK)
        self.assertEqual((page["page"], page["pageSize"]), (1, 24))
        book = page["items"][0]
        self.assertEqual(book["callNumber"], "005.13 S955p")
        self.assertEqual(book["areaId"], "technology")
        self.assertCountEqual(book["courseIds"], ["internet-systems", "information-systems"])
        self.assertIsNone(book["copies"])
        self.assertNotIn("links", book)

    def test_filters(self) -> None:
        self.assertEqual([b["id"] for b in self.get("/api/books?course=nutrition")["items"]], [TCC])
        self.assertEqual([b["id"] for b in self.get("/api/books?type=thesis")["items"]], [TCC])
        self.assertEqual(self.get("/api/books?area=technology")["total"], 5)
        self.assertEqual(self.get("/api/books?area=technology&area=health-sciences")["total"], 6)
        self.assertEqual(self.get("/api/books?q=python&area=health-sciences")["total"], 0)
        Book.objects.filter(id=DJANGO_BOOK).update(copies_total=2, copies_available=1)
        self.assertEqual([b["id"] for b in self.get("/api/books?available=true")["items"]], [DJANGO_BOOK])

    def test_preferred_area_comes_first(self) -> None:
        page = self.get("/api/books?sort=title&preferArea=health-sciences")
        self.assertEqual(page["items"][0]["id"], TCC)
        self.assertEqual(page["total"], 9)

    def test_pagination(self) -> None:
        first = self.get("/api/books?sort=title&pageSize=5")
        second = self.get("/api/books?sort=title&pageSize=5&page=2")
        self.assertEqual((len(first["items"]), len(second["items"]), first["total"]), (5, 4, 9))
        self.assertFalse({b["id"] for b in first["items"]} & {b["id"] for b in second["items"]})

    def test_ids_keep_order_and_skip_unknown(self) -> None:
        page = self.get("/api/books?ids=%s&ids=naoexiste&ids=%s" % (TCC, PYTHON_BOOK))
        self.assertEqual([b["id"] for b in page["items"]], [TCC, PYTHON_BOOK])

    def test_invalid_parameters(self) -> None:
        self.get("/api/books?pageSize=500", status=422)
        self.get("/api/books?type=livro", status=422)
        self.get("/api/books?sort=random", status=422)
        self.get("/api/books?" + "&".join("ids=%d" % i for i in range(61)), status=422)

    def test_search_text_is_not_fts_syntax(self) -> None:
        self.assertEqual(self.get('/api/books?q=%22python%22%20OR%20NEAR(')["total"], 0)


class BookDetailTests(ApiTestCase):
    def test_detail_refreshes_stale_copies(self) -> None:
        book = self.get("/api/books/%s" % PYTHON_BOOK)
        self.assertEqual(self.library.checked, [PYTHON_BOOK])
        self.assertEqual((book["copies"]["total"], book["copies"]["available"], book["loans"]), (2, 1, 9))
        self.assertEqual(book["contributors"], "Trad. por: Fabiane Fiorini")
        self.get("/api/books/%s" % PYTHON_BOOK)
        self.assertEqual(self.library.checked, [PYTHON_BOOK])  # ainda fresco: não consulta de novo

    def test_old_copies_are_refreshed(self) -> None:
        Book.objects.filter(id=PYTHON_BOOK).update(copies_total=1, copies_available=0,
                                                   copies_checked_at=timezone.now() - dt.timedelta(hours=1))
        self.assertEqual(self.get("/api/books/%s" % PYTHON_BOOK)["copies"]["available"], 1)

    def test_phl_failure_keeps_stored_data(self) -> None:
        self.library.failing[TCC] = LibraryConnectionError("fora do ar")
        with self.assertLogs("catalog.services.availability", "WARNING"):
            book = self.get("/api/books/%s" % TCC)
        self.assertIsNone(book["copies"])
        self.assertEqual(book["links"][0]["label"], "TCC")
        self.assertEqual(book["tccCourse"], "Nutrição")

    def test_missing_and_inactive_books(self) -> None:
        self.get("/api/books/naoexiste", status=404)
        Book.objects.filter(id=PYTHON_BOOK).update(is_active=False)
        self.get("/api/books/%s" % PYTHON_BOOK, status=404)
        self.assertNotIn(PYTHON_BOOK, [b["id"] for b in self.get("/api/books?q=python")["items"]])

    def test_related_by_shared_subjects(self) -> None:
        related = self.get("/api/books/%s/related" % PYTHON_BOOK)
        ids = [b["id"] for b in related["related"]]
        self.assertEqual(ids[0], DJANGO_BOOK)
        self.assertNotIn(PYTHON_BOOK, ids)
        self.assertNotIn(SERIAL, ids)
        self.assertIsNone(related["sameAuthor"])


class RecommendationTests(ApiTestCase):
    def test_home_shelves(self) -> None:
        result = self.post("/api/recommendations", {"areaIds": ["technology"], "courseIds": ["internet-systems"],
                                                    "seedBookIds": [PYTHON_BOOK], "genreIds": ["romance"]})
        kinds = {shelf["id"]: shelf for shelf in result["shelves"]}
        # "porque você escolheu" fica de fora: só 2 livros compartilham assuntos com o
        # escolhido, e prateleiras com menos de 3 são descartadas; romance não tem livros.
        self.assertEqual(list(kinds), ["for-you", "area-technology"])
        self.assertEqual(kinds["area-technology"]["subject"], "Tecnologia e Computação")
        for shelf in result["shelves"]:
            ids = [book["id"] for book in shelf["books"]]
            self.assertGreaterEqual(len(ids), 3)
            self.assertNotIn(PYTHON_BOOK, ids)
            self.assertNotIn(SERIAL, ids)
        self.assertEqual(result["areas"], [{"id": "technology", "name": "Tecnologia e Computação"}])

    def test_unknown_ids_are_ignored(self) -> None:
        result = self.post("/api/recommendations", {"areaIds": ["nope"], "seedBookIds": ["nope"]})
        self.assertEqual(result, {"shelves": [], "areas": []})

    def test_profile_limits(self) -> None:
        self.post("/api/recommendations", {"seedBookIds": ["x"] * 21}, status=422)

    def test_onboarding_candidates(self) -> None:
        candidates = [b["id"] for b in self.get("/api/recommendations/candidates?course=nutrition&area=technology")]
        self.assertEqual(candidates[0], TCC)
        self.assertEqual(len(candidates), 6)
        # sem área nem curso, completa com os demais títulos recomendáveis
        self.assertEqual(len(self.get("/api/recommendations/candidates?limit=4")), 4)


class StatusTests(ApiTestCase):
    def test_status(self) -> None:
        status = self.get("/api/status")
        self.assertEqual((status["activeBooks"], status["booksWithCopies"]), (9, 0))
        self.assertIsNone(status["catalogSync"])  # apply_snapshot direto não registra execução
