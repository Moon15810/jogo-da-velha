import os

from dotenv import load_dotenv
from sqlalchemy.pool import StaticPool

load_dotenv()  # carrega variáveis do arquivo .env


class Config:
    """Configuração de desenvolvimento/produção (lê do ambiente)."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-inseguro-trocar")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://games_user:12345678@localhost/games",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    """Configuração de testes: banco SQLite em memória, sem CSRF."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }
    WTF_CSRF_ENABLED = False
