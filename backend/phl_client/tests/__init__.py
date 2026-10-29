"""Testes do cliente PHL. Não usam a rede: as páginas reais ficam em `fixtures/`."""

from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"
BASE_URL = "https://biblioteca.barbacena.ifsudestemg.edu.br"


def fixture(name: str) -> str:
    """Conteúdo de uma página salva do OPAC."""
    return (FIXTURES / name).read_text(encoding="utf-8")
