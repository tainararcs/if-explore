"""Rotas da API com o acervo das páginas salvas. O PHL nunca é acessado: a
disponibilidade ao vivo usa uma Library falsa."""

import datetime as dt
import json
from typing import Any
from unittest.mock import patch

from django.db import OperationalError
from django.test import TestCase
from django.utils import timezone

from catalog.models import Book, CopyStatus
from catalog.services import recommendations
from catalog.services.sync import apply_snapshot
from phl_client import LibraryConnectionError

from .test_sync import DJANGO_BOOK, PYTHON_BOOK, TCC, FakeLibrary, snapshot_records, status_items

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
        self.assertEqual((len(areas), len(courses), len(genres)), (8, 25, 14))
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
        self.assertNotIn("loans", book)

    def test_batch_copies_in_cards(self) -> None:
        apply_snapshot(snapshot_records(), status_items(), min_ratio=0.9)
        items = {b["id"]: b for b in self.get("/api/books?sort=title")["items"]}
        self.assertEqual(items[PYTHON_BOOK]["copies"]["status"], "uncertain")
        self.assertEqual(items[DJANGO_BOOK]["copies"]["total"], 2)
        # a contagem exata de livres só vem da consulta ao vivo
        self.assertIsNone(items[DJANGO_BOOK]["copies"]["available"])
        self.assertEqual(items[TCC]["copies"], {"total": 0, "status": "no_copies", "available": None,
                                                "updatedAt": items[TCC]["copies"]["updatedAt"]})

    def test_popular_sorts_by_number_of_copies(self) -> None:
        apply_snapshot(snapshot_records(), status_items(), min_ratio=0.9)
        self.assertEqual([b["id"] for b in self.get("/api/books?pageSize=2")["items"]], [PYTHON_BOOK, DJANGO_BOOK])
        self.assertEqual([b["id"] for b in self.get("/api/books?q=python&sort=popular")["items"]][0], PYTHON_BOOK)

    def test_filters(self) -> None:
        self.assertEqual([b["id"] for b in self.get("/api/books?course=nutrition")["items"]], [TCC])
        self.assertEqual([b["id"] for b in self.get("/api/books?type=thesis")["items"]], [TCC])
        self.assertEqual(self.get("/api/books?area=technology")["total"], 5)
        self.assertEqual(self.get("/api/books?area=technology&area=health-sciences")["total"], 6)
        self.assertEqual(self.get("/api/books?q=python&area=health-sciences")["total"], 0)
        apply_snapshot(snapshot_records(), status_items(), min_ratio=0.9)
        self.assertEqual([b["id"] for b in self.get("/api/books?available=true")["items"]], [DJANGO_BOOK])
        # incerta (Python) e sem exemplar (TCC) ficam fora dos dois filtros
        unavailable = {b["id"] for b in self.get("/api/books?available=false")["items"]}
        self.assertEqual(len(unavailable), 6)
        self.assertFalse(unavailable & {PYTHON_BOOK, DJANGO_BOOK, TCC})

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

    def test_equipment_is_never_listed(self) -> None:
        Book.objects.filter(id=TCC).update(document_type="Fone de ouvido")
        self.assertEqual(self.get("/api/books")["total"], 8)
        self.assertNotIn(TCC, [b["id"] for b in self.get("/api/books?pageSize=100")["items"]])
        self.assertEqual(self.get("/api/books/%s" % TCC)["id"], TCC)  # a página do item continua

    def test_language_and_year_filters(self) -> None:
        Book.objects.filter(id=PYTHON_BOOK).update(languages=["Inglês"], year=1990)
        Book.objects.filter(id=DJANGO_BOOK).update(languages=["Português", "Inglês"], year=2015)
        english = {b["id"] for b in self.get("/api/books?language=Ingl%C3%AAs")["items"]}
        self.assertEqual(english, {PYTHON_BOOK, DJANGO_BOOK})
        self.assertEqual([b["id"] for b in self.get("/api/books?language=Ingl%C3%AAs&yearTo=2000")["items"]],
                         [PYTHON_BOOK])
        self.assertEqual([b["id"] for b in self.get("/api/books?yearFrom=2015&yearTo=2015")["items"]], [DJANGO_BOOK])
        self.assertEqual(self.get("/api/books?q=python&language=Ingl%C3%AAs&yearTo=2000")["total"], 1)
        self.get("/api/books?yearFrom=-1", status=422)
        self.get("/api/books?language=" + "x" * 41, status=422)

    def test_sort_by_publication_year(self) -> None:
        Book.objects.filter(id=PYTHON_BOOK).update(year=2030)
        Book.objects.filter(id=DJANGO_BOOK).update(year=2029)
        self.assertEqual([b["id"] for b in self.get("/api/books?sort=year&pageSize=2")["items"]],
                         [PYTHON_BOOK, DJANGO_BOOK])
        self.assertEqual(self.get("/api/books?q=python&sort=year")["items"][0]["id"], PYTHON_BOOK)


