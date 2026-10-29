"""Derivação da área, dos cursos e dos gêneros de um livro a partir dos dados do PHL.

Funções puras: as regras vêm da taxonomia (editável no admin) já convertida em
`CourseRule` e `GenreRule`, então podem ser testadas sem banco.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from phl_client.text import normalize

# CDD 004–006 (computação) é sempre Tecnologia, qualquer que seja a área CNPq.
TECHNOLOGY_CDD_PREFIXES = ("004", "005", "006")
TECHNOLOGY_AREA = "technology"

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


def cdd_digits(cdd: str) -> str:
    """Só os dígitos da CDD, sem o prefixo de letras da tabela brasileira.

    'B869.3' -> '8693'; '005.133 PYTHON' -> '005133'.
    """
    return re.sub(r"\D", "", re.sub(r"^[A-Za-z]+", "", cdd.strip()))


def resolve_area(cnpq_code: str, cdd: str, cnpq_to_area: Mapping[str, str]) -> str | None:
    """Área do IF Explore de um livro.

    Ordem: computação pela CDD; depois a área CNPq do registro; por fim a CDD.

    Args:
        cnpq_code: Código CNPq do PHL (1 a 9) ou vazio.
        cdd: Classificação como cadastrada.
        cnpq_to_area: Código CNPq -> slug da área.
    """
    digits = cdd_digits(cdd)
    if digits.startswith(TECHNOLOGY_CDD_PREFIXES):
        return TECHNOLOGY_AREA
    if cnpq_code in cnpq_to_area:
        return cnpq_to_area[cnpq_code]
    for size in range(min(len(digits), 3), 0, -1):
        area = CDD_AREA_FALLBACK.get(digits[:size])
        if area:
            return area
    return None


def resolve_courses(phl_codes: Iterable[str], tcc_course: str, rules: Iterable[CourseRule]) -> list[str]:
    """Slugs dos cursos de um livro, pelos códigos de bibliografia ou pelo curso do TCC."""
    codes = set(phl_codes)
    tcc = normalize(tcc_course.strip()) if tcc_course else ""
    return [rule.slug for rule in rules if codes & rule.phl_codes or (tcc and tcc in rule.tcc_names)]


def resolve_genres(subjects: Iterable[str], cdd: str, authors: Iterable[str],
                   rules: Iterable[GenreRule]) -> list[str]:
    """Slugs dos gêneros literários de um livro.

    As palavras-chave de assunto só valem para CDD literária (800–899, inclusive a
    B869 brasileira) ou ausente: assim "MEMÓRIA RAM" não vira biografia.
    """
    digits = cdd_digits(cdd)
    literary = not digits or digits.startswith("8")
    cdd_upper = cdd.strip().upper()
    normalized_subjects = [normalize(subject) for subject in subjects]
    normalized_authors = [normalize(author) for author in authors]
    genres = []
    for rule in rules:
        matched = any(cdd_upper.startswith(prefix) for prefix in rule.cdd_prefixes) or (
            literary and any(re.search(r"\b" + re.escape(keyword), subject)
                             for keyword in rule.subject_keywords for subject in normalized_subjects))
        if matched and rule.author_keywords:
            matched = any(keyword in author for keyword in rule.author_keywords for author in normalized_authors)
        if matched:
            genres.append(rule.slug)
    return genres
