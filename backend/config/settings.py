"""Configuração do projeto Django da API do IF Explore.

Valores sensíveis ou dependentes do ambiente vêm de variáveis de ambiente, que
podem ser declaradas em `backend/.env` (modelo em `.env.example`); os padrões
servem para desenvolvimento local.
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Variáveis já definidas no ambiente (servidor, cron) têm prioridade sobre o arquivo.
load_dotenv(BASE_DIR / ".env", override=False)


def env_bool(name: str, default: bool) -> bool:
    """Lê uma variável de ambiente booleana ('1', 'true', 'yes', 'on')."""
    value = os.environ.get(name)
    return default if value is None else value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    """Lê uma lista separada por vírgulas."""
    return [item.strip() for item in os.environ.get(name, default).split(",") if item.strip()]


DEBUG = env_bool("DJANGO_DEBUG", True)

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured("defina DJANGO_SECRET_KEY quando DJANGO_DEBUG estiver desligado")
    # Só para desenvolvimento local: nunca usada com DEBUG desligado.
    SECRET_KEY = "dev-only-insecure-key"

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "catalog",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# SQLite em modo WAL: a sincronização grava numa transação enquanto a API continua
# lendo a versão anterior. IMMEDIATE evita "database is locked" em escritas concorrentes.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("SQLITE_PATH", BASE_DIR / "db.sqlite3"),
        "OPTIONS": {
            "init_command": "PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;",
            "transaction_mode": "IMMEDIATE",
            "timeout": 20,
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"catalog": {"handlers": ["console"], "level": os.environ.get("CATALOG_LOG_LEVEL", "INFO")}},
}

# ---- catálogo da biblioteca (PHL)
PHL_CATALOG_URL = os.environ.get("PHL_CATALOG_URL", "https://biblioteca.barbacena.ifsudestemg.edu.br")
# Pausa de cortesia entre requisições ao CGI do campus, em segundos.
PHL_PAUSE = float(os.environ.get("PHL_PAUSE", "0.5"))
# Um snapshot com menos que esta fração dos títulos ativos (ou uma leitura dos
# exemplares com menos que esta fração dos registros) é tratado como resposta
# truncada e não é aplicado.
CATALOG_SYNC_MIN_RATIO = float(os.environ.get("CATALOG_SYNC_MIN_RATIO", "0.9"))
# Na página de um livro, exemplares verificados há mais que isto são consultados
# de novo no PHL, com este tempo limite (segundos) por tentativa.
COPIES_LIVE_MAX_AGE_MINUTES = int(os.environ.get("COPIES_LIVE_MAX_AGE_MINUTES", "15"))
PHL_LIVE_TIMEOUT = int(os.environ.get("PHL_LIVE_TIMEOUT", "5"))

# ---- IA (Gemini): descoberta e explicações dos livros
# Sem chave, a IA fica desligada e as rotas respondem com a seleção por regras.
# A chave só existe no servidor; nunca a exponha ao frontend.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()
# Tempo limite de cada chamada, em segundos: há uma pessoa esperando.
GEMINI_TIMEOUT = int(os.environ.get("GEMINI_TIMEOUT", "10"))
# Limites por IP ("número/período": s, m, h ou d) dos pedidos de descoberta e das
# explicações dos livros. O IP vem de X-Forwarded-For quando presente; atrás de um
# proxy reverso, defina aqui NINJA_NUM_PROXIES para que o cabeçalho não seja forjável.
DISCOVERY_RATE = os.environ.get("DISCOVERY_RATE", "10/m").strip()
EXPLANATION_RATE = os.environ.get("EXPLANATION_RATE", "60/m").strip()
