"""Sugestões da IA para o perfil e explicações dos livros. O Gemini nunca é acessado: um
FakeGemini registra os pedidos e devolve respostas prontas ou falhas."""

import json
from typing import Any
from unittest.mock import patch

from django.core.cache import cache
from django.test import SimpleTestCase

from catalog.models import Book, BookExplanation
from catalog.services import discovery, gemini, recommendations

from .test_api import ApiTestCase
from .test_sync import DJANGO_BOOK, PYTHON_BOOK, TCC

# Perfil de quem estuda Sistemas para Internet e marcou o livro de Django.
PROFILE = {"areaIds": ["technology"], "courseIds": ["internet-systems"], "seedBookIds": [DJANGO_BOOK],
           "genreIds": ["romance"]}


class FakeGemini:
    """Substitui `gemini.client()`: guarda os pedidos e devolve `answers` em ordem
    (uma exceção na lista é levantada)."""

    model = "fake-model"

    def __init__(self, *answers: object, enabled: bool = True) -> None:
        self.answers = list(answers)
        self.enabled = enabled
        self.prompts: list[str] = []

    def generate_json(self, system: str, prompt: str, schema: dict[str, object]) -> object:
        self.prompts.append(prompt)
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer


class GeminiTestCase(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        cache.clear()

    def use(self, fake: FakeGemini) -> FakeGemini:
        client = patch("catalog.services.gemini.client", return_value=fake)
        client.start()
        self.addCleanup(client.stop)
        return fake

    def discover(self, status: int = 200, **extra: object) -> Any:
        return self.post("/api/recommendations/ai", {**PROFILE, **extra}, status)

    def ids(self, result: Any) -> list[str]:
        return [item["book"]["id"] for item in result["items"]]


class DiscoveryApiTests(GeminiTestCase):
    def setUp(self) -> None:
        super().setUp()
        # O TCC tem o gênero escolhido: é o candidato de "dos seus gêneros".
        Book.objects.get(id=TCC).genres.add("romance")

    def kinds(self, result: Any) -> list[str]:
        return [item["kind"] for item in result["items"]]

    def test_ai_picks_one_per_shelf_with_reasons(self) -> None:
        fake = self.use(FakeGemini({"mensagem": "  Boas   leituras!  ", "recomendacoes": [
            {"grupo": "curso_area", "id": PYTHON_BOOK, "motivo": "Você estuda Sistemas para Internet."},
            {"grupo": "generos", "id": TCC, "motivo": "Você gosta de romance."},
        ]}))
        result = self.discover()
        self.assertEqual(result["source"], "ai")
        self.assertEqual(result["message"], "Boas leituras!")
        # na ordem das prateleiras; sem candidatos de "parecidos", a vaga vai a outro livro
        self.assertEqual(self.ids(result)[:2], [TCC, PYTHON_BOOK])
        self.assertEqual(self.kinds(result)[:2], ["yourGenres", "forYou"])
        self.assertEqual(result["items"][0]["reason"], "Você gosta de romance.")
        self.assertEqual(len(result["items"]), discovery.PICKS)
        self.assertIsNone(result["items"][2]["reason"])
        self.assertIn("callNumber", result["items"][0]["book"])
        self.assertEqual(len(fake.prompts), 1)

    def test_pick_from_the_wrong_group_or_outside_is_dropped(self) -> None:
        self.use(FakeGemini({"mensagem": "", "recomendacoes": [
            {"grupo": "generos", "id": PYTHON_BOOK, "motivo": "grupo errado"},
            {"grupo": "curso_area", "id": "999999", "motivo": "inventado"},
            {"grupo": "curso_area", "id": PYTHON_BOOK, "motivo": "ok"},
            {"grupo": "curso_area", "id": DJANGO_BOOK, "motivo": "segundo do mesmo grupo"},
        ]}))
        result = self.discover()
        ids = self.ids(result)
        self.assertEqual((ids[0], result["items"][0]["reason"]), (TCC, None))  # completado pelas regras
        self.assertEqual((ids[1], result["items"][1]["reason"]), (PYTHON_BOOK, "ok"))
        self.assertEqual((len(ids), len(set(ids))), (discovery.PICKS, discovery.PICKS))
        self.assertNotIn("999999", ids)
        self.assertNotIn(DJANGO_BOOK, ids)  # o título escolhido no perfil nunca volta

    def test_failures_fall_back_to_rules(self) -> None:
        for failure in (gemini.GeminiUnavailableError("timeout"), gemini.GeminiQuotaError("429"),
                        gemini.GeminiBlockedError("SAFETY"), {"sem": "formato"},
                        {"mensagem": "x", "recomendacoes": [{"grupo": "generos", "id": "999999", "motivo": "fora"}]}):
            with self.subTest(failure=failure):
                self.use(FakeGemini(failure))
                result = self.discover()
                self.assertEqual(result["source"], "rules")
                self.assertIsNone(result["message"])
                # o primeiro de cada prateleira, completado até 3
                self.assertEqual(self.ids(result)[0], TCC)
                self.assertEqual(len(result["items"]), discovery.PICKS)
                self.assertTrue(all(item["reason"] is None for item in result["items"]))

    def test_without_key_gemini_is_not_called(self) -> None:
        fake = self.use(FakeGemini(enabled=False))
        result = self.discover()
        self.assertEqual(result["source"], "rules")
        self.assertEqual(fake.prompts, [])

    def test_no_candidates_returns_empty_without_calling_gemini(self) -> None:
        fake = self.use(FakeGemini())
        result = self.post("/api/recommendations/ai", {"areaIds": ["nope"]})
        self.assertEqual((result["source"], result["items"]), ("rules", []))
        self.assertEqual(fake.prompts, [])

    def test_prompt_has_the_anonymous_profile_and_candidates_by_shelf(self) -> None:
        fake = self.use(FakeGemini({"mensagem": "", "recomendacoes": [
            {"grupo": "curso_area", "id": PYTHON_BOOK, "motivo": "ok"}]}))
        self.discover()
        prompt = json.loads(fake.prompts[0])
        profile = prompt["perfil"]
        self.assertEqual(profile["areas"], ["Tecnologia e Computação"])
        self.assertEqual(profile["cursos"], ["Tecnologia em Sistemas para Internet"])
        self.assertEqual(profile["generos"], ["Romance"])
        self.assertEqual(len(profile["livros_escolhidos"]), 1)
        # nenhum id do perfil vai para a IA: nem slugs nem o id do livro escolhido
        self.assertNotIn("internet-systems", fake.prompts[0])
        self.assertNotIn(DJANGO_BOOK, json.dumps(profile))
        groups = prompt["grupos"]
        # só grupos com candidatos, e um livro não aparece em dois grupos
        self.assertEqual(set(groups), {"generos", "curso_area"})
        self.assertEqual([book["id"] for book in groups["generos"]], [TCC])
        ids = [book["id"] for group in groups.values() for book in group]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertNotIn(DJANGO_BOOK, ids)
        self.assertEqual(recommendations.recommendable().filter(id__in=ids).count(), len(ids))
        self.assertTrue(all(len(book.get("sinopse", "")) <= discovery.SYNOPSIS_CHARS + 1
                            for group in groups.values() for book in group))

    def test_gemini_is_asked_for_one_book_per_group(self) -> None:
        schema = discovery.discovery_schema(["generos", "curso_area"])
        properties = schema["properties"]
        assert isinstance(properties, dict)
        array = properties["recomendacoes"]
        self.assertEqual((array["minItems"], array["maxItems"]), (2, 2))
        self.assertEqual(array["items"]["properties"]["grupo"]["enum"], ["generos", "curso_area"])
        self.assertIn("exatamente um livro de cada grupo", discovery.DISCOVERY_SYSTEM)

    def test_more_suggestions_exclude_the_ones_already_shown(self) -> None:
        fake = self.use(FakeGemini(enabled=False))
        first = self.ids(self.discover())
        second = self.ids(self.discover(excludeIds=first))
        self.assertTrue(second)
        self.assertFalse(set(first) & set(second))
        self.assertEqual(fake.prompts, [])

    def test_excluded_ids_never_reach_gemini(self) -> None:
        fake = self.use(FakeGemini({"mensagem": "", "recomendacoes": [
            {"grupo": "curso_area", "id": PYTHON_BOOK, "motivo": "de novo"}]}))
        result = self.discover(excludeIds=[PYTHON_BOOK])
        groups = json.loads(fake.prompts[0])["grupos"]
        self.assertNotIn(PYTHON_BOOK, [book["id"] for group in groups.values() for book in group])
        # o Gemini insistiu num livro já mostrado: a escolha é descartada e vale a seleção por regras
        self.assertEqual(result["source"], "rules")
        self.assertNotIn(PYTHON_BOOK, self.ids(result))

    def test_too_many_or_too_long_excluded_ids_are_rejected(self) -> None:
        self.discover(excludeIds=[str(n) for n in range(discovery.MAX_EXCLUDED + 1)], status=422)
        self.discover(excludeIds=["9" * 21], status=422)

    def test_rate_limit(self) -> None:
        self.use(FakeGemini(enabled=False))
        for _ in range(10):
            self.discover()
        response = self.client.post("/api/recommendations/ai", json.dumps(PROFILE),
                                    content_type="application/json", HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 429)
        self.assertIn("tente de novo", response.json()["detail"])
        self.assertTrue(response.has_header("Retry-After"))

    def test_old_discovery_route_is_gone(self) -> None:
        response = self.client.post("/api/discovery", json.dumps({"query": "python"}),
                                    content_type="application/json", HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 404)


class ExplanationApiTests(GeminiTestCase):
    def test_generated_once_then_cached(self) -> None:
        fake = self.use(FakeGemini({"explicacao": "Um livro   para começar a programar."}))
        first = self.get(f"/api/books/{PYTHON_BOOK}/explanation")
        second = self.get(f"/api/books/{PYTHON_BOOK}/explanation")
        self.assertEqual(first["text"], "Um livro para começar a programar.")
        self.assertEqual(second, first)
        self.assertIsNotNone(first["generatedAt"])
        self.assertEqual(len(fake.prompts), 1)
        self.assertNotIn('"id"', fake.prompts[0])

    def test_regenerated_when_the_record_changes(self) -> None:
        fake = self.use(FakeGemini({"explicacao": "Primeira."}, {"explicacao": "Segunda."}))
        self.get(f"/api/books/{PYTHON_BOOK}/explanation")
        Book.objects.filter(id=PYTHON_BOOK).update(synopsis="Uma sinopse nova sobre Python.")
        self.assertEqual(self.get(f"/api/books/{PYTHON_BOOK}/explanation")["text"], "Segunda.")
        self.assertEqual(len(fake.prompts), 2)
        self.assertEqual(BookExplanation.objects.count(), 1)

    def test_null_without_data_key_or_on_failure(self) -> None:
        empty = {"text": None, "generatedAt": None}
        book = Book.objects.get(id=TCC)
        book.subjects.clear()
        Book.objects.filter(id=TCC).update(synopsis="")
        fake = self.use(FakeGemini(gemini.GeminiUnavailableError("timeout"), {"explicacao": "  "}))
        self.assertEqual(self.get(f"/api/books/{TCC}/explanation"), empty)
        self.assertEqual(fake.prompts, [])
        self.assertEqual(self.get(f"/api/books/{PYTHON_BOOK}/explanation"), empty)
        self.assertEqual(self.get(f"/api/books/{PYTHON_BOOK}/explanation"), empty)
        self.assertFalse(BookExplanation.objects.exists())
        self.use(FakeGemini(enabled=False))
        self.assertEqual(self.get(f"/api/books/{DJANGO_BOOK}/explanation"), empty)

    def test_inactive_or_missing_book_is_404(self) -> None:
        self.use(FakeGemini())
        Book.objects.filter(id=PYTHON_BOOK).update(is_active=False)
        self.get(f"/api/books/{PYTHON_BOOK}/explanation", status=404)
        self.get("/api/books/000/explanation", status=404)


class PureRulesTests(SimpleTestCase):
    def test_validate_answer(self) -> None:
        groups = {"yourGenres": ["1", "2"], "forYou": ["3", "4"], "fromYourBooks": ["5"]}
        answer = {"mensagem": "  Oi  ", "recomendacoes": [
            {"grupo": "parecidos", "id": "5", "motivo": " a  b "}, {"grupo": "generos", "id": "3", "motivo": "grupo errado"},
            "lixo", {"grupo": "nenhum", "id": "1"}, {"grupo": "generos", "id": "2"},
            {"grupo": "generos", "id": "1", "motivo": "segundo do grupo"}]}
        message, picks = discovery.validate_answer(answer, groups)
        self.assertEqual(message, "Oi")
        # na ordem das prateleiras; "curso_area" não veio
        self.assertEqual([(pick.kind, pick.book_id, pick.reason) for pick in picks],
                         [("yourGenres", "2", None), ("fromYourBooks", "5", "a b")])
        with self.assertRaises(gemini.GeminiInvalidResponseError):
            discovery.validate_answer({"recomendacoes": "nada"}, groups)

    def test_complete_gives_one_per_shelf_and_fills_empty_ones(self) -> None:
        groups = {"yourGenres": [], "forYou": ["3", "4", "6"], "fromYourBooks": ["5"]}
        picks = discovery.complete([discovery.Pick("5", "fromYourBooks", "ok")], groups)
        self.assertEqual([(pick.kind, pick.book_id) for pick in picks],
                         [("forYou", "3"), ("fromYourBooks", "5"), ("forYou", "4")])
        self.assertEqual(len(discovery.complete([], {"yourGenres": ["1"], "forYou": [], "fromYourBooks": []})), 1)

    def test_clean_text_cuts_on_a_word(self) -> None:
        text = discovery.clean_text("palavra " * 50, 30)
        assert text is not None
        self.assertLessEqual(len(text), 30)
        self.assertTrue(text.endswith("palavra…"))
        self.assertIsNone(discovery.clean_text(42, 30))

    def test_parse_answer(self) -> None:
        ok = {"candidates": [{"finishReason": "STOP", "content": {"parts": [
            {"text": "pensando", "thought": True}, {"text": '{"a": 1}'}]}}]}
        self.assertEqual(gemini._parse_answer(ok), {"a": 1})
        for broken, error in (({"candidates": []}, gemini.GeminiBlockedError),
                              ({"candidates": [{"finishReason": "MAX_TOKENS"}]}, gemini.GeminiBlockedError),
                              ({"candidates": [{"content": {"parts": [{"text": "{"}]}}]},
                               gemini.GeminiInvalidResponseError)):
            with self.subTest(broken=broken), self.assertRaises(error):
                gemini._parse_answer(broken)

    def test_client_without_key_never_calls(self) -> None:
        with self.assertRaises(gemini.GeminiUnavailableError):
            gemini.GeminiClient("", "model", 1).generate_json("s", "p", {})
