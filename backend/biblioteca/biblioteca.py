#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
biblioteca -- consulta o acervo de uma biblioteca PHL Elysio, num unico arquivo.

    from biblioteca import Biblioteca
    bib = Biblioteca("https://biblioteca.barbacena.ifsudestemg.edu.br")

    for livro in bib.buscar(titulo="python", ano=(2019, 2024)):
        print(livro)                       # Django de A a Z — SILVA, Tiago (2021)

    livro = bib.livro(isbn="978-65-86110-68-5")
    print(livro.ficha())                   # tudo sobre o livro
    livro.disponivel, livro.emprestimos    # consultam o servidor na 1a vez

    disponiveis = [l for l in bib.buscar(autor="Fowler") if l.disponivel]
    bib.buscar(titulo="python").salvar("python.csv")

Regras: um livro -> `Livro` ou None; uma busca -> `Resultado` (uma lista, vazia
se nada achou); argumento invalido -> ValueError; servidor/URL com problema ->
BibliotecaError. A matricula de quem esta com o livro nao existe nesta API.
O que consulta o servidor esta marcado; as respostas ficam em cache e ha uma
pausa entre chamadas, para ser gentil com o servidor do campus.

Mapa do arquivo (cada secao so depende das anteriores):
  1 Erros                 4 ISBN (funcoes puras)     7 Transporte  (sessao, HTTP, cache)
  2 Tabelas do PHL        5 URL e consulta (puras)   8 PHL         (buscas; `bib.phl`)
  3 Texto, numeros, datas 6 Parsers das paginas      9 Modelos     (Exemplar, Livro, Resultado)
                                                    10 Biblioteca  (a API)
