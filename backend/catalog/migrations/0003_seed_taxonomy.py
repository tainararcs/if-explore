"""Taxonomia inicial do IF Explore: áreas, cursos e gêneros.

Áreas, cursos e gêneros são os mesmos do frontend (`src/services/mocks/taxonomy-data.ts`).
Os códigos de curso do PHL foram inferidos pelos assuntos dos livros de cada código
(ex.: o 24 traz Java, programação e banco de dados) e ficam com
`mapping_confirmed=False` até a biblioteca validar no admin. Os códigos 4, 5 e 18
não têm curso claro e ficam sem mapeamento.

As regras de gênero vêm da frequência de assuntos e CDDs no acervo (out/2026).
"""

from django.db import migrations

AREAS = [
    # (slug, nome, códigos CNPq)
    ("exact-sciences", "Ciências Exatas e da Terra", ["1"]),
    ("biological-sciences", "Ciências Biológicas", ["2"]),
    ("agricultural-sciences", "Ciências Agrárias", ["5"]),
    ("health-sciences", "Ciências da Saúde", ["4"]),
    ("humanities", "Ciências Humanas", ["7"]),
    ("applied-social-sciences", "Ciências Sociais Aplicadas", ["6"]),
    # O CNPq não tem área de computação; no acervo, "Engenharias" (3) é quase toda
    # informática (programação, redes, banco de dados).
    ("technology", "Tecnologia e Computação", ["3"]),
    ("languages-arts", "Linguagens, Letras e Artes", ["8"]),
]

COURSES = [
    # (slug, nome, área, nível, códigos no PHL, nomes nos TCCs)
    ("agroindustry-integrated", "Agroindústria", "agricultural-sciences", "integrated", [], []),
    ("agriculture-integrated", "Agropecuária", "agricultural-sciences", "integrated", [], []),
    ("food-integrated", "Alimentos", "agricultural-sciences", "integrated", [], []),
    ("hospitality-integrated", "Hospedagem", "applied-social-sciences", "integrated", [], []),
    ("chemistry-integrated", "Química", "exact-sciences", "integrated", [], []),
    ("nursing-technician", "Enfermagem", "health-sciences", "technical", ["9"], []),
    ("events-technician", "Eventos", "applied-social-sciences", "technical", [], []),
    ("it-technician", "Informática", "technology", "technical", ["7", "07"], []),
    ("environment-technician", "Meio Ambiente", "biological-sciences", "technical", [], []),
    ("workplace-safety-technician", "Segurança do Trabalho", "health-sciences", "technical", [], []),
    ("agriculture-distance", "Agropecuária (EaD)", "agricultural-sciences", "technical", [], []),
    ("administration", "Bacharelado em Administração", "applied-social-sciences", "undergraduate",
     ["85"], ["Administração"]),
    ("agronomy", "Bacharelado em Agronomia", "agricultural-sciences", "undergraduate", ["86"], ["Agronomia"]),
    ("food-technology", "Tecnologia em Alimentos", "agricultural-sciences", "undergraduate",
     ["91"], ["Tecnologia de alimentos"]),
    ("biology-teaching", "Licenciatura em Ciências Biológicas", "biological-sciences", "undergraduate",
     ["90"], ["Ciências biológicas"]),
    ("physical-education-teaching", "Licenciatura em Educação Física", "health-sciences", "undergraduate",
     ["89"], ["Educação física", "Educação da física"]),
    ("physical-education", "Bacharelado em Educação Física", "health-sciences", "undergraduate",
     ["89"], ["Educação física", "Educação da física"]),
    ("environmental-management", "Bacharelado em Gestão Ambiental", "biological-sciences", "undergraduate",
     ["21"], []),
    ("tourism-management", "Tecnologia em Gestão de Turismo", "applied-social-sciences", "undergraduate",
     ["22"], ["Gestão de Turismo"]),
    ("tourism-management-distance", "Tecnologia em Gestão de Turismo (EaD)", "applied-social-sciences",
     "undergraduate", ["22"], []),
    ("nutrition", "Bacharelado em Nutrição", "health-sciences", "undergraduate", ["92"], ["Nutrição"]),
    ("chemistry-teaching", "Licenciatura em Química", "exact-sciences", "undergraduate", ["23"], ["Química"]),
    ("internet-systems", "Tecnologia em Sistemas para Internet", "technology", "undergraduate", ["24"], []),
    ("information-systems", "Bacharelado em Sistemas de Informação", "technology", "undergraduate",
     ["117", "120"], []),
    ("protected-areas-specialization", "Especialização em Planejamento e Gestão de Áreas Naturais Protegidas",
     "biological-sciences", "graduate", [], []),
]

