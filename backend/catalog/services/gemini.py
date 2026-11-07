"""Cliente mínimo da API Gemini (generateContent), só com a biblioteca padrão.

Uma única chamada REST com resposta em JSON estruturado não justifica o SDK. A
chave vai no cabeçalho `x-goog-api-key`, nunca na URL, e nem a chave nem o texto
enviado aparecem nos logs.
"""

from __future__ import annotations

import json
import logging
import threading
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

from django.conf import settings

logger = logging.getLogger(__name__)

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent"
# Inclui o "raciocínio" dos modelos que pensam antes de responder; com pouco
# espaço a resposta é cortada (MAX_TOKENS).
MAX_OUTPUT_TOKENS = 8192
TEMPERATURE = 0.3


class GeminiError(Exception):
    """Falha ao obter uma resposta utilizável do Gemini."""


class GeminiUnavailableError(GeminiError):
    """Sem chave configurada, erro de rede, tempo esgotado ou erro do servidor."""


class GeminiQuotaError(GeminiError):
    """Cota ou limite de requisições da conta esgotado (HTTP 429)."""


class GeminiBlockedError(GeminiError):
    """Resposta vazia, bloqueada por segurança ou cortada antes do fim."""


class GeminiInvalidResponseError(GeminiError):
    """Resposta que não é o JSON esperado."""


@dataclass(frozen=True)
class GeminiClient:
    """Chamadas ao Gemini com um modelo e um tempo limite fixos."""

    api_key: str
    model: str
    timeout: float

    @property
    def enabled(self) -> bool:
        """Se há chave configurada; sem ela nenhuma chamada é feita."""
        return bool(self.api_key)

    def generate_json(self, system: str, prompt: str, schema: dict[str, object]) -> object:
        """Gera uma resposta em JSON que segue `schema`.

        Args:
            system: Instrução de sistema (papel e regras).
            prompt: Conteúdo do pedido.
            schema: Esquema da resposta no formato OpenAPI aceito pelo Gemini.

        Returns:
            O JSON da resposta, já decodificado.

        Raises:
            GeminiError: Qualquer falha; nenhuma outra exceção escapa.
        """
        if not self.enabled:
            raise GeminiUnavailableError("GEMINI_API_KEY não configurada")
        body = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": schema,
                "temperature": TEMPERATURE,
                "maxOutputTokens": MAX_OUTPUT_TOKENS,
            },
        }
        data = self._post(json.dumps(body).encode("utf-8"))
        return _parse_answer(data)

    def _post(self, payload: bytes) -> object:
        request = urllib.request.Request(
            API_URL % urllib.parse.quote(self.model, safe=""), data=payload, method="POST",
            headers={"Content-Type": "application/json", "x-goog-api-key": self.api_key},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
        except urllib.error.HTTPError as error:
            logger.warning("gemini respondeu HTTP %s (modelo %s)", error.code, self.model)
            if error.code == 429:
                raise GeminiQuotaError("cota do Gemini esgotada") from error
            raise GeminiUnavailableError("Gemini respondeu HTTP %s" % error.code) from error
        except OSError as error:  # URLError, tempo esgotado e falhas de conexão
            logger.warning("gemini inacessível (modelo %s): %s", self.model, type(error).__name__)
            raise GeminiUnavailableError("Gemini inacessível") from error
        try:
            return json.loads(raw)
        except ValueError as error:
            raise GeminiInvalidResponseError("corpo da resposta não é JSON") from error


def _parse_answer(data: object) -> object:
    """Extrai e decodifica o texto JSON do primeiro candidato da resposta."""
    if not isinstance(data, dict):
        raise GeminiInvalidResponseError("resposta sem objeto")
    candidates = data.get("candidates")
    if not isinstance(candidates, list) or not candidates or not isinstance(candidates[0], dict):
        raise GeminiBlockedError("resposta sem candidatos")
    candidate = candidates[0]
    # MAX_TOKENS corta o JSON no meio; SAFETY e outros motivos não trazem texto útil.
    if candidate.get("finishReason") not in (None, "STOP"):
        raise GeminiBlockedError("resposta interrompida: %s" % candidate.get("finishReason"))
    content = candidate.get("content")
    parts = content.get("parts") if isinstance(content, dict) else None
    if not isinstance(parts, list):
        raise GeminiBlockedError("resposta sem conteúdo")
    # Partes marcadas como `thought` são o raciocínio do modelo, não a resposta.
    text = "".join(part["text"] for part in parts if isinstance(part, dict)
                   and isinstance(part.get("text"), str) and not part.get("thought"))
    if not text.strip():
        raise GeminiBlockedError("resposta vazia")
    try:
        return json.loads(text)
    except ValueError as error:
        raise GeminiInvalidResponseError("texto da resposta não é JSON") from error


_client: GeminiClient | None = None
_client_lock = threading.Lock()


def client() -> GeminiClient:
    """Cliente compartilhado entre requisições, criado na primeira vez com as
    configurações do projeto. Os testes substituem esta função."""
    global _client
    with _client_lock:
        if _client is None:
            _client = GeminiClient(settings.GEMINI_API_KEY, settings.GEMINI_MODEL, settings.GEMINI_TIMEOUT)
            if not _client.enabled:
                logger.warning("GEMINI_API_KEY vazia: descoberta e explicações usam só as regras")
        return _client
