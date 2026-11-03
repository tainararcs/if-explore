from django.apps import AppConfig


class CatalogConfig(AppConfig):
    """Acervo da biblioteca: livros sincronizados do PHL e a taxonomia do IF Explore."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "catalog"
    verbose_name = "Acervo"
