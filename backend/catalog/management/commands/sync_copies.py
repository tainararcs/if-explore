"""Comando `sync_copies`: rodízio noturno da situação dos exemplares."""

from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from catalog.services.sync import SyncError, sync_copies
from phl_client import LibraryError


class Command(BaseCommand):
    help = ("Verifica os exemplares dos títulos verificados há mais tempo (1 requisição por título, "
            "~0,7 s cada) e grava disponibilidade e empréstimos.")

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--limit", type=int, default=None,
                            help="títulos nesta execução (padrão: COPIES_SYNC_BATCH)")
        parser.add_argument("--book", action="append", dest="book_ids", metavar="ID",
                            help="verifica só este título; pode repetir")

    def handle(self, *args: Any, **options: Any) -> None:
        if options["limit"] is not None and options["limit"] < 1:
            raise CommandError("--limit deve ser >= 1")
        try:
            run = sync_copies(limit=options["limit"], book_ids=options["book_ids"])
        except (SyncError, LibraryError) as error:
            raise CommandError(str(error)) from error
        self.stdout.write(self.style.SUCCESS("exemplares sincronizados: %s" % run.stats))
