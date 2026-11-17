"""Derivação da área, dos cursos e dos gêneros de um livro a partir dos dados do PHL.

Funções puras: as regras vêm da taxonomia (editável no admin) já convertida em
`CourseRule` e `GenreRule`, então podem ser testadas sem banco.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from phl_client.text import normalize

# Faixas da CDD que valem mais que a área CNPq do registro, que nelas costuma vir
# errada: computação cadastrada como Engenharias ou Exatas, e criação animal,
# veterinária e tecnologia de alimentos cadastradas como Biológicas, Saúde ou
# Engenharias. Chave: prefixo dos dígitos da CDD; vale o prefixo mais longo.
CDD_AREA_OVERRIDES = {
    "004": "technology", "005": "technology", "006": "technology",
    "63": "agricultural-sciences", "664": "agricultural-sciences",
}

# Área pela CDD quando o PHL não traz área CNPq útil (9 = "Outros", ou vazia).
# Chave: prefixo dos dígitos da CDD; vale o prefixo mais longo.
CDD_AREA_FALLBACK = {
    "0": "humanities", "1": "humanities", "2": "humanities",
    "3": "applied-social-sciences", "37": "humanities",          # 370: educação
    "4": "languages-arts",
    "5": "exact-sciences", "57": "biological-sciences", "58": "biological-sciences",
    "59": "biological-sciences",
    "6": "technology", "61": "health-sciences", "63": "agricultural-sciences",
    "641": "health-sciences",                                     # nutrição
    "65": "applied-social-sciences", "664": "agricultural-sciences",  # tecnologia de alimentos
    "7": "languages-arts", "796": "health-sciences",              # esportes
    "8": "languages-arts",
    "9": "humanities",
}

# Dígitos da CDD de literatura: 800–899 e a 028.5 (literatura infantojuvenil).
LITERARY_CDD_PREFIXES = ("8", "0285")


@dataclass(frozen=True)
class CourseRule:
    """Como reconhecer um curso nos registros do PHL."""

    slug: str
    phl_codes: frozenset[str]
    #: Nomes do curso nos TCCs, já normalizados.
    tcc_names: frozenset[str]


@dataclass(frozen=True)
class GenreRule:
    """Regras de um gênero literário (ver `catalog.models.LiteraryGenre`)."""

    slug: str
    #: Palavras-chave já normalizadas; casam no início de uma palavra do assunto.
    subject_keywords: tuple[str, ...]
    #: Prefixos da CDD como cadastrada, em maiúsculas ("B869.1", "741.5").
    cdd_prefixes: tuple[str, ...]
    #: Trechos de nomes de autor já normalizados; quando há algum, um precisa casar.
    author_keywords: tuple[str, ...]


# Primeiro número da classificação, com o "B" da tabela brasileira quando houver.
# Letras coladas antes do número (coleção ou outra tabela, como "Cb863") ficam de fora.
_CDD_CLASS = re.compile(r"(?:(?<![A-Z])B\s*)?\d+(?:\.\d+)?")


def cdd_class(cdd: str) -> str:
    """A classificação da CDD, sem prefixo de coleção nem notação de autor.

    O catálogo escreve a coleção antes da CDD ("CE", "R", "LIJ") e às vezes a
    notação de autor depois: 'CE / B 869.33' -> 'B869.33'; 'LIJ /B028.5' ->
    'B028.5'; 'R / CE / 636 / D 569z' -> '636'; 'Cb863' -> '863'.
    """
    match = _CDD_CLASS.search(cdd.upper())
    return re.sub(r"\s", "", match.group()) if match else ""


def cdd_digits(cdd: str) -> str:
    """Só os dígitos da classificação, sem prefixos de letras.

    'B869.3' -> '8693'; '005.133 PYTHON' -> '005133'.
    """
    return re.sub(r"\D", "", cdd_class(cdd))


def _by_cdd_prefix(digits: str, table: Mapping[str, str]) -> str | None:
    """Valor do prefixo mais longo (até 3 dígitos) de `digits` em `table`."""
    for size in range(min(len(digits), 3), 0, -1):
        value = table.get(digits[:size])
        if value:
            return value
    return None


def resolve_area(cnpq_code: str, cdd: str, cnpq_to_area: Mapping[str, str]) -> str | None:
    """Área do IF Explore de um livro.

    Ordem: as faixas da CDD em `CDD_AREA_OVERRIDES`; depois a área CNPq do
    registro; por fim a CDD.

    Args:
        cnpq_code: Código CNPq do PHL (1 a 9) ou vazio.
        cdd: Classificação como cadastrada.
        cnpq_to_area: Código CNPq -> slug da área.
    """
    digits = cdd_digits(cdd)
    override = _by_cdd_prefix(digits, CDD_AREA_OVERRIDES)
    if override:
        return override
    if cnpq_code in cnpq_to_area:
        return cnpq_to_area[cnpq_code]
    return _by_cdd_prefix(digits, CDD_AREA_FALLBACK)


def resolve_courses(phl_codes: Iterable[str], tcc_course: str, rules: Iterable[CourseRule]) -> list[str]:
    """Slugs dos cursos de um livro, pelos códigos de bibliografia ou pelo curso do TCC."""
    codes = set(phl_codes)
    tcc = normalize(tcc_course.strip()) if tcc_course else ""
    return [rule.slug for rule in rules if codes & rule.phl_codes or (tcc and tcc in rule.tcc_names)]


def resolve_genres(subjects: Iterable[str], cdd: str, authors: Iterable[str],
                   rules: Iterable[GenreRule]) -> list[str]:
    """Slugs dos gêneros literários de um livro.

    As palavras-chave de assunto só valem para CDD literária (800–899, inclusive a
    B869 brasileira, e a 028.5 da literatura infantojuvenil) ou ausente: assim
    "MEMÓRIA RAM" não vira biografia. Os prefixos de CDD são comparados com a
    classificação sem o prefixo de coleção (`cdd_class`).
    """
    classification = cdd_class(cdd)
    digits = re.sub(r"\D", "", classification)
    literary = not digits or digits.startswith(LITERARY_CDD_PREFIXES)
    normalized_subjects = [normalize(subject) for subject in subjects]
    normalized_authors = [normalize(author) for author in authors]
    genres = []
    for rule in rules:
        matched = any(classification.startswith(prefix) for prefix in rule.cdd_prefixes) or (
            literary and any(re.search(r"\b" + re.escape(keyword), subject)
                             for keyword in rule.subject_keywords for subject in normalized_subjects))
        if matched and rule.author_keywords:
            matched = any(keyword in author for keyword in rule.author_keywords for author in normalized_authors)
        if matched:
            genres.append(rule.slug)
    return genres