# Autores do cânone brasileiro, como o catálogo grafa (sobrenome, nome), sem acento.
BRAZILIAN_CLASSIC_AUTHORS = [
    "assis, machado", "alencar, jose de", "azevedo, aluisio", "azevedo, alvares de", "barreto, lima",
    "ramos, graciliano", "amado, jorge", "andrade, carlos drummond", "andrade, mario de",
    "andrade, oswald de", "rosa, joao guimaraes", "lispector, clarice", "queiroz, rachel de",
    "verissimo, erico", "bandeira, manuel", "meireles, cecilia", "moraes, vinicius de",
    "lobato, monteiro", "rego, jose lins do", "cunha, euclides da", "alves, castro",
    "dias, goncalves", "bilac, olavo", "cruz e sousa", "pompeia, raul", "almeida, manuel antonio",
    "guimaraes, bernardo", "melo neto, joao cabral", "taunay, visconde", "macedo, joaquim manuel",
    "macedo, joaquim manoel", "suassuna, ariano", "telles, lygia fagundes", "quintana, mario",
]

GENRES = [
    # (slug, nome, palavras-chave de assunto, prefixos de CDD, autores)
    ("romance", "Romance", ["romance", "novela"], [], []),
    ("adventure", "Aventura", ["aventura"], [], []),
    ("mystery", "Suspense e mistério", ["suspense", "policial", "misterio"], [], []),
    ("fantasy", "Fantasia", ["fantasia", "ficcao fantastica"], [], []),
    ("science-fiction", "Ficção científica", ["ficcao cientifica"], [], []),
    ("horror", "Terror", ["terror", "horror"], [], []),
    ("poetry", "Poesia", ["poesia", "poemas"], ["B869.1"], []),
    ("brazilian-classics", "Clássicos brasileiros", [], ["B869"], BRAZILIAN_CLASSIC_AUTHORS),
    ("biography", "Biografias e memórias", ["biografia", "autobiografia", "memorias", "diario"], ["92"], []),
    ("comics", "Quadrinhos", ["quadrinhos"], ["741.5"], []),
    ("humor", "Humor", ["humor", "humorismo"], [], []),
    ("short-stories", "Crônicas e contos", ["conto", "cronica"], [], []),
]


def seed(apps, schema_editor):
    KnowledgeArea = apps.get_model("catalog", "KnowledgeArea")
    Course = apps.get_model("catalog", "Course")
    LiteraryGenre = apps.get_model("catalog", "LiteraryGenre")
    for order, (slug, name, cnpq_codes) in enumerate(AREAS, 1):
        KnowledgeArea.objects.create(slug=slug, name=name, order=order, cnpq_codes=cnpq_codes)
    for slug, name, area, level, phl_codes, tcc_names in COURSES:
        Course.objects.create(slug=slug, name=name, area_id=area, level=level,
                              phl_codes=phl_codes, tcc_names=tcc_names)
    for order, (slug, name, keywords, cdd_prefixes, authors) in enumerate(GENRES, 1):
        LiteraryGenre.objects.create(slug=slug, name=name, order=order, subject_keywords=keywords,
                                     cdd_prefixes=cdd_prefixes, author_keywords=authors)


def unseed(apps, schema_editor):
    for model in ("Course", "LiteraryGenre", "KnowledgeArea"):
        apps.get_model("catalog", model).objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0002_book_search_index"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
