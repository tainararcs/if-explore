"""Rotas do projeto: o admin e a API (documentação interativa em /api/docs)."""

from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from catalog.api import router as catalog_router

api = NinjaAPI(
    title="IF Explore API",
    version="1.0.0",
    description="Acervo da Biblioteca Roberval Cardoso, sincronizado com o catálogo PHL do campus.",
)
api.add_router("/", catalog_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