As secoes 3-6 nao usam a rede e podem ser testadas com paginas de exemplo.
"""
from __future__ import annotations

import csv
import datetime as dt
import html
import http.client
import json
import re
import ssl
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any, Iterable, Optional

__all__ = ["Biblioteca", "Livro", "Exemplar", "Resultado", "PHL", "BibliotecaError", "ErroDeConexao"]

UA = "projeto-extensao-ifsudestemg/1.0 Núcleo de Informática - Campus Barbacena"
BIBLIOTECA = "001"      # codigo da biblioteca no PHL (usado em CUR=/ATE=/exemplares)
# Diretorios de scripts conhecidos, usados para descobrir a versao quando a URL nao a traz.
VERSOES_CONHECIDAS = ("phl82", "phl83", "phl84", "phl85", "phl8")


# ═══════════════════════════════════════════════════════════════════ 1. ERROS
class BibliotecaError(RuntimeError):
    """Problema com o catalogo (URL que nao e PHL, resposta de erro do servidor...)."""


class ErroDeConexao(BibliotecaError):
    """Servidor inacessivel, sem resposta ou com HTTP de erro. Subclasse de
    BibliotecaError: `except BibliotecaError` pega os dois."""


# ═══════════════════════════════════════════════════════════ 2. TABELAS DO PHL
# Dicionario de campos do PHL 8.2/8.3 (manual do autor, secao "Tabela de campos").
CAMPOS = {
    "001": "biblioteca", "002": "id_titulo", "003": "classificacao",
    "004": "bases", "005": "tipo_documento", "006": "nivel_bibliografico",
    # 007 (tombos) existe no manual, mas NUNCA vem no export 'phl': os
    # exemplares ficam numa base separada, so acessivel via exemplares().
    "007": "tombos", "008": "meio_eletronico", "010": "autor_parte",
    "012": "titulo_parte", "014": "paginas_parte", "015": "creditos",
    "016": "autor", "017": "autor_coletivo", "018": "titulo",
    "019": "titulo_traduzido", "020": "paginas", "021": "volume",
    "022": "suporte_codigo", "026": "tipo_colecao", "030": "serie",
    "031": "ano_volume", "032": "fasciculo", "035": "issn",
    # IDIOMA: todos os manuais (PHL 7.01, 8.2, 8.3, 8.4) documentam o idioma
    # no campo 040 e o indice IDM=; 039 seria "nivel de descricao
    # arquivistica". Mas nesta base o export 'phl' entrega o codigo de idioma
    # como "039", e o indice IDM= e o filtro idm= dao contagens identicas as
    # de 039 (ex.: Frances 83=83). Nao da para saber de fora se a base usa 039
    # de fato ou se e uma peculiaridade do formato de exportacao; o mapeamento
    # empirico e o que vale. O 040 nunca aparece nos registros.
    "038": "descricao_fisica", "039": "idioma_codigo", "040": "idioma_040_nao_usado",
    "050": "instituicao_tese", "051": "notas_tese", "053": "evento",
    "061": "notas_gerais", "062": "editora", "063": "edicao",
    "064": "ano", "065": "data_padronizada", "066": "cidade",
    "067": "pais", "069": "isbn", "070": "imagem_capa",
    "072": "total_referencias", "079": "curso", "083": "resumo",
    "085": "area_conhecimento", "086": "notas_conteudo", "087": "assuntos",
    "089": "observacoes", "090": "disponibilidade", "103": "cutter",
    "105": "genero", "181": "subtitulo", "182": "subtitulo_serie",
    "186": "comentarios_wiki",
    # Campos locais desta instalacao, fora do manual (mapeados olhando o acervo):
    # 080 so aparece em TCCs, com o nome do curso; 084/092/096 trazem um <a href>
    # para o PDF do TCC/e-book, do termo de autorizacao e da apresentacao. O 092
    # tambem e usado para notas da equipe ("O LIVRO NAO FOI ACHADO NA PRATELEIRA!").
    "080": "curso_tcc", "084": "documento", "092": "documento_termo",
    "096": "documento_apresentacao",
}
REPETIVEIS = {"007", "010", "017", "030", "040", "079", "086", "087", "004"}   # viram lista
# Campos cujo valor e um link: alem do texto, guardam a URL em `<nome>_url`.
CAMPOS_LINK = {"084", "092", "096"}

# Status de exemplar, codificado pelo nome do GIF na tela do OPAC.
STATUS_GIF = {"002": "disponivel", "003": "emprestado", "004": "consulta_local",
              "005": "indisponivel", "016": "reservado"}

# Grupos de tags para busca por campo (valores do <select name="tag">).
TAGS_BUSCA = {
    "assunto": "74,75,76,78,82,87,88", "autor": "10,11,15,121,16,17,23,24",
    "data": "65", "local": "66", "titulo": "12,13,18,19,25,30,34,181,182",
    "editora": "62", "curso": "079",
}
INDICES = {"todos": "087.xis", "assuntos": "085.xis", "autores": "086.xis",
           "periodicos": "088.xis", "titulos": "089.xis"}

# Area do conhecimento (campo 085), tabela CNPq. Indexada como <bib>ATE=<n>.
AREAS_CNPQ = {
    "1": "Ciências Exatas e da Terra", "2": "Ciências Biológicas",
    "3": "Engenharias", "4": "Ciências da Saúde", "5": "Ciências Agrárias",
    "6": "Ciências Sociais Aplicadas", "7": "Ciências Humanas",
    "8": "Linguística, Letras e Artes", "9": "Outros",
}
# Idioma (campo 039 nesta instalacao, ver nota em CAMPOS). Filtro idm=.
IDIOMAS = {
    "1": "Português", "2": "Espanhol", "3": "Inglês", "4": "Italiano",
    "5": "Francês", "6": "Alemão", "7": "Japonês", "8": "Latim", "9": "Outro",
}
# Suporte (campo 022): codigos do <select name="spt"> do OPAC, confirmados contra o
# filtro spt=. O codigo 9 ("Folheto") e o mais comum (60% do acervo): padrao de
# cadastro, nao o formato fisico real.
SUPORTES = {
    "1": "Artigo", "4": "CD", "5": "CD-ROM", "7": "Disquete", "8": "DVD",
    "9": "Folheto", "10": "Internet", "14": "Foto", "15": "Vidro",
    "16": "Boletim", "17": "Chave", "20": "Livro didático - acervo",
    "22": "Livro didático - PNLEM", "23": "Impresso", "24": "Globo Terrestre",
    "25": "Periódico", "26": "Digital", "27": "Livro Técnico",
    "28": "Livro Literatura", "29": "Revista em Quadrinhos", "30": "Revista",
    "33": "Apostila", "34": "Fone de Ouvido", "35": "Computador Pessoal",
}
TIPOS_DOCUMENTO = {
    "apostila": "36", "artigo": "40", "audio_livro": "38", "boletim": "25",
    "cd": "27", "chave": "26", "computador_pessoal": "43", "e-book": "44",
    "fone_de_ouvido": "42", "livro": "7", "mapa": "9", "outro": "12",
    "periodico": "16", "referencia": "30", "tese": "21", "video": "22",
}
# Nivel bibliografico (campo 006).
NIVEIS = {"m": "monografia", "s": "periodico", "as": "artigo_de_periodico",
          "am": "parte_de_monografia"}


# ═════════════════════════════════════════════════ 3. TEXTO, NUMEROS E DATAS
def _norm(txt) -> str:
    """Minusculas e sem acento, para comparar."""
    return unicodedata.normalize("NFKD", str(txt)).encode("ascii", "ignore").decode().lower()


def _um(v):
    """O primeiro item se for lista; senao o proprio valor."""
    return v[0] if isinstance(v, list) else v


def _limpa(v) -> Optional[str]:
    """Texto com espacos colapsados ('São  Paulo'); lista vira 'a / b'."""
    if isinstance(v, (list, tuple)):
        v = " / ".join(str(x) for x in v if x)
    return " ".join(str(v).split()) or None if v is not None else None


def _lista(v) -> list:
    v = [] if v is None else v if isinstance(v, (list, tuple)) else [v]
    return [" ".join(str(x).split()) for x in v if x is not None and str(x).strip()]


def _plano(v):
    """Lista vira texto 'a; b' (links viram a URL), para CSV, tabela e ficha."""
    if isinstance(v, list):
        return "; ".join(x["url"] if isinstance(x, dict) else str(x) for x in v)
    return v


def _int(v) -> Optional[int]:
    m = re.search(r"\d+", str(v if v is not None else ""))
    return int(m.group()) if m else None


def _data(v, nome) -> dt.date:
    """date/datetime, 'AAAA-MM-DD' ou 'DD/MM/AAAA'."""
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return dt.datetime.strptime(str(v).strip(), fmt).date()
        except ValueError:
            pass
    raise ValueError("%s invalida: %r (use 'AAAA-MM-DD', 'DD/MM/AAAA' ou date)" % (nome, v))


# ═══════════════════════════════════════════════════ 4. ISBN (funcoes puras)
def _isbn(v) -> str:
    """So os digitos (e o X final) de um ISBN."""
    return re.sub(r"[^0-9Xx]", "", str(v or "")).upper()


def _isbn10_para_13(d):
    base = "978" + d[:9]
    dv = (10 - sum(int(c) * (3 if i % 2 else 1) for i, c in enumerate(base)) % 10) % 10
    return base + str(dv)


def _isbn13_para_10(d):
    if not d.startswith("978"):
        return None
    nucleo = d[3:12]
    dv = (11 - sum((10 - i) * int(c) for i, c in enumerate(nucleo)) % 11) % 11
    return nucleo + ("X" if dv == 10 else str(dv))


def _hifenizacoes(d):
    """Todas as formas hifenizadas plausiveis (grupo 1-5 digitos, editor 1-7): o
    catalogo guarda o ISBN como foi digitado (metade com hifen, metade sem) e so
    acha a forma exata."""
    pref = d[:3] if len(d) == 13 else ""
    corpo, dv = d[len(pref):-1], d[-1]
    saida = set()
    for g in range(1, 6):
        for e in range(1, 8):
            if len(corpo) - g - e < 1:
                continue
            saida.add("-".join(([pref] if pref else []) + [corpo[:g], corpo[g:g + e], corpo[g + e:], dv]))
    return saida


def _formas_isbn(d):
    """(formas para buscar, digitos-alvo) de um ISBN de 10 ou 13 digitos."""
    d13 = _isbn10_para_13(d) if len(d) == 10 else d
    d10 = d if len(d) == 10 else _isbn13_para_10(d)
    formas = {d13} | ({d10} if d10 else set())
    for f in list(formas):
        formas |= _hifenizacoes(f)
    return formas, {d13, d10} - {None}


# ═══════════════════════════════════════════════ 5. URL E CONSULTA (puras)
def analisar_url(url):
    """Decompoe a URL de um catalogo PHL. Aceita a URL completa que o navegador
    mostra (`https://x.br/cgi-bin/wxis.exe?IsisScript=phl82.xis&cipar=phl82.cip&
    lang=por`) ou so o endereco do site (`x.br`, `https://x.br/`), caso em que a
    versao dos scripts e descoberta depois.

    Devolve dict: base, cgi, dir (ex.: "phl82", ou None), cipar, lang.
    Levanta ValueError se a URL for invalida.
    """
    txt = str(url or "").strip()
    if not txt:
        raise ValueError("URL vazia")
    if "://" not in txt:
        txt = "https://" + txt
    partes = urllib.parse.urlsplit(txt)
    if partes.scheme not in ("http", "https") or not partes.hostname:
        raise ValueError("URL invalida: %r (use http(s)://endereco-do-catalogo)" % url)
    base = "%s://%s" % (partes.scheme, partes.netloc)
    caminho = partes.path if "wxis" in partes.path.lower() else "/cgi-bin/wxis.exe"
    q = urllib.parse.parse_qs(partes.query)
    script = (q.get("IsisScript") or [""])[0]
    dir_ = re.match(r"([A-Za-z0-9_]+)", script).group(1) if re.match(r"[A-Za-z0-9_]+", script) else None
    return {"base": base, "cgi": base + caminho, "dir": dir_,
            "cipar": (q.get("cipar") or [None])[0] or (dir_ + ".cip" if dir_ else None),
            "lang": (q.get("lang") or ["por"])[0]}


def _limpar_consulta(exp, modo):
    """Prepara o texto digitado para o ISIS. Pontuacao colada em palavra zera a busca:
    'Fowler, Martin' (como vem numa referencia ABNT), 'fowler.', 'fowler;' -> 0
    resultados, enquanto 'Martin Fowler' acha 4. Fora do modo 'exp' (onde o usuario
    escreve operadores de proposito) faz, portanto:
      * NFKC: acento decomposto (macOS, PDF) e caracteres largos viram os normais;
      * simbolos e pontuacao nao-ASCII (aspas curvas, travessao, emoji) e caracteres de
        controle viram espaco -- o servidor so entende latin-1 e os trocaria por '?';
      * tira pontuacao das bordas das palavras; virgula, ponto-e-virgula e dois-pontos
        viram espaco; 'agro*' vira 'agro$' (truncamento do ISIS);
      * descarta palavras feitas so de '$'/'*': sozinhas casariam o acervo inteiro.
    Pontuacao interna ('ASP.NET', 'C#', "D'Imperio") e preservada. O '+' nao e tocado: e
    operador OU e nao ha como escapa-lo. No modo 'exp' so normaliza para NFC."""
    if exp is None:
        return exp
    exp = unicodedata.normalize("NFC" if modo == "exp" else "NFKC", str(exp))
    if modo == "exp":
        return exp
    exp = "".join(" " if ord(c) < 32 or ord(c) == 127 or (not c.isascii() and not c.isalnum()) else c for c in exp)
    exp = re.sub(r"[,;:!?\[\]/()\\]", " ", exp)
    palavras = []
    for w in exp.split():
        w = w.strip(",.;:!?[]/'-\"")
        if w.endswith("*"):
            w = w.rstrip("*") + "$"
        if w.strip("$"):
            palavras.append(w)
    return " ".join(palavras)


def _exigir_expressao(exp):
    """exp="" e tratada pelo ISIS como 'sem filtro' (casa tudo) e devolve registros
    arbitrarios sem avisar -- ja causou um bug real (livro("") devolvia um livro ao
    acaso). Barra cedo. Tambem barra consultas enormes: o servidor responde HTTP 414."""
    if exp is None or not str(exp).strip():
        raise ValueError("expressao de busca vazia: o ISIS trata '' como 'sem filtro' "
                         "e devolve registros arbitrarios em vez de nada. Use '$' "
                         "(com modo=\"exp\") se a intencao e mesmo buscar tudo.")
    if len(str(exp)) > 4000:
        raise ValueError("consulta longa demais (%d caracteres; maximo 4000)" % len(str(exp)))
    return exp


# ═════════════════════════════════════════════ 6. PARSERS (pagina -> dados)
def _parse_registros(pagina, base):
    """O formato 'phl' imprime '<hr>001: v<br>002: v<br>...' por registro."""
    regs = []
    for bloco in pagina.split("<hr>")[1:]:
        pares = re.findall(r"(\d{3}):\s*(.*?)(?=<br>|$)", bloco.split("</td>")[0])
        if not pares:
            continue
        reg = {}

        def guardar(nome, valor, lista):
            if lista or nome in reg:
                reg.setdefault(nome, [])
                if not isinstance(reg[nome], list):
                    reg[nome] = [reg[nome]]
                reg[nome].append(valor)
            else:
                reg[nome] = valor

        for tag, valor in pares:
            nome = CAMPOS.get(tag, "campo_%s" % tag)
            if tag in CAMPOS_LINK:
                # o href se perderia ao tirar as tags. Ha links quebrados no acervo
                # ('href="...tccs/.pdf>' sem aspas de fechamento, ou arquivo sem
                # nome): esses ficam so com o texto.
                link = re.search(r'<a\s[^>]*href="([^"]+)"', valor, re.I)
                url = html.unescape(link.group(1)).strip() if link else ""
                if url and not url.endswith("/.pdf"):
                    # o cadastro grava 'http://', mas o servidor so responde em https:
                    # no mesmo host, usa o esquema do catalogo
                    partes = urllib.parse.urlsplit(urllib.parse.urljoin(base + "/", url))
                    if partes.netloc == urllib.parse.urlsplit(base).netloc:
                        partes = partes._replace(scheme=urllib.parse.urlsplit(base).scheme)
                    guardar(nome + "_url", urllib.parse.quote(partes.geturl(), safe=":/?&=#%~+,;@"), False)
            valor = html.unescape(re.sub(r"<[^>]+>", "", valor)).strip()
            if valor:
                guardar(nome, valor, tag in REPETIVEIS)
        if "imagem_capa" in reg:
            reg["imagem_capa"] = base + reg["imagem_capa"]
        _preencher_titulo_autor(reg)
        _normalizar_ano(reg)
        regs.append(reg)
    return regs


def _normalizar_ano(reg):
    """`ano` (064) e texto livre: so 83% tem 4 digitos exatos; o resto sao '[s.d.]',
    'jan.2014', '2.sem.2021', '2019/2020', '20110000', '[19..]'. `ano_num` e o
    primeiro ano plausivel (int) ou None -- use-o no lugar de int(reg["ano"]), que
    quebra em ~17% dos registros."""
    v = _um(reg.get("ano")) or ""
    m = re.search(r"(?<!\d)(1[5-9]\d\d|20\d\d)(?!\d)", v) or re.fullmatch(r"((?:1[5-9]|20)\d\d)0000", v)
    reg["ano_num"] = int(m.group(1)) if m else None


def _preencher_titulo_autor(reg):
    """~11% do acervo (fasciculos NIV=s, artigos NIV=as/am) nao usa os campos
    018/016 (titulo/autor): guarda o titulo em 030 (serie) ou 012 (titulo_parte), e
    o autor em 010 (autor_parte). Sem isso `titulo` ficaria ausente em ~2200
    registros. Mantem os campos originais e so preenche quando realmente ausentes."""
    if not reg.get("titulo"):
        alt = reg.get("titulo_parte") or reg.get("serie")
        if alt:
            reg["titulo"] = _um(alt)
    if not reg.get("autor"):
        alt = reg.get("autor_parte") or reg.get("autor_coletivo")
        if alt:
            reg["autor"] = alt


def _parse_exemplares(pagina, com_usuario=False):
    """Pagina de status de um titulo -> um dict por exemplar. Cada exemplar vem numa
    tabela propria (marcada por FMX000152) e o status e o nome do GIF."""
    linhas = []
    for bloco in pagina.split("FMX000152")[1:]:
        linhas.extend(re.findall(r"<tr>(.*?)(?=<tr>|</table>)", bloco, re.S))
    itens = []
    for linha in linhas:
        celulas = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip()
                   for c in re.findall(r"<td[^>]*>(.*?)</td>", linha, re.S)]
        gif = re.search(r"/img/(\d{3})\.gif", linha)
        if not celulas or not gif:
            continue
        celulas += [""] * (8 - len(celulas))
        item = {"tombo": celulas[0], "observacao": celulas[1], "etiqueta": celulas[2],
                "status": STATUS_GIF.get(gif.group(1), "desconhecido"),
                "devolucao": celulas[4], "usuario": celulas[5],
                "emprestimos": celulas[6], "renovacoes": celulas[7]}
        if not com_usuario:         # a tela mostra a MATRICULA de quem esta com o livro
            item.pop("usuario")
        itens.append(item)
    return itens


def _parse_referencias(xml):
    """Pagina do formato 'referencia' (XML) -> (total em <hits> ou None, itens). Um
    registro sem <mfn> ou <ref> (resposta truncada/corrompida) levanta BibliotecaError,
    em vez de pular (desalinharia a paginacao) ou quebrar com TypeError."""
    hits = re.search(r"<hits>(\d+)</hits>", xml)
    itens = []
    for r in re.findall(r"<reg>(.*?)</reg>", xml, re.S):
        mfn, ref = re.search(r"<mfn>\s*(\d+)", r), re.search(r"<ref>(.*?)</ref>", r, re.S)
        if not (mfn and ref):
            raise BibliotecaError("resposta do servidor em formato inesperado (registro sem <mfn> ou <ref>)")
        tira = lambda t, r=r: html.unescape(re.sub(
            r"<[^>]+>", "", (re.search(r"<%s>(.*?)</%s>" % (t, t), r, re.S) or [None, ""])[1])).strip()
        ex = re.search(r"<e>\s*(\d+)\s*Ex", r)
        itens.append({
            "mfn": int(mfn.group(1)), "autor": tira("a"), "titulo": tira("b").rstrip(": ").strip(),
            "referencia": html.unescape(re.sub(r"\s+", " ", re.sub(r"<e>.*?</e>|<[^>]+>", "", ref[1]))).strip(),
            "exemplares_aprox": int(ex.group(1)) if ex else None,
        })
    return (int(hits.group(1)) if hits else None), itens


# ════════════════════════════════════════════════ 7. TRANSPORTE (sessao e HTTP)
class Transporte:
    """Sessao e HTTP do WWWisis: monta as URLs em ISO-8859-1, abre e renova a
    sessao (`tmp`), tenta de novo, faz cache e pausa. Nao sabe nada de busca."""

    def __init__(self, url, pausa=0.5, timeout=60, cache_ttl=0):
        """`url`: site do catalogo ou URL completa do navegador (ver analisar_url).
        `pausa`: cortesia entre requisicoes, em segundos. `cache_ttl`: segundos que
        uma resposta identica fica em cache (0 = sem)."""
        info = analisar_url(url)
        self.base, self.cgi, self.dir = info["base"], info["cgi"], info["dir"]   # dir None = descobrir
        self.cipar, self.lang = info["cipar"], info["lang"]
        self.pausa, self.timeout, self.cache_ttl = pausa, timeout, cache_ttl
        self._cache, self.tmp = {}, None

    @property
    def script(self):
        """Script de busca (`<dir>/003.xis`); descobre a versao se preciso."""
        if self.dir is None:
            self.abrir_sessao()
        return "%s/003.xis" % self.dir

    def _get(self, params):
        if self.tmp is None:
            self.abrir_sessao()
        for tentativa in (1, 2):
            p = dict(params)
            p.setdefault("tmp", self.tmp)
            # o WWWisis so entende ISO-8859-1: em UTF-8 ele devolve zero resultados,
            # em silencio, para qualquer termo acentuado.
            url = self.cgi + "?" + urllib.parse.urlencode(p, encoding="iso-8859-1", errors="replace")
            try:
                return self._raw(url)
            except ErroDeConexao:
                raise
            except BibliotecaError as e:
                # sessao (tmp) expirada: o servidor responde 'dbxopen'. Abre outra e repete uma vez.
                if tentativa == 1 and "dbxopen" in str(e) and "tmp" not in params:
                    self.tmp = None
                    self.abrir_sessao()
                    continue
                raise

    def _raw(self, url, tentativas=2, cache=True):
        usar_cache = cache and self.cache_ttl > 0
        if usar_cache:
            hit = self._cache.get(url)
            if hit and time.time() - hit[0] < self.cache_ttl:
                return hit[1]
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        erro = None
        for i in range(tentativas):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    bruto = r.read()
                break
            except urllib.error.HTTPError as e:
                if e.code < 500:      # 404/403...: repetir nao adianta
                    raise ErroDeConexao("o servidor respondeu HTTP %d para %s -- confira a URL do "
                                        "catalogo" % (e.code, self.cgi)) from None
                erro = e
            except (urllib.error.URLError, TimeoutError, ConnectionError, ssl.SSLError, http.client.HTTPException) as e:
                erro = e
            if i + 1 < tentativas:
                time.sleep(1.0)
        else:
            # expressoes booleanas muito compostas (varios "^" encadeados contra a base
            # inteira) podem fazer o WWWisis nao responder no prazo: e do motor ISIS.
            raise ErroDeConexao("sem resposta de %s apos %d tentativa(s) (%s). Se a expressao de "
                                "busca for muito complexa (varios '^' encadeados), tente "
                                "simplifica-la." % (self.base, tentativas, erro))
        time.sleep(self.pausa)
        texto = bruto.decode("iso-8859-1")
        # o WWWisis as vezes antepoe uma quebra de linha ao erro ("\nWXIS|fatal error|..."):
        # sem lstrip, sessao expirada virava "0 resultados" mudo.
        if texto.lstrip().startswith("WXIS|"):
            raise BibliotecaError(texto.strip())
        if usar_cache and len(bruto) < 1000000:
            if len(self._cache) >= 200:   # ponytail: despejo FIFO simples; LRU se a taxa de acerto importar
                self._cache.pop(next(iter(self._cache)))
            self._cache[url] = (time.time(), texto)
        return texto

    def abrir_sessao(self):
        """Pega um id de sessao (/tmp/fileXXXXXX) na pagina inicial do catalogo. Se a
        versao dos scripts nao foi informada, testa as conhecidas."""
        candidatos = [self.dir] if self.dir else list(VERSOES_CONHECIDAS)
        for d in candidatos:
            cipar = self.cipar if self.dir else d + ".cip"
            url = "%s?IsisScript=%s.xis&cipar=%s&lang=%s" % (self.cgi, d, cipar, self.lang)
            try:
                texto = self._raw(url, cache=False)
            except ErroDeConexao:
                raise
            except BibliotecaError:
                continue                        # script inexistente: proximo
            m = re.search(r"tmp=(/tmp/file[A-Za-z0-9]+)", texto)
            if m:
                self.dir, self.cipar, self.tmp = d, cipar, m.group(1)
                return self.tmp
        raise BibliotecaError("%s nao parece ser um catalogo PHL (nao consegui abrir uma sessao%s). "
                              "Confira a URL." % (self.base, "" if self.dir is None else
                                                  " com IsisScript=%s.xis" % candidatos[0]))


# ════════════════════════════════════════════════════ 8. PHL (cliente de busca)
class PHL(Transporte):
    """Cliente de baixo nivel do OPAC: busca crua, exemplares, referencias, indices.
    Devolve dicts do PHL (campos ja com nome). E o `bib.phl` de uma `Biblioteca`;
    prefira a API `Biblioteca` no dia a dia."""

    # ---- busca
    def _params_busca(self, exp, modo="and", campo=None, tipo=None, idioma=None,
                      suporte=None, rpp=50, inicio=1, pft="phl"):
        p = {"IsisScript": self.script, "opc": pft, "pft": pft,
             "bool": modo, "exp": exp, "rpp": str(rpp), "from": str(inicio)}
        if campo:
            p["tag"] = TAGS_BUSCA.get(campo, campo)
        if tipo:
            p["tip"] = TIPOS_DOCUMENTO.get(tipo, tipo)
        if idioma:
            p["idm"] = idioma
        if suporte:
            p["spt"] = suporte
        return p

    def _preparar(self, exp, modo):
        return _exigir_expressao(_limpar_consulta(exp, modo))

    def contar(self, exp, modo="and", **kw):
        """Total de registros de uma expressao (le o 'n/total' do formato decorado)."""
        exp = self._preparar(exp, modo)
        m = re.search(r">\d+/(\d+)<", self._get(self._params_busca(exp, modo, rpp=1, pft="decorado", **kw)))
        return int(m.group(1)) if m else 0

    def buscar(self, exp, modo="and", rpp=50, inicio=1, **kw):
        """Uma pagina de resultados, ja parseada em dicts."""
        exp = self._preparar(exp, modo)
        return _parse_registros(self._get(self._params_busca(exp, modo, rpp=rpp, inicio=inicio, **kw)), self.base)

    def buscar_tudo(self, exp, modo="and", pagina=5000, limite=None, **kw):
        """Itera sobre todos os resultados, paginando com `from`. `pagina` (registros por
        requisicao): testado ao vivo ate 25000 numa chamada (acervo inteiro, ~8 s, sem
        duplicatas); poucas requisicoes grandes sao mais gentis com o CGI (um processo
        por requisicao) que muitas pequenas."""
        if pagina < 1:
            raise ValueError("pagina deve ser >= 1 (recebi %r)" % (pagina,))
        total = limite if limite is not None else self.contar(exp, modo, **kw)
        lidos = 0
        while lidos < total:
            lote = self.buscar(exp, modo, rpp=min(pagina, total - lidos), inicio=lidos + 1, **kw)
            if not lote:
                break
            yield from lote
            lidos += len(lote)

    def por_mfns(self, mfns, pagina=50):
        """Varios registros de uma vez: 'MFN=a + MFN=b + ...' (OU do ISIS)."""
        mfns, regs = list(mfns), []
        for i in range(0, len(mfns), pagina):
            lote = mfns[i:i + pagina]
            regs.extend(self.buscar(" + ".join("MFN=%s" % m for m in lote), modo="exp", rpp=len(lote)))
        return regs

    def por_isbn(self, isbn):
        """Livros com esse ISBN, em qualquer formato de entrada. A busca simples so acha
        o ISBN escrito exatamente como foi cadastrado; aqui: normaliza, gera as formas
        10/13 e todas as hifenizacoes plausiveis, busca tudo numa requisicao (OU) e
        confere o resultado no cliente (digitos iguais), sem falso positivo."""
        d = _isbn(isbn)
        if len(d) not in (10, 13):
            raise ValueError("ISBN deve ter 10 ou 13 digitos (recebi %d)" % len(d))
        formas, alvo = _formas_isbn(d)
        exp = " + ".join('"%s"' % f for f in sorted(formas))
        return [r for r in self.buscar(exp, modo="exp", rpp=50)
                if any(_isbn(x) in alvo for x in _lista(r.get("isbn")))]

    def por_tombo(self, tombo):
        """Titulo a que pertence um exemplar, pelo numero de tombo (prefixo TBO=)."""
        t = str(tombo).strip()
        if not t.isdigit():
            raise ValueError("tombo deve ser numerico (recebi %r)" % tombo)
        regs = self.buscar("TBO=%s" % t, modo="exp", rpp=1)
        return regs[0] if regs else None

    # ---- feeds e datas
    def aquisicoes_do_mes(self):
        """Feed 'Aquisicoes do Mes' do menu do OPAC. opc=sdi ignora o pft e devolve sempre
        o HTML decorado; dele extraimos os MFN e buscamos os registros no formato phl."""
        pagina = self._get({"IsisScript": self.script, "cipar": self.cipar,
                            "opc": "sdi", "pft": "decorado", "lang": "por"})
        return self.por_mfns(dict.fromkeys(re.findall(r'value="MFN=(\d+)"', pagina)))

    def catalogados_entre(self, inicio, fim=None, **kw):
        """Registros do catalogo com data entre duas datas (aaaammdd, inclusive).

        O campo 065 (`data_padronizada`) NAO e a data de publicacao (um livro de 1994
        aparece com 20080709): e a data em que o REGISTRO foi criado ou salvo. O indice
        DTP= so guarda o ANO dessa data, entao busca-se por ano e filtra-se a data aqui.
        065 mistura dois usos: em 92% dos registros e a data de entrada completa; em ~6%
        e o ANO DE PUBLICACAO com AAAA0000 (ex.: 20210000). Datas terminadas em "00" nao
        sao data de entrada: ficam fora. Nao e identico a aquisicoes_do_mes(): la o
        servidor usa outro criterio (provavelmente a aquisicao dos exemplares)."""
        inicio = str(inicio).replace("-", "")
        fim = str(fim).replace("-", "") if fim else time.strftime("%Y%m%d")
        anos, regs = list(range(int(inicio[:4]), int(fim[:4]) + 1)), []
        for i in range(0, len(anos), 200):      # um OU de anos por consulta (antes: 2 requisicoes por ano)
            regs.extend(self.buscar_tudo(" + ".join("DTP=%d" % a for a in anos[i:i + 200]), modo="exp", **kw))
        data = lambda r: _um(r.get("data_padronizada")) or ""
        return sorted((r for r in regs if not data(r).endswith("00") and inicio <= data(r) <= fim), key=data)

    # ---- exemplares e referencias
    def exemplares(self, id_titulo, biblioteca=BIBLIOTECA, com_usuario=False):
        """Situacao de cada exemplar (tombo, etiqueta, status, devolucao, emprestimos).
        A tela do OPAC mostra a MATRICULA de quem esta com o livro; por ser dado
        pessoal, o campo `usuario` so vem com com_usuario=True."""
        return _parse_exemplares(self._get({"IsisScript": self.script, "opc": "status_tit",
                                            "tit": id_titulo, "acv": biblioteca}), com_usuario)

    def referencias(self, exp="$", modo="exp", pagina=5000, limite=None, **kw):
        """Itera referencias bibliograficas ja formatadas pelo servidor -- o formato mais
        leve do OPAC (opc=referencia, XML): ~4000 registros em ~1,6 s.

        Cada item: {mfn, autor, titulo, referencia (texto ABNT pronto), exemplares_aprox}.
        ATENCAO: o numero de exemplares aqui e APROXIMADO (divergiu de exemplares() em 3
        de 20264 titulos). Traz o total em <hits>, pagina por `from` e renderiza ate os
        registros-esqueleto (sem campo 001). NAO traz id_titulo: so o MFN."""
        exp = self._preparar(exp, modo)
        inicio, total = 1, None
        while total is None or inicio <= total:
            if limite is not None and inicio > limite:
                return
            pedido = pagina if limite is None else min(pagina, limite - inicio + 1)
            hits, itens = _parse_referencias(self._get(self._params_busca(
                exp, modo, rpp=pedido, inicio=inicio, pft="referencia", **kw)))
            if total is None:
                total = hits or 0
            if not itens:
                return
            yield from itens
            inicio += len(itens)

    def referencia_abnt(self, id_titulo):
        """Referencia bibliografica pronta ('POLYA, G. A arte de resolver problemas: ...
        Rio de Janeiro: Interciencia, 1994. 179 p.'), ou None se o titulo nao existe."""
        r = next(iter(self.referencias("TIT=%s" % id_titulo, limite=1)), None)
        return (r["referencia"] or None) if r else None

    # ---- indices de autoridade
    def indice(self, qual, prefixo):
        """Navega nos indices (autoridades): assuntos, autores, titulos... (10 por vez)."""
        pagina = self._get({"IsisScript": "%s/%s" % (self.script.split("/")[0], INDICES.get(qual, qual)),
                            "exp": prefixo})
        return [l.strip() for l in re.sub(r"<[^>]+>", "", pagina).splitlines() if l.strip()]

    def sugerir(self, termo, qual="todos", tentativas=6):
        """'Voce quis dizer?' sobre o indice de autoridades. O indice e um cursor B-tree: um
        erro DEPOIS do ponto certo ('chiavenatto', que ordena depois de 'chiavenato') cai
        depois da entrada correta e nao a encontra. Por isso encurta o termo ate achar
        entradas que comecem com o prefixo (sem acento/caixa). [] se nada parecido existe."""
        t = str(termo).strip()
        if not t:
            raise ValueError("termo vazio")
        for n in range(len(t), max(1, len(t) // 2) - 1, -1)[:tentativas]:
            achados = [e for e in self.indice(qual, t[:n]) if _norm(e).startswith(_norm(t[:n]))]
            if achados:
                return achados
        return []


# ═════════════════════════════════════════════════════ 9. MODELOS (dados prontos)
@dataclass(frozen=True)
class Exemplar:
    """Um exemplar fisico. Nao guarda quem esta com ele (dado pessoal)."""
    tombo: str
    etiqueta: str
    situacao: str            # disponivel | emprestado | consulta_local | indisponivel | reservado
    devolucao: Optional[dt.date]
    emprestimos: int
    renovacoes: int
    observacao: Optional[str] = None

    @classmethod
    def _de_dict(cls, e: dict) -> "Exemplar":
        try:
            dev = dt.datetime.strptime(e.get("devolucao") or "", "%d/%m/%Y").date()
        except ValueError:
            dev = None
        return cls(e["tombo"], e["etiqueta"], e["status"], dev,
                   _int(e["emprestimos"]) or 0, _int(e["renovacoes"]) or 0,
                   _limpa(e.get("observacao")))

    @property
    def disponivel(self) -> bool:
        return self.situacao == "disponivel"

    def __str__(self):
        s = {"disponivel": "disponível", "indisponivel": "indisponível"}.get(
            self.situacao, self.situacao.replace("_", " "))
        return "%-7s %-32s %s%s" % (self.tombo, self.etiqueta, s,
                                    " (devolução %s)" % self.devolucao.strftime("%d/%m/%Y")
                                    if self.devolucao else "")


@dataclass(eq=False, repr=False)
class Livro:
    """Um titulo do acervo, com tipos previsiveis: `autores`, `assuntos`, `idiomas`,
    `notas_conteudo`, `notas`, `curso_codigos` e `links` sao sempre listas; `ano` e
    `paginas` sao int ou None; `catalogado_em` e date ou None; texto ausente e None.
    `links` sao os arquivos digitais ({"rotulo", "url"}): PDF de TCC/e-book, termo de
    autorizacao, apresentacao. `bruto` guarda o registro original do PHL.

    `exemplares`, `disponivel`, `disponiveis`, `emprestimos` e `referencia` consultam o
    servidor na primeira vez e ficam guardados no objeto."""
    id: str
    titulo: str
    subtitulo: Optional[str]
    autores: list
    creditos: Optional[str]
    editora: Optional[str]
    cidade: Optional[str]
    pais: Optional[str]
    ano: Optional[int]
    edicao: Optional[str]
    volume: Optional[str]
    serie: Optional[str]
    paginas: Optional[int]
    descricao_fisica: Optional[str]
    isbn: Optional[str]
    issn: Optional[str]
    fasciculo: Optional[str]
    ano_volume: Optional[str]
    cdd: Optional[str]
    cutter: Optional[str]
    assuntos: list
    notas_conteudo: list
    notas: list
    observacoes: Optional[str]
    idiomas: list
    suporte: Optional[str]
    area: Optional[str]
    tipo: Optional[str]
    nivel: Optional[str]
    curso_codigos: list
    curso_tcc: Optional[str]
    links: list
    capa: Optional[str]
    catalogado_em: Optional[dt.date]
    bruto: dict
    _bib: Any

    @classmethod
    def _de_registro(cls, r: dict, bib: "Biblioteca") -> "Livro":
        # 065 e a data de entrada em ~92% dos registros; em ~6% e so o ano (AAAA0000)
        d = _um(r.get("data_padronizada")) or ""
        try:
            entrada = dt.date(int(d[:4]), int(d[4:6]), int(d[6:])) if re.fullmatch(r"\d{8}", d) and d[6:] != "00" else None
        except ValueError:
            entrada = None
        isbns = [x for x in map(_isbn, _lista(r.get("isbn"))) if x]
        # o texto do link e "TCC (Clique aqui)": o rotulo fica so "TCC"
        rotulo = lambda campo, padrao: re.sub(r"(?i)clique aqui", "", _limpa(r.get(campo)) or "").strip("() ") or padrao
        links = [{"rotulo": rotulo(campo, padrao), "url": url}
                 for campo, padrao in (("documento", "Documento"), ("documento_termo", "Termo de autorização"),
                                       ("documento_apresentacao", "Apresentação"))
                 for url in _lista(r.get(campo + "_url"))]
        # sem link, o 092 e uma nota da equipe ("Acompanha CD", "NÃO POSSUI IMAGEM!"),
        # exceto quando e o rotulo de um link quebrado ("Termo de Autorização")
        notas = _lista(r.get("notas_gerais")) + [
            n for n in ([] if r.get("documento_termo_url") else _lista(r.get("documento_termo")))
            if not _norm(n).startswith("termo de autorizacao")]
        return cls(
            id=r["id_titulo"], titulo=_limpa(r.get("titulo")) or "(sem título)",
            subtitulo=_limpa(r.get("subtitulo")), autores=_lista(r.get("autor")),
            creditos=_limpa(r.get("creditos")),
            editora=_limpa(r.get("editora")), cidade=_limpa(r.get("cidade")),
            pais=_limpa(r.get("pais")), ano=r.get("ano_num"), edicao=_limpa(r.get("edicao")),
            volume=_limpa(r.get("volume")), serie=_limpa(r.get("serie")),
            paginas=_int(r.get("paginas")), descricao_fisica=_limpa(r.get("descricao_fisica")),
            isbn=isbns[0] if isbns else None, issn=_limpa(r.get("issn")),
            fasciculo=_limpa(r.get("fasciculo")), ano_volume=_limpa(r.get("ano_volume")),
            cdd=_limpa(r.get("classificacao")), cutter=_limpa(r.get("cutter")),
            assuntos=_lista(r.get("assuntos")), notas_conteudo=_lista(r.get("notas_conteudo")),
            notas=notas, observacoes=_limpa(r.get("observacoes")),
            idiomas=list(dict.fromkeys(IDIOMAS.get(c, c) for c in _lista(r.get("idioma_codigo")))),
            suporte=SUPORTES.get(_um(r.get("suporte_codigo"))),
            area=AREAS_CNPQ.get(_um(r.get("area_conhecimento"))),
            tipo=_limpa(r.get("tipo_documento")), nivel=NIVEIS.get(_um(r.get("nivel_bibliografico"))),
            # ~30 registros tem texto digitado no campo de curso (sinopses, assuntos): so
            # codigos numericos sao cursos.
            curso_codigos=[c for c in _lista(r.get("curso")) if c.isdigit()],
            curso_tcc=_limpa(r.get("curso_tcc")), links=links,
            capa=_limpa(r.get("imagem_capa")), catalogado_em=entrada, bruto=r, _bib=bib)

    # ---- derivados (sem rede)
    @property
    def titulo_completo(self) -> str:
        return "%s: %s" % (self.titulo, self.subtitulo) if self.subtitulo else self.titulo

    @property
    def chamada(self) -> str:
        """Numero de chamada (CDD + cutter), ex.: '005.133 PYTHON S586d'."""
        return " ".join(x for x in (self.cdd, self.cutter) if x)

    @property
    def sinopse(self) -> Optional[str]:
        """Notas de conteudo: em muitos livros a sinopse da editora, em outros o sumario."""
        return " ".join(self.notas_conteudo) or None

    # ---- consultam o servidor (1a vez)
    @cached_property
    def exemplares(self) -> list:
        return [Exemplar._de_dict(e) for e in self._bib.phl.exemplares(self.id, BIBLIOTECA)]

    @cached_property
    def referencia(self) -> Optional[str]:
        """Referencia bibliografica pronta, gerada pelo servidor."""
        return self._bib.phl.referencia_abnt(self.id)

    @property
    def disponiveis(self) -> int:
        return sum(e.disponivel for e in self.exemplares)

    @property
    def disponivel(self) -> bool:
        return self.disponiveis > 0

    @property
    def emprestimos(self) -> int:
        """Total de emprestimos ja feitos (so o total: nao ha datas nem quem pegou)."""
        return sum(e.emprestimos for e in self.exemplares)

    # ---- apresentacao
    def para_dict(self, exemplares: bool = False) -> dict:
        """Dict pronto para JSON; `exemplares=True` inclui exemplares, `disponiveis` e
        `emprestimos` (consulta o servidor)."""
        d = {k: getattr(self, k) for k in (
            "id", "titulo", "subtitulo", "autores", "creditos", "editora", "cidade", "pais", "ano",
            "edicao", "volume", "serie", "paginas", "descricao_fisica", "isbn", "issn", "fasciculo",
            "ano_volume", "cdd", "cutter", "assuntos", "idiomas", "suporte", "area", "tipo", "nivel",
            "curso_codigos", "curso_tcc", "links", "capa", "sinopse", "notas", "observacoes")}
        d["catalogado_em"] = self.catalogado_em.isoformat() if self.catalogado_em else None
        if exemplares:
            d["exemplares"] = [dict(vars(e), devolucao=e.devolucao and e.devolucao.isoformat())
                               for e in self.exemplares]
            d["disponiveis"], d["emprestimos"] = self.disponiveis, self.emprestimos
        return d

    def ficha(self) -> str:
        """Texto com tudo sobre o livro (consulta o servidor: exemplares e referencia)."""
        d = self.para_dict()
        d["referencia"] = self.referencia
        linhas = [self.titulo_completo, "─" * min(80, len(self.titulo_completo))]
        linhas += ["%-14s %s" % (k + ":", _plano(v))
                   for k, v in d.items() if v not in (None, "", []) and k not in ("titulo", "subtitulo")]
        ex = self.exemplares
        linhas.append("exemplares:   %d (%d disponíveis, %d empréstimo(s) no total)"
                      % (len(ex), self.disponiveis, self.emprestimos))
        return "\n".join(linhas + ["  " + str(e) for e in ex])

    def __str__(self):
        return "%s — %s%s" % (self.titulo, "; ".join(self.autores) or "s/ autor",
                              " (%d)" % self.ano if self.ano else "")

    def __repr__(self):
        return "Livro(id=%r, titulo=%r, ano=%r)" % (self.id, self.titulo, self.ano)

    def __eq__(self, o):
        return isinstance(o, Livro) and o.id == self.id

    def __hash__(self):
        return hash(self.id)


COLUNAS_LIVRO = frozenset(
    [k for k in Livro.__dataclass_fields__ if not k.startswith("_") and k != "bruto"] +
    [k for k, v in vars(Livro).items() if not k.startswith("_") and not callable(v)])


class Resultado(list):
    """Lista de `Livro`. `total`: quantos livros correspondem ao todo; `truncado`: True
    se `limite` deixou algum de fora."""

    def __init__(self, livros: Iterable[Livro] = (), *, total: Optional[int] = None, truncado: bool = False):
        super().__init__(livros)
        self.total, self.truncado = total, truncado

    def __repr__(self):
        return "<Resultado: %d livro(s)%s>" % (len(self), ", truncado (total %s)" % self.total if self.truncado else "")

    def tabela(self, colunas=("titulo", "autores", "ano", "editora"), largura: int = 60) -> str:
        """Tabela Markdown; `colunas` sao atributos de Livro ('isbn', 'cdd', 'disponiveis'...).
        Coluna desconhecida levanta ValueError -- inclusive com a lista vazia, onde antes
        passava batido e so quebrava quando houvesse resultado."""
        for c in colunas:
            if c not in COLUNAS_LIVRO:
                raise ValueError("coluna %r desconhecida. Opcoes: %s" % (c, ", ".join(sorted(COLUNAS_LIVRO))))

        def fmt(v):
            v = _plano(v)
            v = "—" if v in (None, "") else str(v).replace("|", "\\|").replace("\n", " ")
            return v if len(v) <= largura else v[:largura - 1] + "…"
        rot = {"titulo": "Título", "autores": "Autor(es)", "isbn": "ISBN", "cdd": "CDD", "paginas": "Págs.", "id": "Código"}
        linhas = ["| # | " + " | ".join(rot.get(c, c.capitalize()) for c in colunas) + " |", "|--:|" + "---|" * len(colunas)]
        linhas += ["| %d | %s |" % (i, " | ".join(fmt(getattr(l, c)) for c in colunas)) for i, l in enumerate(self, 1)]
        return "\n".join(linhas)

    def salvar(self, caminho) -> Path:
        """Grava em .csv (abre no Excel) ou .json, conforme a extensao."""
        caminho, dados = Path(caminho), [l.para_dict() for l in self]
        if caminho.suffix.lower() == ".json":
            caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
        elif caminho.suffix.lower() == ".csv":
            with caminho.open("w", newline="", encoding="utf-8-sig") as f:
                w = csv.DictWriter(f, fieldnames=list(dados[0]) if dados else ["id"])
                w.writeheader()
                w.writerows({k: _plano(v) for k, v in d.items()} for d in dados)
        else:
            raise ValueError("use uma extensao .csv ou .json: %r" % str(caminho))
        return caminho


# ═══════════════════════════════════════════════════════ 10. BIBLIOTECA (a API)
class Biblioteca:
    """Ponto de entrada. `url`: o site do catalogo (`https://biblioteca.exemplo.br`) ou a
    URL completa que o navegador mostra (`.../wxis.exe?IsisScript=phl82.xis&...`).
    `pausa`: segundos entre requisicoes. `cache`: segundos que respostas identicas ficam
    guardadas (0 desliga). `conectar=False` adia a conexao. `phl`: o cliente de baixo
    nivel, para o que esta API nao cobre."""

    def __init__(self, url: str, *, pausa: float = 0.5, timeout: int = 60, cache: int = 120,
                 conectar: bool = True):
        self.phl = PHL(url, pausa=pausa, timeout=timeout, cache_ttl=cache)
        if conectar:
            self.phl.abrir_sessao()

    def __repr__(self):
        return "Biblioteca(%r)" % self.phl.base

    def livro(self, id: Optional[str] = None, *, isbn: Optional[str] = None,
              tombo: Optional[Any] = None) -> Optional[Livro]:
        """Um livro pelo codigo do titulo, ISBN (com/sem hifen, ISBN-10 ou 13) ou tombo.
        None se nao existir; ValueError se nao informar exatamente um dos tres.
        (consulta o servidor)"""
        if sum(x is not None for x in (id, isbn, tombo)) != 1:
            raise ValueError("informe exatamente um: id=..., isbn=... ou tombo=...")
        if id is not None:
            if not re.fullmatch(r"[A-Za-z0-9]+", str(id).strip()):
                raise ValueError("id invalido: %r (so letras e digitos)" % id)
            reg = next(iter(self.phl.buscar("TIT=%s" % str(id).strip(), modo="exp", rpp=1)), None)
        elif isbn is not None:
            reg = next(iter(self.phl.por_isbn(isbn)), None)
        else:
            reg = self.phl.por_tombo(tombo)
        # o acervo tem 1 registro-esqueleto sem o campo 002; sem este teste ele viraria
        # KeyError('id_titulo') em vez de "nao encontrado".
        return Livro._de_registro(reg, self) if reg and reg.get("id_titulo") else None

    def buscar(self, texto: Optional[str] = None, *, titulo: Optional[str] = None,
               autor: Optional[str] = None, assunto: Optional[str] = None,
               editora: Optional[str] = None, isbn: Optional[str] = None, ano=None,
               curso=None, area=None, classificacao: Optional[str] = None,
               tipo: Optional[str] = None, idioma: Optional[str] = None,
               expressao: Optional[str] = None, limite: Optional[int] = 50) -> Resultado:
        """Busca por criterios combinados (todos precisam valer). Consulta o servidor.

        Texto (todas as palavras; sem acento/caixa; pontuacao ignorada):
          texto (qualquer campo, como o site) | titulo | autor | assunto | editora
        Outros:
          isbn           com/sem hifen, ISBN-10 ou 13
          ano            2021 ou (2019, 2024): ano de PUBLICACAO (filtrado aqui; o servidor
                         nao busca por ele)
          curso          codigo do curso da bibliografia (ex.: 24)
          area           area CNPq: 1..9 ou nome ("engenharias", "saude")
          classificacao  CDD por prefixo: "005" traz 005, 005.1, 005.133...
          tipo           "livro", "periodico", "tese", "e-book"...
          idioma         "portugues", "ingles"... ou o codigo 1..9
          expressao      expressao ISIS crua, para OU/E/NAO: "PYTHON + JAVA", "MATEMATICA ^ ALGEBRA"
        limite: maximo de livros (padrao 50; None = todos). `total` e `truncado` dizem
        se algo ficou de fora. A ordem e a do catalogo (o servidor nao ordena por relevancia);
        ordene com sorted(). Para so os disponiveis: [l for l in ... if l.disponivel].
        """
        if limite is not None and (isinstance(limite, bool) or not isinstance(limite, int) or limite < 1):
            raise ValueError("limite deve ser um inteiro >= 1 ou None: %r" % (limite,))
        faixa = self._faixa_ano(ano) if ano is not None else None
        if isbn is not None and len(_isbn(isbn)) not in (10, 13):
            raise ValueError("ISBN deve ter 10 ou 13 digitos: %r" % isbn)
        kw = {}
        if tipo is not None:
            kw["tipo"] = self._tipo(tipo)
        if idioma is not None:
            kw["idioma"] = self._escolher(idioma, IDIOMAS, "idioma")
        consultas = []      # (expressao, modo, filtros) -- cada uma vira um conjunto de titulos
        for rotulo, valor, campo in (("texto", texto, None), ("titulo", titulo, "titulo"),
                                     ("autor", autor, "autor"), ("assunto", assunto, "assunto"),
                                     ("editora", editora, "editora")):
            if valor is not None:
                if isinstance(valor, bool) or not isinstance(valor, (str, int)):
                    raise ValueError("%s deve ser texto (recebi %s): %r" % (rotulo, type(valor).__name__, valor))
                if not _limpar_consulta(str(valor), "and"):
                    raise ValueError("%s sem conteudo pesquisavel: %r" % (rotulo, valor))
                consultas.append((str(valor), "and", dict(kw, campo=campo) if campo else dict(kw)))
        if expressao is not None:
            if not isinstance(expressao, str) or not expressao.strip():
                raise ValueError("expressao deve ser um texto nao vazio: %r" % (expressao,))
            consultas.append((str(expressao), "exp", dict(kw)))
        if curso is not None:
            if isinstance(curso, bool) or not re.fullmatch(r"[0-9A-Za-z]+", str(curso).strip()):
                raise ValueError("curso invalido: %r (informe o codigo, ex.: 24)" % (curso,))
            consultas.append(("%sCUR=%s" % (BIBLIOTECA, str(curso).strip()), "exp", dict(kw)))
        if area is not None:
            consultas.append(("%sATE=%s" % (BIBLIOTECA, self._escolher(area, AREAS_CNPQ, "area")), "exp", dict(kw)))
        if classificacao is not None:
            if not re.fullmatch(r"[0-9A-Za-z.\-/ ]+", str(classificacao).strip()):
                raise ValueError("classificacao invalida: %r (ex.: '005.13')" % (classificacao,))
            consultas.append(("CLA=%s$" % str(classificacao).strip(), "exp", dict(kw)))
        if not consultas and isbn is None:
            # ponytail: `ano=` sem outro criterio baixa o acervo todo (~10 s) e filtra aqui; o
            #   servidor nao busca por ano de publicacao. Upgrade: cache em disco do acervo.
            if not (faixa or kw):
                raise ValueError("informe ao menos um criterio (titulo=, autor=, ano=, ...); "
                                 "para o acervo inteiro: buscar(expressao='$', limite=None)")
            consultas.append(("$", "exp", dict(kw)))

        if len(consultas) == 1 and isbn is None and not faixa:        # caminho rapido
            exp, modo, f = consultas[0]
            n = self.phl.contar(exp, modo, **f)
            regs = list(self.phl.buscar_tudo(exp, modo, limite=min(limite or n, n), **f)) if n else []
            livros = [Livro._de_registro(r, self) for r in regs if r.get("id_titulo")]
            truncado = limite is not None and n > limite      # nao conta o registro sem id, que e descartado
            return Resultado(livros, total=n if truncado else len(livros), truncado=truncado)

        # varios criterios: intersecao dos titulos de cada um, comecando pelo menor conjunto
        # ponytail: baixa o conjunto completo de CADA criterio (~8 s se casar com o acervo todo);
        #   teto: dois criterios largos. Upgrade: filtrar o menor conjunto por TIT= em lotes.
        conjuntos = []
        if isbn is not None:
            conjuntos.append({r["id_titulo"]: r for r in self.phl.por_isbn(isbn) if r.get("id_titulo")})
        # key=contagem: sem ela, criterios com mesmo texto/modo e mesma contagem (ex.: titulo= e
        # assunto= com a mesma palavra, ambos 0) faziam o sorted comparar os dicts -> TypeError.
        contagens = sorted(((self.phl.contar(e, m, **f), e, m, f) for e, m, f in consultas),
                           key=lambda x: x[0])
        if contagens and contagens[0][0] == 0:
            return Resultado()
        base = conjuntos[0] if conjuntos else None
        for n, e, m, f in contagens:
            if base is not None and not base:
                break
            regs = {r["id_titulo"]: r for r in self.phl.buscar_tudo(e, m, limite=n, pagina=25000, **f)
                    if r.get("id_titulo")}
            base = regs if base is None else {k: v for k, v in base.items() if k in regs}
        livros = [Livro._de_registro(r, self) for r in (base or {}).values()]
        if faixa:
            livros = [l for l in livros if l.ano is not None and faixa[0] <= l.ano <= faixa[1]]
        return Resultado(livros[:limite], total=len(livros), truncado=limite is not None and len(livros) > limite)

    def novidades(self, desde=None, ate=None) -> Resultado:
        """Sem argumentos: o feed 'Aquisicoes do Mes' do proprio OPAC. Com `desde=` (e
        `ate=`, padrao hoje): registros com data de entrada no periodo. Do mais novo ao
        mais antigo; registros sem data de entrada completa ficam de fora. (consulta o servidor)"""
        if desde is None:
            if ate is not None:
                raise ValueError("com 'ate' informe tambem 'desde'")
            regs = self.phl.aquisicoes_do_mes()
        else:
            ini = _data(desde, "desde")
            fim = _data(ate, "ate") if ate is not None else dt.date.today()
            if ini > fim:
                raise ValueError("'desde' (%s) e depois de 'ate' (%s)" % (ini, fim))
            regs = self.phl.catalogados_entre(ini.strftime("%Y%m%d"), fim.strftime("%Y%m%d"))
        livros = [Livro._de_registro(r, self) for r in regs if r.get("id_titulo")]
        if desde is not None:
            # ~40 registros tem data impossivel no catalogo ('20073110', '20111131',
            # '201000609'): passam no filtro do servidor (comparacao de texto) mas nao
            # viram data. Sem isto entravam no resultado com catalogado_em=None.
            livros = [l for l in livros if l.catalogado_em is not None]
        livros.sort(key=lambda l: l.catalogado_em or dt.date.min, reverse=True)
        return Resultado(livros, total=len(livros))

    def sugerir(self, termo: str) -> list:
        """'Voce quis dizer?': entradas do indice parecidas com o termo. Cobre erro no
        fim da palavra, nao no meio de uma frase. (consulta o servidor)"""
        return self.phl.sugerir(termo)

    # ---- validacao dos argumentos de buscar()
    @staticmethod
    def _faixa_ano(ano):
        if isinstance(ano, bool):
            raise ValueError("ano invalido: %r" % ano)
        if isinstance(ano, int):
            a = b = ano
        elif isinstance(ano, (tuple, list)) and len(ano) == 2 and all(isinstance(x, int) for x in ano):
            a, b = min(ano), max(ano)
        else:
            raise ValueError("ano deve ser um int (2021) ou um intervalo (2019, 2024): %r" % (ano,))
        if not 1000 <= a <= b <= 2100:
            raise ValueError("ano fora do intervalo plausivel (1000-2100): %r" % (ano,))
        return a, b

    @staticmethod
    def _escolher(valor, opcoes: dict, nome: str) -> str:
        """Codigo (chave de `opcoes`) a partir do proprio codigo ou do nome (sem acento; trecho unico)."""
        v = _norm(str(valor).strip())
        if v in opcoes:
            return v
        achados = [k for k, n in opcoes.items() if _norm(n) == v] or \
                  [k for k, n in opcoes.items() if v and v in _norm(n)]
        if len(achados) == 1:
            return achados[0]
        raise ValueError("%s %r %s. Opcoes: %s" % (nome, valor, "ambiguo" if achados else "desconhecido",
                                                    ", ".join(sorted(opcoes.values()))))

    @staticmethod
    def _tipo(tipo) -> str:
        # "e-book", "audio livro" e "fone_de_ouvido" valem igual: ignora hifen, espaco e _
        v = re.sub(r"[-_ ]", "", _norm(str(tipo).strip()))
        for k in TIPOS_DOCUMENTO:
            if re.sub(r"[-_ ]", "", k) == v:
                return k
        raise ValueError("tipo %r desconhecido. Opcoes: %s" % (tipo, ", ".join(sorted(TIPOS_DOCUMENTO))))
