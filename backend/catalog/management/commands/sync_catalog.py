"""Comando `sync_catalog`: snapshot diário dos metadados do PHL."""

from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from catalog.services.sync import SyncError, sync_catalog
from phl_client import LibraryError


class Command(BaseCommand):
    help = "Baixa o acervo inteiro do PHL (1 requisição, ~10 s) e atualiza livros, relações e índice de busca."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--min-ratio", type=float, default=None,
                            help="fração mínima dos títulos ativos que o snapshot precisa ter "
                                 "(padrão: CATALOG_SYNC_MIN_RATIO)")

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            run = sync_catalog(min_ratio=options["min_ratio"])
        except (SyncError, LibraryError) as error:
            raise CommandError(str(error)) from error
        self.stdout.write(self.style.SUCCESS("catálogo sincronizado: %s" % run.stats))
