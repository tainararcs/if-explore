"""Modelos do acervo.

A taxonomia (áreas, cursos e gêneros) é a do IF Explore e fica editável no admin;
os livros são cópias dos registros do PHL, atualizadas pela sincronização.
"""

from django.db import models
from django.db.models.functions import Upper


class KnowledgeArea(models.Model):
    """Grande área do conhecimento exibida no IF Explore."""

    slug = models.SlugField("identificador", primary_key=True, max_length=50)
    name = models.CharField("nome", max_length=100)
    order = models.PositiveSmallIntegerField("ordem", default=0)
    #: Códigos de área do CNPq (campo 085 do PHL) que caem nesta área.
    cnpq_codes = models.JSONField("códigos CNPq", default=list, blank=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "área do conhecimento"
        verbose_name_plural = "áreas do conhecimento"

    def __str__(self) -> str:
        return self.name


class CourseLevel(models.TextChoices):
    INTEGRATED = "integrated", "Técnico integrado"
    TECHNICAL = "technical", "Técnico"
    UNDERGRADUATE = "undergraduate", "Graduação"
    GRADUATE = "graduate", "Pós-graduação"


class Course(models.Model):
    """Curso do campus e como reconhecê-lo nos registros do PHL."""

    slug = models.SlugField("identificador", primary_key=True, max_length=60)
    name = models.CharField("nome", max_length=150)
    area = models.ForeignKey(KnowledgeArea, models.PROTECT, related_name="courses", verbose_name="área")
    level = models.CharField("nível", max_length=20, choices=CourseLevel.choices)
    #: Códigos do campo 079 (bibliografia do curso). O PHL não publica os nomes dos
    #: cursos: o mapeamento foi inferido pelos assuntos e precisa ser confirmado.
    phl_codes = models.JSONField("códigos no PHL", default=list, blank=True)
    #: Nomes do curso como aparecem no campo 080 dos TCCs.
    tcc_names = models.JSONField("nomes nos TCCs", default=list, blank=True)
    mapping_confirmed = models.BooleanField("mapeamento confirmado pela biblioteca", default=False)

    class Meta:
        ordering = ["level", "name"]
        verbose_name = "curso"

    def __str__(self) -> str:
        return self.name


class LiteraryGenre(models.Model):
    """Gênero literário, derivado das regras abaixo (o PHL não registra gênero).

    Um livro é do gênero quando a CDD começa com um dos prefixos, ou quando um
    assunto contém uma das palavras-chave e a CDD é literária. Com autores
    preenchidos, além disso, um dos autores precisa casar.
    """

    slug = models.SlugField("identificador", primary_key=True, max_length=50)
    name = models.CharField("nome", max_length=100)
    order = models.PositiveSmallIntegerField("ordem", default=0)
    subject_keywords = models.JSONField("palavras-chave de assunto", default=list, blank=True)
    cdd_prefixes = models.JSONField("prefixos de CDD", default=list, blank=True)
    author_keywords = models.JSONField("autores", default=list, blank=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "gênero literário"
        verbose_name_plural = "gêneros literários"

    def __str__(self) -> str:
        return self.name


class Author(models.Model):
    """Autor, único pelo nome normalizado: grafias que só diferem em acento ou caixa
    são a mesma pessoa. `name` guarda a primeira grafia vista."""

    name = models.CharField("nome", max_length=255)
    normalized_name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "autor"
        verbose_name_plural = "autores"

    def __str__(self) -> str:
        return self.name


class Subject(models.Model):
    """Assunto, único pelo nome normalizado ("NUTRIÇÃO" e "Nutrição" são um só)."""

    # Há assuntos longos no acervo (sinopses digitadas no campo errado, até ~550 caracteres).
    name = models.CharField("nome", max_length=1000)
    normalized_name = models.CharField(max_length=1000, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "assunto"

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    """Título do acervo, copiado do PHL pela sincronização diária.

    Os campos de exemplares (`copies_*`, `loans_total`) vêm de outra consulta, mais
    cara, feita em rodízio; ficam nulos até a primeira verificação do título.
    """

    #: Código do título no PHL (campo 002).
    id = models.CharField("código", primary_key=True, max_length=20)
    title = models.CharField("título", max_length=500)
    subtitle = models.CharField("subtítulo", max_length=500, blank=True)
    authors = models.ManyToManyField(Author, through="BookAuthor", related_name="books", verbose_name="autores")
    contributors = models.CharField("créditos", max_length=500, blank=True)
    publisher = models.CharField("editora", max_length=255, blank=True)
    city = models.CharField("cidade", max_length=255, blank=True)
    country = models.CharField("país", max_length=100, blank=True)
    year = models.PositiveSmallIntegerField("ano", null=True, blank=True)
    edition = models.CharField("edição", max_length=100, blank=True)
    volume = models.CharField(max_length=100, blank=True)
    series = models.CharField("série", max_length=500, blank=True)
    pages = models.PositiveIntegerField("páginas", null=True, blank=True)
    physical_description = models.CharField("descrição física", max_length=500, blank=True)
    isbn = models.CharField(max_length=13, blank=True)
    issn = models.CharField(max_length=20, blank=True)
    issue = models.CharField("fascículo", max_length=100, blank=True)
    volume_year = models.CharField("ano/volume", max_length=100, blank=True)
    cdd = models.CharField("CDD", max_length=100, blank=True)
    cutter = models.CharField(max_length=50, blank=True)
    subjects = models.ManyToManyField(Subject, related_name="books", verbose_name="assuntos")
    synopsis = models.TextField("sinopse", blank=True)
    notes = models.JSONField("notas", default=list, blank=True)
    remarks = models.TextField("observações", blank=True)
    languages = models.JSONField("idiomas", default=list, blank=True)
    medium = models.CharField("suporte", max_length=100, blank=True)
    #: Código CNPq do PHL (1 a 9); a área exibida é `area`.
    cnpq_area = models.CharField("área CNPq", max_length=2, blank=True)
    document_type = models.CharField("tipo", max_length=100, blank=True)
    bibliographic_level = models.CharField("nível bibliográfico", max_length=20, blank=True)
    phl_course_codes = models.JSONField("códigos de curso no PHL", default=list, blank=True)
    tcc_course = models.CharField("curso do TCC", max_length=255, blank=True)
    links = models.JSONField("arquivos digitais", default=list, blank=True)
    cover_url = models.URLField("capa", max_length=500, blank=True)
    cataloged_at = models.DateField("catalogado em", null=True, blank=True)
    #: Registro original do PHL, para reprocessar sem baixar de novo.
    raw = models.JSONField("registro do PHL", default=dict)

    # Derivados na sincronização a partir da taxonomia.
    area = models.ForeignKey(KnowledgeArea, models.SET_NULL, null=True, blank=True,
                             related_name="books", verbose_name="área")
    courses = models.ManyToManyField(Course, blank=True, related_name="books", verbose_name="cursos")
    genres = models.ManyToManyField(LiteraryGenre, blank=True, related_name="books", verbose_name="gêneros")

    # Exemplares (rodízio e consulta ao vivo).
    copies_total = models.PositiveSmallIntegerField("exemplares", null=True, blank=True)
    copies_available = models.PositiveSmallIntegerField("disponíveis", null=True, blank=True)
    loans_total = models.PositiveIntegerField("empréstimos", default=0)
    copies_checked_at = models.DateTimeField("exemplares verificados em", null=True, blank=True)

    #: False quando o título saiu do catálogo; o registro fica para não quebrar
    #: preferências salvas que apontem para ele.
    is_active = models.BooleanField("ativo", default=True)
    synced_at = models.DateTimeField("sincronizado em")

    class Meta:
        ordering = [Upper("title")]
        verbose_name = "livro"
        indexes = [
            models.Index(fields=["is_active", "area"], name="book_active_area_idx"),
            models.Index(fields=["document_type"], name="book_document_type_idx"),
            models.Index(fields=["year"], name="book_year_idx"),
            models.Index(fields=["isbn"], name="book_isbn_idx"),
            models.Index(fields=["-loans_total"], name="book_loans_idx"),
            models.Index(fields=["-cataloged_at"], name="book_cataloged_idx"),
            models.Index(fields=["copies_checked_at"], name="book_copies_checked_idx"),
            models.Index(fields=["synced_at"], name="book_synced_idx"),
        ]

    def __str__(self) -> str:
        return self.title

    @property
    def call_number(self) -> str:
        """Número de chamada (CDD e cutter), usado para achar o livro na estante."""
        return " ".join(part for part in (self.cdd, self.cutter) if part)


class BookAuthor(models.Model):
    """Autoria, com a posição do autor no registro."""

    book = models.ForeignKey(Book, models.CASCADE)
    author = models.ForeignKey(Author, models.CASCADE)
    position = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["position"]
        constraints = [models.UniqueConstraint(fields=["book", "author"], name="unique_book_author")]


class SyncKind(models.TextChoices):
    CATALOG = "catalog", "Catálogo"
    COPIES = "copies", "Exemplares"


class SyncStatus(models.TextChoices):
    RUNNING = "running", "Em andamento"
    SUCCESS = "success", "Concluída"
    FAILED = "failed", "Falhou"


class SyncRun(models.Model):
    """Execução de uma sincronização com o PHL, para status e monitoramento."""

    kind = models.CharField("tipo", max_length=20, choices=SyncKind.choices)
    status = models.CharField(max_length=20, choices=SyncStatus.choices, default=SyncStatus.RUNNING)
    started_at = models.DateTimeField("início", auto_now_add=True)
    finished_at = models.DateTimeField("fim", null=True, blank=True)
    stats = models.JSONField("contagens", default=dict, blank=True)
    error = models.TextField("erro", blank=True)

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "sincronização"
        verbose_name_plural = "sincronizações"
        indexes = [models.Index(fields=["kind", "-started_at"], name="syncrun_kind_started_idx")]

    def __str__(self) -> str:
        return "%s em %s (%s)" % (self.get_kind_display(), self.started_at, self.get_status_display())
