"""Rotas do projeto: o admin e a API (documentação interativa em /api/docs)."""

from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.urls import path
from ninja import NinjaAPI
from ninja.errors import Throttled

from catalog.api import router as catalog_router

api = NinjaAPI(
    title="IF Explore API",
    version="1.0.0",
    description="Acervo da Biblioteca Roberval Cardoso, sincronizado com o catálogo PHL do campus.",
)
api.add_router("/", catalog_router)


@api.exception_handler(Throttled)
def throttled(request: HttpRequest, exc: Throttled) -> HttpResponse:
    """Limite de requisições atingido, com a mensagem em português."""
    response = api.create_response(request, {"detail": "muitas requisições; tente de novo em instantes"},
                                   status=429)
    if exc.wait is not None:
        response["Retry-After"] = str(max(1, round(exc.wait)))
    return response

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
