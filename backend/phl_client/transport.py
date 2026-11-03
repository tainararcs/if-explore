"""Sessão e HTTP do WWWisis: URLs em ISO-8859-1, sessão `tmp`, novas tentativas,
cache e pausa entre requisições. Não sabe nada de busca."""

from __future__ import annotations

import http.client
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping

from .errors import LibraryConnectionError, LibraryError
from .fields import KNOWN_SCRIPT_DIRS, USER_AGENT
from .query import parse_catalog_url

MAX_CACHE_ENTRIES = 200
MAX_CACHED_RESPONSE_BYTES = 1_000_000


class Transport:
    """Acesso HTTP ao CGI do catálogo, com sessão, cache e pausa de cortesia."""

    def __init__(self, url: str, pause: float = 0.5, timeout: int = 60, cache_ttl: int = 0):
        """
        Args:
            url: Site do catálogo ou URL completa do navegador (ver `parse_catalog_url`).
            pause: Segundos de espera depois de cada requisição, por cortesia.
            timeout: Segundos até desistir de uma requisição.
            cache_ttl: Segundos que uma resposta idêntica fica em cache (0 desliga).
        """
        info = parse_catalog_url(url)
        self.base, self.cgi = info["base"], info["cgi"]
        self.script_dir = info["script_dir"]   # None: descobrir ao abrir a sessão
        self.cipar, self.lang = info["cipar"], info["lang"]
        self.pause, self.timeout, self.cache_ttl = pause, timeout, cache_ttl
        self.session: str | None = None
        self._cache: dict[str, tuple[float, str]] = {}

    @property
    def script(self) -> str:
        """Script de busca (`<dir>/003.xis`); descobre a versão se preciso."""
        if self.script_dir is None:
            self.open_session()
        return "%s/003.xis" % self.script_dir

    def request(self, params: Mapping[str, str | None]) -> str:
        """Faz uma consulta ao CGI, renovando a sessão uma vez se ela expirou.

        Parâmetros com valor None são omitidos.

        Raises:
            LibraryConnectionError: Servidor inacessível ou com HTTP de erro.
            LibraryError: Resposta de erro do WWWisis.
        """
        if self.session is None:
            self.open_session()
        for attempt in (1, 2):
            query = {key: value for key, value in params.items() if value is not None}
            query.setdefault("tmp", self.session or "")
            # O WWWisis só entende ISO-8859-1: em UTF-8 ele devolve zero resultados,
            # em silêncio, para qualquer termo acentuado.
            url = self.cgi + "?" + urllib.parse.urlencode(query, encoding="iso-8859-1", errors="replace")
            try:
                return self.fetch(url)
            except LibraryConnectionError:
                raise
            except LibraryError as error:
                # Sessão (tmp) expirada: o servidor responde 'dbxopen'. Abre outra e repete.
                if attempt == 1 and "dbxopen" in str(error) and "tmp" not in params:
                    self.session = None
                    self.open_session()
                    continue
                raise
        raise AssertionError("inalcançável")

    def fetch(self, url: str, attempts: int = 2, use_cache: bool = True) -> str:
        """Baixa uma URL e devolve o texto, com cache, novas tentativas e pausa.

        Raises:
            LibraryConnectionError: Servidor inacessível ou com HTTP de erro.
            LibraryError: Resposta de erro do WWWisis ('WXIS|...').
        """
        cached = use_cache and self.cache_ttl > 0
        if cached:
            hit = self._cache.get(url)
            if hit and time.time() - hit[0] < self.cache_ttl:
                return hit[1]
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        last_error: Exception | None = None
        for attempt in range(attempts):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    body: bytes = response.read()
                break
            except urllib.error.HTTPError as error:
                if error.code < 500:   # 404/403...: repetir não adianta
                    raise LibraryConnectionError("o servidor respondeu HTTP %d para %s -- confira "
                                                 "a URL do catálogo" % (error.code, self.cgi)) from None
                last_error = error
            except (urllib.error.URLError, TimeoutError, ConnectionError, ssl.SSLError,
                    http.client.HTTPException) as error:
                last_error = error
            if attempt + 1 < attempts:
                time.sleep(1.0)
        else:
            # Expressões booleanas muito compostas (vários "^" encadeados contra a base
            # inteira) podem fazer o WWWisis não responder no prazo: é do motor ISIS.
            raise LibraryConnectionError(
                "sem resposta de %s após %d tentativa(s) (%s). Se a expressão de busca for "
                "muito complexa (vários '^' encadeados), tente simplificá-la."
                % (self.base, attempts, last_error))
        time.sleep(self.pause)
        text = body.decode("iso-8859-1")
        # O WWWisis às vezes antepõe uma quebra de linha ao erro ("\nWXIS|fatal error|..."):
        # sem o lstrip, sessão expirada virava "0 resultados" mudo.
        if text.lstrip().startswith("WXIS|"):
            raise LibraryError(text.strip())
        if cached and len(body) < MAX_CACHED_RESPONSE_BYTES:
            if len(self._cache) >= MAX_CACHE_ENTRIES:
                # despejo FIFO simples; trocar por LRU se a taxa de acerto importar
                self._cache.pop(next(iter(self._cache)))
            self._cache[url] = (time.time(), text)
        return text

    def open_session(self) -> str:
        """Obtém um id de sessão (/tmp/fileXXXXXX) na página inicial do catálogo.

        Se a versão dos scripts não foi informada, testa as conhecidas.

        Raises:
            LibraryError: Quando nenhuma versão abre sessão (a URL não é um PHL).
        """
        candidates = [self.script_dir] if self.script_dir else list(KNOWN_SCRIPT_DIRS)
        for script_dir in candidates:
            cipar = self.cipar if self.script_dir else script_dir + ".cip"
            url = "%s?IsisScript=%s.xis&cipar=%s&lang=%s" % (self.cgi, script_dir, cipar, self.lang)
            try:
                text = self.fetch(url, use_cache=False)
            except LibraryConnectionError:
                raise
            except LibraryError:
                continue   # script inexistente: tenta o próximo
            match = re.search(r"tmp=(/tmp/file[A-Za-z0-9]+)", text)
            if match:
                self.script_dir, self.cipar, self.session = script_dir, cipar, match.group(1)
                return self.session
        raise LibraryError("%s não parece ser um catálogo PHL (não consegui abrir uma sessão%s). "
                           "Confira a URL." % (self.base, "" if self.script_dir is None else
                                               " com IsisScript=%s.xis" % candidates[0]))