class LanguageTests(ApiTestCase):
    def test_languages_of_active_books_most_common_first(self) -> None:
        Book.objects.filter(id=PYTHON_BOOK).update(languages=["Inglês"])
        Book.objects.filter(id=DJANGO_BOOK).update(languages=["Inglês", "Francês"])
        Book.objects.filter(id=TCC).update(languages=["Francês"], is_active=False)
        languages = self.get("/api/languages")
        self.assertEqual(languages[:2], ["Português", "Inglês"])
        self.assertIn("Francês", languages)
        self.get("/api/books/facets", status=404)


class BookDetailTests(ApiTestCase):
    def test_detail_refreshes_stale_copies(self) -> None:
        book = self.get("/api/books/%s" % PYTHON_BOOK)
        self.assertEqual(self.library.checked, [PYTHON_BOOK])
        self.assertEqual((book["copies"]["total"], book["copies"]["available"], book["loans"]), (2, 1, 9))
        self.assertEqual(book["copies"]["status"], "available")
        self.assertEqual(book["contributors"], "Trad. por: Fabiane Fiorini")
        self.get("/api/books/%s" % PYTHON_BOOK)
        self.assertEqual(self.library.checked, [PYTHON_BOOK])  # ainda fresco: não consulta de novo

    def test_old_copies_are_refreshed(self) -> None:
        Book.objects.filter(id=PYTHON_BOOK).update(copies_total=1, copies_available=0, copy_status=CopyStatus.ON_LOAN,
                                                   copies_checked_at=timezone.now() - dt.timedelta(hours=1))
        self.assertEqual(self.get("/api/books/%s" % PYTHON_BOOK)["copies"]["available"], 1)

    def test_newer_batch_hides_the_live_count(self) -> None:
        self.get("/api/books/%s" % PYTHON_BOOK)
        apply_snapshot(snapshot_records(), status_items(), min_ratio=0.9,
                       now=timezone.now() + dt.timedelta(minutes=1))
        book = self.get("/api/books/%s" % PYTHON_BOOK)
        self.assertEqual(self.library.checked, [PYTHON_BOOK])  # a consulta ao vivo ainda vale
        self.assertEqual((book["copies"]["status"], book["copies"]["available"], book["loans"]), ("uncertain", None, 9))

    def test_phl_failure_keeps_stored_data(self) -> None:
        self.library.failing[TCC] = LibraryConnectionError("fora do ar")
        with self.assertLogs("catalog.services.availability", "WARNING"):
            book = self.get("/api/books/%s" % TCC)
        self.assertIsNone(book["copies"])
        self.assertEqual(book["links"][0]["label"], "TCC")
        self.assertEqual(book["tccCourse"], "Nutrição")

    def test_locked_database_keeps_stored_data(self) -> None:
        # Durante a sincronização o SQLite só aceita um escritor: a página não pode quebrar.
        locked = OperationalError("database is locked")
        with patch("catalog.services.availability.refresh_copies", side_effect=locked), \
                self.assertLogs("catalog.services.availability", "WARNING"):
            book = self.get("/api/books/%s" % PYTHON_BOOK)
        self.assertEqual(book["id"], PYTHON_BOOK)

    def test_missing_and_inactive_books(self) -> None:
        self.get("/api/books/naoexiste", status=404)
        Book.objects.filter(id=PYTHON_BOOK).update(is_active=False)
        self.get("/api/books/%s" % PYTHON_BOOK, status=404)
        self.assertNotIn(PYTHON_BOOK, [b["id"] for b in self.get("/api/books?q=python")["items"]])

    def test_catalog_link_redirects_to_the_record(self) -> None:
        with patch.object(self.library.phl, "open_session",
                          side_effect=lambda: setattr(self.library.phl, "session", "/tmp/fileNEW")) as open_session:
            self.library.phl.script_dir = "phl82"
            response = self.client.get("/api/books/%s/catalog" % PYTHON_BOOK, HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(open_session.call_count, 1)
        self.assertIn("exp=TIT%%3D%s&" % PYTHON_BOOK, response["Location"])
        self.assertTrue(response["Location"].endswith("tmp=%2Ftmp%2FfileNEW"))

    def test_catalog_link_falls_back_to_the_catalog_home(self) -> None:
        with patch.object(self.library.phl, "open_session", side_effect=LibraryConnectionError("fora do ar")),                 self.assertLogs("catalog.services.catalog_link", "WARNING"):
            response = self.client.get("/api/books/%s/catalog" % PYTHON_BOOK, HTTP_HOST="localhost")
        self.assertEqual((response.status_code, response["Location"]),
                         (302, "https://biblioteca.barbacena.ifsudestemg.edu.br/"))

    def test_catalog_link_of_missing_book(self) -> None:
        self.get("/api/books/naoexiste/catalog", status=404)

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
        # O acervo de teste cabe todo em "para você"; as demais repetiriam os mesmos
        # livros e ficam de fora (cada livro aparece uma vez só), e romance não tem livros.
        self.assertEqual([shelf["id"] for shelf in result["shelves"]], ["for-you"])
        for shelf in result["shelves"]:
            ids = [book["id"] for book in shelf["books"]]
            self.assertGreaterEqual(len(ids), 3)
            self.assertNotIn(PYTHON_BOOK, ids)
            self.assertNotIn(SERIAL, ids)
        self.assertEqual(result["areas"], [{"id": "technology", "name": "Tecnologia e Computação"}])

    def small_shelves(self, size: int = 2) -> None:
        """Prateleiras pequenas, para o acervo de teste render várias."""
        for name, value in (("SHELF_SIZE", size), ("MIN_SHELF_SIZE", 1)):
            patcher = patch.object(recommendations, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def shelf_books(self, body: dict[str, object]) -> dict[str, list[str]]:
        result = self.post("/api/recommendations", body)
        return {shelf["id"]: [book["id"] for book in shelf["books"]] for shelf in result["shelves"]}

    def test_each_book_appears_once(self) -> None:
        self.small_shelves(size=1)
        shelves = self.shelf_books({"areaIds": ["technology", "health-sciences"], "courseIds": ["internet-systems"],
                                    "seedBookIds": [PYTHON_BOOK]})
        self.assertGreater(len(shelves), 1)
        ids = [book_id for books in shelves.values() for book_id in books]
        self.assertEqual(len(ids), len(set(ids)))

    def test_shuffle_seed(self) -> None:
        profile: dict[str, object] = {"areaIds": ["technology"], "seedBookIds": [PYTHON_BOOK]}
        relevance = self.shelf_books(profile)["for-you"]
        orders = set()
        for seed in range(10):
            shuffled = self.shelf_books({**profile, "shuffleSeed": seed})["for-you"]
            self.assertEqual(shuffled, self.shelf_books({**profile, "shuffleSeed": seed})["for-you"])
            self.assertEqual(set(shuffled), set(relevance))  # os candidatos cabem todos no sorteio
            orders.add(tuple(shuffled))
        self.assertGreater(len(orders), 1)
        self.post("/api/recommendations", {**profile, "shuffleSeed": -1}, status=422)

    def give_genre(self, genre: str, *book_ids: str) -> None:
        for book_id in book_ids:
            Book.objects.get(id=book_id).genres.add(genre)

    def test_shelves_in_order_genres_for_you_then_similar(self) -> None:
        self.small_shelves(size=1)
        self.give_genre("romance", TCC)
        shelves = self.shelf_books({"areaIds": ["technology"], "seedBookIds": [PYTHON_BOOK], "genreIds": ["romance"]})
        self.assertEqual(list(shelves), ["your-genres", "for-you", "from-your-books"])

    def test_chosen_genres_share_one_shelf(self) -> None:
        self.small_shelves(size=4)
        self.give_genre("romance", TCC, DJANGO_BOOK)
        self.give_genre("poetry", PYTHON_BOOK)
        shelves = self.shelf_books({"genreIds": ["romance", "poetry"]})
        # sem área nem curso não há "para você"; os gêneros se intercalam numa prateleira só
        self.assertEqual(list(shelves), ["your-genres"])
        self.assertEqual(set(shelves["your-genres"]), {TCC, DJANGO_BOOK, PYTHON_BOOK})
        self.assertEqual(list(self.shelf_books({"genreIds": ["poetry"]})), ["your-genres"])

    def test_for_you_counts_only_course_and_area(self) -> None:
        self.small_shelves()
        self.give_genre("romance", TCC)
        # o TCC tem o gênero escolhido, mas não é da área: fica só em "dos seus gêneros"
        shelves = self.shelf_books({"areaIds": ["technology"], "genreIds": ["romance"]})
        self.assertEqual(shelves["your-genres"], [TCC])
        self.assertNotIn(TCC, shelves["for-you"])
        self.assertEqual(Book.objects.get(id=shelves["for-you"][0]).area_id, "technology")

    def test_without_seed_books_there_is_no_similar_shelf(self) -> None:
        self.assertNotIn("from-your-books", self.shelf_books({"areaIds": ["technology"]}))

    def test_unreadable_titles_are_left_out(self) -> None:
        profile = {"areaIds": ["technology"], "seedBookIds": [PYTHON_BOOK]}
        shelf_ids = [book["id"] for book in self.post("/api/recommendations", profile)["shelves"][0]["books"]]
        related_ids = [book["id"] for book in self.get("/api/books/%s/related" % PYTHON_BOOK)["related"]]
        unavailable, without_copies = shelf_ids[0], related_ids[0]
        Book.objects.filter(id=unavailable).update(copy_status=CopyStatus.UNAVAILABLE)
        Book.objects.filter(id=without_copies).update(copy_status=CopyStatus.NO_COPIES, links=[])
        result = self.post("/api/recommendations", profile)
        ids = {book["id"] for shelf in result["shelves"] for book in shelf["books"]}
        ids |= {book["id"] for book in self.get("/api/books/%s/related" % PYTHON_BOOK)["related"]}
        self.assertFalse(ids & {unavailable, without_copies})

    def test_titles_without_copies_stay_when_they_have_a_link(self) -> None:
        Book.objects.filter(id=TCC).update(copy_status=CopyStatus.NO_COPIES)
        self.assertTrue(recommendations.recommendable().filter(id=TCC).exists())

    def test_unknown_ids_are_ignored(self) -> None:
        result = self.post("/api/recommendations", {"areaIds": ["nope"], "seedBookIds": ["nope"]})
        self.assertEqual(result, {"shelves": [], "areas": []})

    def test_profile_limits(self) -> None:
        self.post("/api/recommendations", {"seedBookIds": ["x"] * 21}, status=422)

    def test_onboarding_candidates(self) -> None:
        candidates = [b["id"] for b in self.get("/api/recommendations/candidates?course=nutrition&area=technology")]
        # as áreas se intercalam: a de Tecnologia (escolhida) e a de Saúde (do curso marcado)
        self.assertEqual(len(candidates), 6)
        self.assertEqual(candidates[1], TCC)
        self.assertNotIn(SERIAL, candidates)

    def test_candidates_cover_every_chosen_area(self) -> None:
        candidates = self.get("/api/recommendations/candidates?course=internet-systems"
                              "&area=technology&area=health-sciences&limit=4")
        self.assertEqual({b["areaId"] for b in candidates}, {"technology", "health-sciences"})
        # sem área nem curso, completa com os demais títulos recomendáveis
        self.assertEqual(len(self.get("/api/recommendations/candidates?limit=4")), 4)


class StatusTests(ApiTestCase):
    def test_status(self) -> None:
        status = self.get("/api/status")
        self.assertEqual((status["activeBooks"], status["booksWithCopies"]), (9, 0))
        self.assertIsNone(status["catalogSync"])  # apply_snapshot direto não registra execução
        self.assertNotIn("copiesSync", status)
        apply_snapshot(snapshot_records(), status_items(), min_ratio=0.9)
        self.assertEqual(self.get("/api/status")["booksWithCopies"], 9)
