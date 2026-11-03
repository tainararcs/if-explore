"""Contrato JSON da API do acervo.

Os campos são declarados em snake_case e saem em camelCase (`areaId`, `pageSize`),
como no tipo `Book` do frontend. Valores ausentes saem como `null`.
"""

from __future__ import annotations

import datetime as dt
from typing import Literal

from ninja import Schema
from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel

from catalog.models import Book, Course, KnowledgeArea, LiteraryGenre

ShelfKind = Literal["forYou", "becauseYouChose", "moreFromArea", "forPleasure"]


class CamelSchema(Schema):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


# ---- taxonomia
class AreaOut(CamelSchema):
    id: str
    name: str

    @classmethod
    def from_model(cls, area: KnowledgeArea) -> AreaOut:
        return cls(id=area.slug, name=area.name)


class CourseOut(CamelSchema):
    id: str
    name: str
    area_id: str
    level: str

    @classmethod
    def from_model(cls, course: Course) -> CourseOut:
        return cls(id=course.slug, name=course.name, area_id=course.area_id, level=course.level)


class GenreOut(CamelSchema):
    id: str
    name: str

    @classmethod
    def from_model(cls, genre: LiteraryGenre) -> GenreOut:
        return cls(id=genre.slug, name=genre.name)


# ---- livros
class CopiesOut(CamelSchema):
    """Exemplares do título. Ausente (`null` no livro) até a primeira verificação."""

    total: int
    available: int
    #: Quando a situação foi consultada no PHL.
    updated_at: dt.datetime


class BookLinkOut(CamelSchema):
    label: str
    url: str


class BookSummaryOut(CamelSchema):
    """Livro como aparece em listas, prateleiras e resultados de busca."""

    id: str
    title: str
    subtitle: str | None
    authors: list[str]
    year: int | None
    area_id: str | None
    course_ids: list[str]
    genre_ids: list[str]
    subjects: list[str]
    synopsis: str | None
    #: CDD e cutter, usados para achar o livro na estante.
    call_number: str | None
    isbn: str | None
    publisher: str | None
    edition: str | None
    pages: int | None
    #: Tipo como o catálogo exibe ("Livro", "Periódico").
    document_type: str | None
    cover_url: str | None
    copies: CopiesOut | None
    #: Empréstimos já feitos, somando os exemplares (0 até a primeira verificação).
    loans: int

    @staticmethod
    def fields_from(book: Book) -> dict[str, object]:
        """Campos comuns a partir de um livro com as relações pré-carregadas
        (ver `catalog.services.books.with_relations`)."""
        copies = None
        if book.copies_checked_at is not None and book.copies_total is not None:
            copies = CopiesOut(total=book.copies_total, available=book.copies_available or 0,
                               updated_at=book.copies_checked_at)
        return {
            "id": book.id, "title": book.title, "subtitle": book.subtitle or None,
            "authors": [link.author.name for link in book.bookauthor_set.all()],
            "year": book.year, "area_id": book.area_id,
            "course_ids": [course.slug for course in book.courses.all()],
            "genre_ids": [genre.slug for genre in book.genres.all()],
            "subjects": [subject.name for subject in book.subjects.all()],
            "synopsis": book.synopsis or None, "call_number": book.call_number or None,
            "isbn": book.isbn or None, "publisher": book.publisher or None,
            "edition": book.edition or None, "pages": book.pages,
            "document_type": book.document_type or None, "cover_url": book.cover_url or None,
            "copies": copies, "loans": book.loans_total,
        }

    @classmethod
    def from_model(cls, book: Book) -> BookSummaryOut:
        return cls(**cls.fields_from(book))


class BookDetailOut(BookSummaryOut):
    """Livro completo, para a página do título."""

    contributors: str | None
    city: str | None
    country: str | None
    volume: str | None
    series: str | None
    physical_description: str | None
    issn: str | None
    issue: str | None
    languages: list[str]
    notes: list[str]
    #: Arquivos digitais: PDF do TCC ou e-book, termo de autorização, apresentação.
    links: list[BookLinkOut]
    tcc_course: str | None
    cataloged_at: dt.date | None

    @classmethod
    def from_model(cls, book: Book) -> BookDetailOut:
        return cls(
            **cls.fields_from(book),
            contributors=book.contributors or None, city=book.city or None,
            country=book.country or None, volume=book.volume or None, series=book.series or None,
            physical_description=book.physical_description or None, issn=book.issn or None,
            issue=book.issue or None, languages=book.languages, notes=book.notes,
            links=[BookLinkOut(label=link["label"], url=link["url"]) for link in book.links],
            tcc_course=book.tcc_course or None, cataloged_at=book.cataloged_at,
        )


class BookPageOut(CamelSchema):
    items: list[BookSummaryOut]
    total: int
    page: int
    page_size: int


class SameAuthorOut(CamelSchema):
    author: str
    books: list[BookSummaryOut]


class RelatedOut(CamelSchema):
    """Leituras relacionadas: outros livros de um autor em comum (quando há ao menos
    dois) e os demais por afinidade."""

    same_author: SameAuthorOut | None
    related: list[BookSummaryOut]


# ---- recomendações
class ProfileIn(CamelSchema):
    """Preferências do visitante, como o frontend guarda no navegador. Ids
    desconhecidos são ignorados."""

    area_ids: list[str] = Field(default_factory=list, max_length=20)
    course_ids: list[str] = Field(default_factory=list, max_length=40)
    seed_book_ids: list[str] = Field(default_factory=list, max_length=20)
    genre_ids: list[str] = Field(default_factory=list, max_length=20)


class ShelfOut(CamelSchema):
    """Prateleira; `subject` completa o título (livro, área ou gênero) quando o tipo exige."""

    id: str
    kind: ShelfKind
    subject: str | None
    books: list[BookSummaryOut]


class RecommendationsOut(CamelSchema):
    shelves: list[ShelfOut]
    #: Áreas escolhidas, usadas na saudação e no filtro.
    areas: list[AreaOut]


# ---- status
class SyncOut(CamelSchema):
    finished_at: dt.datetime
    stats: dict[str, float]


class StatusOut(CamelSchema):
    active_books: int
    #: Títulos com exemplares já verificados no PHL.
    books_with_copies: int
    #: Última sincronização concluída de cada tipo; null se nunca houve.
    catalog_sync: SyncOut | None
    copies_sync: SyncOut | None
