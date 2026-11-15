"""CORS da API: só origens configuradas, só em /api/ e sem cookies."""

from django.test import TestCase, override_settings

ORIGIN = "https://if-explore.example.edu.br"


@override_settings(CORS_ALLOWED_ORIGINS=[ORIGIN])
class CorsTests(TestCase):
    def preflight(self, url: str, origin: str) -> dict[str, str]:
        response = self.client.options(url, HTTP_HOST="localhost", HTTP_ORIGIN=origin,
                                       HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST")
        return dict(response.headers)

    def test_allowed_origin_on_api(self) -> None:
        headers = self.preflight("/api/discovery", ORIGIN)
        self.assertEqual(headers.get("access-control-allow-origin"), ORIGIN)
        self.assertNotIn("access-control-allow-credentials", headers)

        response = self.client.get("/api/areas", HTTP_HOST="localhost", HTTP_ORIGIN=ORIGIN)
        self.assertEqual(response.headers.get("access-control-allow-origin"), ORIGIN)

    def test_unknown_origin_is_not_allowed(self) -> None:
        headers = self.preflight("/api/discovery", "https://other.example.com")
        self.assertNotIn("access-control-allow-origin", headers)

    def test_admin_is_not_exposed(self) -> None:
        headers = self.preflight("/admin/", ORIGIN)
        self.assertNotIn("access-control-allow-origin", headers)

    @override_settings(CORS_ALLOWED_ORIGINS=[])
    def test_disabled_by_default(self) -> None:
        headers = self.preflight("/api/areas", ORIGIN)
        self.assertNotIn("access-control-allow-origin", headers)
