"""Tabelas do PHL Elysio: campos dos registros, códigos e grupos de busca.

Os rótulos (nomes de área, idioma, suporte) são dados exibidos ao usuário e
ficam em português, como no catálogo; as chaves usadas no código são inglesas.
"""

from __future__ import annotations

# Valor de um campo do registro: texto, lista (campos repetíveis) ou o ano já
# convertido em `year_number`.
RecordValue = str | list[str] | int | None
Record = dict[str, RecordValue]

USER_AGENT = "projeto-extensao-ifsudestemg/1.0 Núcleo de Informática - Campus Barbacena"
# Código da biblioteca no PHL, usado nos prefixos CUR=/ATE= e na consulta de exemplares.
LIBRARY_CODE = "001"
# Diretórios de scripts conhecidos, testados quando a URL não informa a versão.
KNOWN_SCRIPT_DIRS = ("phl82", "phl83", "phl84", "phl85", "phl8")

# Dicionário de campos do PHL 8.2/8.3 (manual do autor, seção "Tabela de campos").
FIELDS = {
    "001": "library", "002": "title_id", "003": "classification",
    "004": "databases", "005": "document_type", "006": "bibliographic_level",
    # O 007 (tombos) existe no manual, mas nunca vem na exportação 'phl': os
    # exemplares ficam numa base separada, acessível só pela consulta de exemplares.
    "007": "accession_numbers", "008": "electronic_medium", "010": "part_author",
    "012": "part_title", "014": "part_pages", "015": "credits",
    "016": "author", "017": "corporate_author", "018": "title",
    "019": "translated_title", "020": "pages", "021": "volume",
    "022": "medium_code", "026": "collection_type", "030": "series",
    "031": "volume_year", "032": "issue", "035": "issn",
    # Idioma: os manuais (PHL 7.01 a 8.4) documentam o idioma no campo 040 e no
    # índice IDM=, e o 039 seria "nível de descrição arquivística". Nesta base, porém,
    # a exportação entrega o código de idioma no 039, e o índice IDM= e o filtro idm=
    # dão contagens idênticas às do 039 (ex.: Francês 83 = 83). Vale o mapeamento
    # empírico; o 040 nunca aparece nos registros.
    "038": "physical_description", "039": "language_code", "040": "language_040_unused",
    "050": "thesis_institution", "051": "thesis_notes", "053": "event",
    "061": "general_notes", "062": "publisher", "063": "edition",
    "064": "year", "065": "standardized_date", "066": "city",
    "067": "country", "069": "isbn", "070": "cover_image",
    "072": "reference_count", "079": "course", "083": "abstract",
    "085": "knowledge_area", "086": "contents_notes", "087": "subjects",
    "089": "remarks", "090": "availability", "103": "cutter",
    "105": "genre", "181": "subtitle", "182": "series_subtitle",
    "186": "wiki_comments",
    # Campos locais desta instalação, fora do manual (mapeados olhando o acervo):
    # o 080 só aparece em TCCs, com o nome do curso; 084/092/096 trazem um <a href>
    # para o PDF do TCC/e-book, do termo de autorização e da apresentação. O 092
    # também guarda notas da equipe ("O LIVRO NÃO FOI ACHADO NA PRATELEIRA!").
    "080": "tcc_course", "084": "document", "092": "authorization_document",
    "096": "presentation_document",
}
REPEATABLE_FIELDS = {"004", "007", "010", "017", "030", "040", "079", "086", "087"}
# Campos cujo valor é um link: além do texto, a URL fica em `<nome>_url`.
LINK_FIELDS = {"084", "092", "096"}

# Situação do exemplar, codificada pelo nome do GIF na tela do OPAC.
COPY_STATUS_BY_GIF = {
    "002": "available", "003": "on_loan", "004": "in_library_use",
    "005": "unavailable", "016": "reserved",
}

# Grupos de tags para busca por campo (valores do <select name="tag"> do OPAC).
SEARCH_FIELD_TAGS = {
    "subject": "74,75,76,78,82,87,88", "author": "10,11,15,121,16,17,23,24",
    "date": "65", "place": "66", "title": "12,13,18,19,25,30,34,181,182",
    "publisher": "62", "course": "079",
}
# Scripts dos índices de autoridade.
AUTHORITY_INDEXES = {
    "all": "087.xis", "subjects": "085.xis", "authors": "086.xis",
    "periodicals": "088.xis", "titles": "089.xis",
}

# Área do conhecimento (campo 085), tabela do CNPq. Indexada como <biblioteca>ATE=<n>.
KNOWLEDGE_AREAS = {
    "1": "Ciências Exatas e da Terra", "2": "Ciências Biológicas",
    "3": "Engenharias", "4": "Ciências da Saúde", "5": "Ciências Agrárias",
    "6": "Ciências Sociais Aplicadas", "7": "Ciências Humanas",
    "8": "Linguística, Letras e Artes", "9": "Outros",
}
# Idioma (campo 039 nesta instalação, ver nota em FIELDS). Filtro idm=.
LANGUAGES = {
    "1": "Português", "2": "Espanhol", "3": "Inglês", "4": "Italiano",
    "5": "Francês", "6": "Alemão", "7": "Japonês", "8": "Latim", "9": "Outro",
}
# Suporte (campo 022): códigos do <select name="spt"> do OPAC, conferidos contra o
# filtro spt=. O código 9 ("Folheto") é o mais comum (60% do acervo): é o padrão de
# cadastro, não o formato físico real.
MEDIA = {
    "1": "Artigo", "4": "CD", "5": "CD-ROM", "7": "Disquete", "8": "DVD",
    "9": "Folheto", "10": "Internet", "14": "Foto", "15": "Vidro",
    "16": "Boletim", "17": "Chave", "20": "Livro didático - acervo",
    "22": "Livro didático - PNLEM", "23": "Impresso", "24": "Globo Terrestre",
    "25": "Periódico", "26": "Digital", "27": "Livro Técnico",
    "28": "Livro Literatura", "29": "Revista em Quadrinhos", "30": "Revista",
    "33": "Apostila", "34": "Fone de Ouvido", "35": "Computador Pessoal",
}
# Tipo de documento: chave usada na busca -> código do filtro tip= do OPAC.
DOCUMENT_TYPES = {
    "article": "40", "audiobook": "38", "book": "7", "bulletin": "25",
    "cd": "27", "ebook": "44", "handout": "36", "headphones": "42",
    "key": "26", "map": "9", "other": "12", "periodical": "16",
    "personal_computer": "43", "reference": "30", "thesis": "21", "video": "22",
}
# Nível bibliográfico (campo 006).
BIBLIOGRAPHIC_LEVELS = {
    "m": "monograph", "s": "serial", "as": "serial_article", "am": "monograph_part",
}
