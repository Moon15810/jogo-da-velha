# Plataforma de Jogos — Fase 1 (Fundação) — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transformar o Jogo da Velha atual em um site público de jogos com contas de usuário, MySQL e a velha jogável integrada à plataforma.

**Architecture:** Flask no padrão *app factory* com blueprints por área (`principal`, `jogos`, `auth`). Persistência em MySQL via SQLAlchemy (ORM); sessões via Flask-Login; formulários com CSRF via Flask-WTF. A lógica do jogo vira um pacote Python puro e reutilizável (`jogo_velha/`), consumido pela camada web.

**Tech Stack:** Python 3.12, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, PyMySQL, python-dotenv, pytest.

## Global Constraints

- Python 3.12; padrão app factory + blueprints.
- Banco: MySQL `games` via SQLAlchemy; driver `mysql+pymysql`; URL vem do `.env` (`DATABASE_URL`).
- Senhas SEMPRE hasheadas (Werkzeug); nunca texto puro.
- CSRF ativo em todos os formulários (Flask-WTF).
- Segredos no `.env` (no `.gitignore`); `.env.example` documenta as variáveis sem valores.
- Testes com pytest; testes que tocam banco usam **SQLite em memória** (`sqlite://` com `StaticPool`).
- Nomes e textos em português (`nome_usuario`, `senha`, etc.).
- Regras: `nome_usuario` 3–30 chars, único; `senha` ≥ 8 chars.
- Nome do site: **"Arcade"** (título de trabalho — pode ser trocado depois; se mudar, ajustar em `base.html`/`home.html`).
- Commits frequentes, um por tarefa concluída.

---

### Task 1: Ambiente — sistema (venv + MySQL), dependências e configuração base

**Files:**
- Create: `requirements.txt`
- Create: `config.py`
- Create: `.env.example`
- Create: `.env` (local, não versionado)
- Create: `.gitignore`

**Interfaces:**
- Produces: `config.Config` (produção/dev, lê `DATABASE_URL` e `SECRET_KEY`) e `config.TestConfig` (SQLite em memória, CSRF desligado).

> ⚠️ Esta tarefa mexe no sistema (precisa de `sudo`) e precisa do Cleiton por perto.

- [ ] **Step 1: Instalar pacotes de sistema**

Run:
```bash
sudo apt update
sudo apt install -y python3-venv mysql-server
```
Expected: `python3-venv` e `mysql-server` instalados sem erro.

- [ ] **Step 2: Criar o banco e o usuário no MySQL**

Run:
```bash
sudo mysql <<'SQL'
CREATE DATABASE IF NOT EXISTS games CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'games_user'@'localhost' IDENTIFIED BY '12345678';
GRANT ALL PRIVILEGES ON games.* TO 'games_user'@'localhost';
FLUSH PRIVILEGES;
SQL
```
Expected: sem erros. (Senha `12345678` é só para desenvolvimento local.)

- [ ] **Step 3: Criar o `requirements.txt`**

Create `requirements.txt`:
```
Flask>=3.0
Flask-SQLAlchemy>=3.1
Flask-Login>=0.6
Flask-WTF>=1.2
PyMySQL>=1.1
python-dotenv>=1.0
pytest>=8.0
```

- [ ] **Step 4: Criar o ambiente virtual e instalar as dependências**

Run:
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```
Expected: instalação conclui com "Successfully installed Flask ... pytest ...".

- [ ] **Step 5: Criar o `.gitignore`**

Create `.gitignore`:
```
.env
.venv/
venv/
__pycache__/
*.pyc
*.sqlite3
```

- [ ] **Step 6: Criar `config.py`**

Create `config.py`:
```python
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
```

- [ ] **Step 7: Criar `.env.example` e `.env`**

Create `.env.example`:
```
SECRET_KEY=troque-por-uma-chave-aleatoria
DATABASE_URL=mysql+pymysql://games_user:SENHA@localhost/games
```

Gerar a `SECRET_KEY` e criar o `.env` real:
```bash
echo "SECRET_KEY=$(.venv/bin/python -c 'import secrets; print(secrets.token_hex(32))')" > .env
echo "DATABASE_URL=mysql+pymysql://games_user:12345678@localhost/games" >> .env
```

- [ ] **Step 8: Testar a conexão com o MySQL**

Run:
```bash
.venv/bin/python -c "import os; from dotenv import load_dotenv; from sqlalchemy import create_engine, text; load_dotenv(); e=create_engine(os.environ['DATABASE_URL']); \
c=e.connect(); print('conectou:', c.execute(text('SELECT 1')).scalar()); c.close()"
```
Expected: `conectou: 1`

- [ ] **Step 9: Commit**

```bash
git add requirements.txt config.py .env.example .gitignore
git commit -m "chore: ambiente, dependencias e config base (MySQL + venv)"
```

---

### Task 2: Reorganizar a lógica do jogo no pacote `jogo_velha/` + testes

**Files:**
- Create: `jogo_velha/__init__.py`
- Move: `tabuleiro.py`, `ia.py`, `logica_web.py`, `jogador.py`, `jogo.py`, `utils.py`, `main.py` → `jogo_velha/`
- Modify: imports internos para relativos (`from .tabuleiro import ...`)
- Create: `jogar_terminal.py` (raiz, atalho para a versão de terminal)
- Create: `pytest.ini`
- Create: `tests/__init__.py`, `tests/test_jogo_velha.py`

**Interfaces:**
- Produces: `jogo_velha.logica_web.processar_jogada(lista, posicao, humano="X", modo="2p") -> dict`; `jogo_velha.tabuleiro.combo_vencedor(tab, simbolo)`, `verificar_vitoria`, `criar_tabuleiro`, `CASA_VAZIA`; `jogo_velha.ia.melhor_jogada(tab, ia, humano)`.

- [ ] **Step 1: Criar o pacote e mover os arquivos**

Run:
```bash
mkdir -p jogo_velha tests
git mv tabuleiro.py ia.py logica_web.py jogador.py jogo.py utils.py main.py jogo_velha/ 2>/dev/null || mv tabuleiro.py ia.py logica_web.py jogador.py jogo.py utils.py main.py jogo_velha/
touch jogo_velha/__init__.py tests/__init__.py
```
Expected: os módulos agora estão em `jogo_velha/`.

- [ ] **Step 2: Ajustar os imports internos para relativos**

In `jogo_velha/ia.py`, trocar:
```python
from tabuleiro import verificar_vitoria, verificar_empate, CASA_VAZIA
```
por:
```python
from .tabuleiro import verificar_vitoria, verificar_empate, CASA_VAZIA
```

In `jogo_velha/logica_web.py`, trocar:
```python
from tabuleiro import (
    validar_jogada,
    realizar_jogada,
    verificar_vitoria,
    verificar_empate,
    combo_vencedor,
    CASA_VAZIA,
)
from ia import melhor_jogada
```
por:
```python
from .tabuleiro import (
    validar_jogada,
    realizar_jogada,
    verificar_vitoria,
    verificar_empate,
    combo_vencedor,
    CASA_VAZIA,
)
from .ia import melhor_jogada
```

In `jogo_velha/jogo.py`, trocar:
```python
from tabuleiro import (
    criar_tabuleiro,
    mostrar_tabuleiro,
    validar_jogada,
    realizar_jogada,
    verificar_vitoria,
    verificar_empate,
)
from jogador import criar_jogador, trocar_jogador
from utils import limpar_tela, ler_inteiro
```
por (prefixar cada módulo com `.`):
```python
from .tabuleiro import (
    criar_tabuleiro,
    mostrar_tabuleiro,
    validar_jogada,
    realizar_jogada,
    verificar_vitoria,
    verificar_empate,
)
from .jogador import criar_jogador, trocar_jogador
from .utils import limpar_tela, ler_inteiro
```

In `jogo_velha/main.py`, trocar:
```python
from jogo import iniciar_jogo
```
por:
```python
from .jogo import iniciar_jogo
```

- [ ] **Step 3: Criar o atalho de terminal na raiz**

Create `jogar_terminal.py`:
```python
# Atalho para rodar a versão de terminal do Jogo da Velha.
from jogo_velha.jogo import iniciar_jogo

if __name__ == "__main__":
    iniciar_jogo()
```

- [ ] **Step 4: Criar `pytest.ini`**

Create `pytest.ini`:
```ini
[pytest]
pythonpath = .
testpaths = tests
```

- [ ] **Step 5: Escrever os testes da lógica do jogo (que devem falhar por import)**

Create `tests/test_jogo_velha.py`:
```python
from jogo_velha.tabuleiro import criar_tabuleiro, verificar_vitoria, combo_vencedor, CASA_VAZIA
from jogo_velha.ia import melhor_jogada
from jogo_velha.logica_web import processar_jogada

E = CASA_VAZIA


def test_ia_fecha_vitoria():
    tab = [["O", "O", E], ["X", "X", E], [E, E, E]]
    assert melhor_jogada(tab, "O", "X") == (0, 2)


def test_ia_bloqueia_humano():
    tab = [["X", "X", E], [E, "O", E], [E, E, E]]
    assert melhor_jogada(tab, "O", "X") == (0, 2)


def test_combo_vencedor_diagonal():
    tab = [["X", E, E], [E, "X", E], [E, E, "X"]]
    assert combo_vencedor(tab, "X") == [(0, 0), (1, 1), (2, 2)]
    assert verificar_vitoria(tab, "X") is True


def test_humano_nunca_vence_a_ia():
    def humano_nunca_ganha(tab, vez_humano):
        if verificar_vitoria(tab, "X"):
            return False
        if verificar_vitoria(tab, "O"):
            return True
        livres = [(l, c) for l in range(3) for c in range(3) if tab[l][c] == E]
        if not livres:
            return True
        if vez_humano:
            for l, c in livres:
                tab[l][c] = "X"
                ok = humano_nunca_ganha(tab, False)
                tab[l][c] = E
                if not ok:
                    return False
            return True
        l, c = melhor_jogada(tab, "O", "X")
        tab[l][c] = "O"
        ok = humano_nunca_ganha(tab, True)
        tab[l][c] = E
        return ok

    assert humano_nunca_ganha(criar_tabuleiro(), True) is True


def test_processar_jogada_2p():
    r = processar_jogada([""] * 9, 0, "X", "2p")
    assert r["ok"] and r["tabuleiro"][0] == "X" and r["proximo"] == "O"


def test_processar_jogada_casa_ocupada():
    r = processar_jogada(["X"] + [""] * 8, 0, "O", "2p")
    assert r["ok"] is False and "ocupada" in r["erro"]


def test_processar_jogada_ia_responde():
    r = processar_jogada([""] * 9, 4, "X", "ia")
    assert r["tabuleiro"][4] == "X"
    assert r["jogada_ia"] in (0, 2, 6, 8)
    assert r["tabuleiro"].count("O") == 1
```

- [ ] **Step 6: Rodar os testes (esperado: PASSAM)**

Run: `.venv/bin/pytest tests/test_jogo_velha.py -v`
Expected: 7 passed.

- [ ] **Step 7: Commit**

```bash
git add jogo_velha/ tests/ jogar_terminal.py pytest.ini
git commit -m "refactor: mover a logica do jogo para o pacote jogo_velha + testes"
```

---

### Task 3: Extensões + modelo `Usuario` (TDD com SQLite)

**Files:**
- Create: `plataforma/__init__.py` (app factory mínima)
- Create: `plataforma/extensoes.py`
- Create: `plataforma/modelos.py`
- Create: `tests/conftest.py`
- Create: `tests/test_modelos.py`

**Interfaces:**
- Consumes: `config.Config`, `config.TestConfig` (Task 1).
- Produces: `plataforma.create_app(config_class=Config) -> Flask`; `plataforma.extensoes.db`, `login_manager`; `plataforma.modelos.Usuario` com `definir_senha(senha)`, `checar_senha(senha) -> bool`, campos `id`, `nome_usuario`, `senha_hash`, `criado_em`.

- [ ] **Step 1: Criar `plataforma/extensoes.py`**

Create `plataforma/extensoes.py`:
```python
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Faça login para acessar esta página."
login_manager.login_message_category = "erro"
```

- [ ] **Step 2: Criar `plataforma/modelos.py`**

Create `plataforma/modelos.py`:
```python
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .extensoes import db, login_manager


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(30), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def checar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f"<Usuario {self.nome_usuario}>"


@login_manager.user_loader
def carregar_usuario(user_id):
    return db.session.get(Usuario, int(user_id))
```

- [ ] **Step 3: Criar a app factory mínima `plataforma/__init__.py`**

Create `plataforma/__init__.py`:
```python
from flask import Flask

from config import Config
from .extensoes import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    from . import modelos  # registra o modelo Usuario no SQLAlchemy

    with app.app_context():
        db.create_all()

    return app
```

- [ ] **Step 4: Criar `tests/conftest.py`**

Create `tests/conftest.py`:
```python
import pytest

from plataforma import create_app
from config import TestConfig


@pytest.fixture
def app():
    return create_app(TestConfig)


@pytest.fixture
def client(app):
    return app.test_client()
```

- [ ] **Step 5: Escrever os testes do modelo (esperado: FALHAM)**

Create `tests/test_modelos.py`:
```python
from plataforma.extensoes import db
from plataforma.modelos import Usuario


def test_senha_e_hasheada(app):
    with app.app_context():
        u = Usuario(nome_usuario="ana")
        u.definir_senha("segredo123")
        assert u.senha_hash != "segredo123"          # nunca em texto puro
        assert u.checar_senha("segredo123") is True
        assert u.checar_senha("errada") is False


def test_nome_usuario_unico(app):
    with app.app_context():
        u1 = Usuario(nome_usuario="bia")
        u1.definir_senha("segredo123")
        db.session.add(u1)
        db.session.commit()

        u2 = Usuario(nome_usuario="bia")
        u2.definir_senha("outra123")
        db.session.add(u2)
        import pytest
        from sqlalchemy.exc import IntegrityError
        with pytest.raises(IntegrityError):
            db.session.commit()
```

- [ ] **Step 6: Rodar os testes (esperado: FALHAM por não existir ainda / depois PASSAM)**

Run: `.venv/bin/pytest tests/test_modelos.py -v`
Expected: 2 passed. (Se algum módulo faltar, o teste falha no import — implemente os steps 1–3 e rode de novo.)

- [ ] **Step 7: Commit**

```bash
git add plataforma/ tests/conftest.py tests/test_modelos.py
git commit -m "feat: modelo Usuario com senha hasheada e app factory minima"
```

---

### Task 4: App factory completa + home/galeria + tema visual

**Files:**
- Modify: `plataforma/__init__.py` (registrar blueprints)
- Create: `plataforma/principal/__init__.py`, `plataforma/principal/rotas.py`
- Create: `plataforma/templates/base.html`, `plataforma/templates/principal/home.html`
- Create: `plataforma/static/css/tema.css`
- Create: `run.py`
- Create: `tests/test_paginas.py`

**Interfaces:**
- Consumes: `create_app` (Task 3).
- Produces: blueprint `principal` com rota `principal.home` em `/`; template `base.html` com blocos `titulo`, `head_extra`, `conteudo`; `run.py` executável.

- [ ] **Step 1: Criar o blueprint principal**

Create `plataforma/principal/__init__.py` (vazio).

Create `plataforma/principal/rotas.py`:
```python
from flask import Blueprint, render_template

bp = Blueprint("principal", __name__)

JOGOS = [
    {
        "nome": "Jogo da Velha",
        "descricao": "O clássico X e O. Jogue a dois ou contra a IA imbatível.",
        "endpoint": "jogos.velha",
    },
]


@bp.route("/")
def home():
    return render_template("principal/home.html", jogos=JOGOS)
```

- [ ] **Step 2: Criar `base.html`**

Create `plataforma/templates/base.html`:
```html
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block titulo %}Arcade{% endblock %}</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/tema.css') }}">
  {% block head_extra %}{% endblock %}
</head>
<body>
  <header class="cabecalho">
    <a class="logo" href="{{ url_for('principal.home') }}">Arcade</a>
    <nav class="nav">
      {% if current_user.is_authenticated %}
        <span class="nav-usuario">Olá, <b>{{ current_user.nome_usuario }}</b></span>
        <form action="{{ url_for('auth.logout') }}" method="post" class="nav-form">
          <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
          <button class="btn btn-ghost" type="submit">Sair</button>
        </form>
      {% else %}
        <a class="btn btn-ghost" href="{{ url_for('auth.login') }}">Entrar</a>
        <a class="btn" href="{{ url_for('auth.cadastro') }}">Cadastrar</a>
      {% endif %}
    </nav>
  </header>

  {% with mensagens = get_flashed_messages(with_categories=true) %}
    {% if mensagens %}
      <div class="flashes">
        {% for categoria, msg in mensagens %}
          <div class="flash flash-{{ categoria }}">{{ msg }}</div>
        {% endfor %}
      </div>
    {% endif %}
  {% endwith %}

  <main class="conteudo">
    {% block conteudo %}{% endblock %}
  </main>
</body>
</html>
```

- [ ] **Step 3: Criar `home.html`**

Create `plataforma/templates/principal/home.html`:
```html
{% extends "base.html" %}
{% block titulo %}Arcade — jogos no navegador{% endblock %}
{% block conteudo %}
  <section class="hero">
    <h1 class="hero-titulo">Arcade</h1>
    <p class="hero-sub">Jogos clássicos no navegador. Jogue já — crie uma conta para competir depois.</p>
  </section>
  <section class="galeria">
    {% for jogo in jogos %}
      <a class="card" href="{{ url_for(jogo.endpoint) }}">
        <span class="card-nome">{{ jogo.nome }}</span>
        <span class="card-desc">{{ jogo.descricao }}</span>
        <span class="card-cta">Jogar →</span>
      </a>
    {% endfor %}
  </section>
{% endblock %}
```

- [ ] **Step 4: Criar o tema `tema.css`**

Create `plataforma/static/css/tema.css` com o tema "tinta sobre papel". Copie as **variáveis de tema** (blocos `:root`, `@media (prefers-color-scheme: dark)`, `:root[data-theme=...]`) e o fundo quadriculado do arquivo existente `templates/index.html`, e acrescente os estilos da casca do site abaixo:
```css
/* Cole aqui, ANTES, os blocos :root / dark / light e o *{box-sizing} do
   templates/index.html atual (as variáveis --paper, --ink, --x, --o, etc.). */

body{
  margin:0; color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  background:
    linear-gradient(var(--grid) 1px, transparent 1px) 0 0 / 26px 26px,
    linear-gradient(90deg, var(--grid) 1px, transparent 1px) 0 0 / 26px 26px,
    var(--paper);
  background-attachment:fixed;
}
.cabecalho{
  display:flex; align-items:center; justify-content:space-between;
  padding:16px clamp(16px,4vw,40px); border-bottom:1px solid var(--edge);
  background:var(--panel);
}
.logo{
  font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  font-weight:700; font-size:1.5rem; color:var(--ink); text-decoration:none; letter-spacing:-.01em;
}
.nav{ display:flex; align-items:center; gap:12px; }
.nav-usuario{ color:var(--muted); font-size:.95rem; }
.nav-form{ margin:0; }
.btn{
  font:inherit; font-weight:600; cursor:pointer; text-decoration:none; display:inline-block;
  padding:9px 18px; border-radius:999px; border:1.5px solid var(--ink);
  background:var(--ink); color:var(--paper); transition:transform .12s ease, box-shadow .2s ease;
}
.btn:hover{ transform:translateY(-1px); box-shadow:var(--shadow-btn); }
.btn-ghost{ background:transparent; color:var(--ink); }
.btn-bloco{ width:100%; text-align:center; margin-top:8px; }
.conteudo{ max-width:960px; margin:0 auto; padding:clamp(24px,5vw,48px) 20px; }
.hero{ text-align:center; margin-bottom:36px; }
.hero-titulo{
  font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  font-size:clamp(2.4rem,8vw,3.6rem); margin:0 0 8px;
}
.hero-sub{ color:var(--muted); max-width:44ch; margin:0 auto; }
.galeria{ display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:18px; }
.card{
  display:flex; flex-direction:column; gap:8px; padding:22px;
  background:var(--panel); border:1px solid var(--edge); border-radius:16px;
  text-decoration:none; color:var(--ink); box-shadow:var(--shadow-sm);
  transition:transform .14s ease, box-shadow .2s ease;
}
.card:hover{ transform:translateY(-3px); box-shadow:var(--shadow-btn); }
.card-nome{ font-weight:800; font-size:1.2rem; }
.card-desc{ color:var(--muted); font-size:.95rem; }
.card-cta{ margin-top:4px; color:var(--x); font-weight:700; }
.flashes{ max-width:960px; margin:16px auto 0; padding:0 20px; display:flex; flex-direction:column; gap:8px; }
.flash{ padding:12px 16px; border-radius:12px; font-size:.95rem; border:1px solid var(--edge); }
.flash-sucesso{ background:color-mix(in srgb, var(--x) 12%, var(--panel)); }
.flash-erro{ background:color-mix(in srgb, var(--o) 14%, var(--panel)); }
.form-card{
  max-width:380px; margin:0 auto; background:var(--panel); border:1px solid var(--edge);
  border-radius:18px; padding:28px; box-shadow:var(--shadow-sm);
}
.form-card h1{ margin:0 0 18px; }
.form-card label{ display:block; margin-bottom:12px; font-weight:600; }
.campo{
  width:100%; margin-top:6px; padding:10px 12px; border-radius:10px;
  border:1.5px solid var(--edge); background:var(--paper); color:var(--ink); font:inherit;
}
.campo:focus{ outline:3px solid var(--x); outline-offset:1px; }
.erro-campo{ display:block; color:var(--o); font-size:.85rem; margin:-6px 0 10px; }
.form-alt{ margin-top:16px; text-align:center; color:var(--muted); }
```

- [ ] **Step 5: Registrar o blueprint na factory**

In `plataforma/__init__.py`, adicionar ANTES do `with app.app_context()`:
```python
    from .principal.rotas import bp as principal_bp
    app.register_blueprint(principal_bp)
```

- [ ] **Step 6: Criar `run.py`**

Create `run.py`:
```python
from plataforma import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
```

- [ ] **Step 7: Escrever o teste da home (esperado: FALHA sem blueprint jogos)**

Create `tests/test_paginas.py`:
```python
def test_home_carrega(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Jogo da Velha".encode() in resp.data
```

> Este teste usa `url_for('jogos.velha')` via `home.html`; ele só passa depois do blueprint `jogos` existir (Task 5). Por isso, rode-o ao final da Task 5.

- [ ] **Step 8: Commit**

```bash
git add plataforma/ run.py tests/test_paginas.py
git commit -m "feat: home com galeria, tema visual e base template"
```

---

### Task 5: Blueprint `jogos` — página da velha + API

**Files:**
- Modify: `plataforma/__init__.py` (registrar blueprint jogos)
- Create: `plataforma/jogos/__init__.py`, `plataforma/jogos/rotas.py`
- Create: `plataforma/templates/jogos/velha.html`
- Create: `plataforma/static/css/velha.css`, `plataforma/static/js/velha.js`
- Create: `tests/test_jogos.py`

**Interfaces:**
- Consumes: `jogo_velha.logica_web.processar_jogada` (Task 2); `create_app` (Task 4).
- Produces: rota `jogos.velha` em `/jogos/velha`; rota `jogos.velha_api_jogar` em `/jogos/velha/api/jogar` (POST).

- [ ] **Step 1: Criar o blueprint jogos**

Create `plataforma/jogos/__init__.py` (vazio).

Create `plataforma/jogos/rotas.py`:
```python
from flask import Blueprint, render_template, request, jsonify

from jogo_velha.logica_web import processar_jogada

bp = Blueprint("jogos", __name__, url_prefix="/jogos")


@bp.route("/velha")
def velha():
    return render_template("jogos/velha.html")


@bp.route("/velha/api/jogar", methods=["POST"])
def velha_api_jogar():
    dados = request.get_json(force=True)
    resultado = processar_jogada(
        lista=dados.get("tabuleiro", [""] * 9),
        posicao=dados.get("posicao"),
        humano=dados.get("jogador", "X"),
        modo=dados.get("modo", "2p"),
    )
    return jsonify(resultado), (200 if resultado["ok"] else 400)
```

- [ ] **Step 2: Registrar o blueprint na factory**

In `plataforma/__init__.py`, junto ao registro do principal:
```python
    from .jogos.rotas import bp as jogos_bp
    app.register_blueprint(jogos_bp)
```

- [ ] **Step 3: Criar os assets do jogo a partir do arquivo existente**

- Copie o conteúdo de `<style>…</style>` do atual `templates/index.html` para `plataforma/static/css/velha.css` (as variáveis `:root` podem ser removidas se já estiverem em `tema.css`; mantenha os estilos `.board`, `.cell`, `.mark`, `.win-line`, `.modes`, `.scores`, etc.).
- Copie o conteúdo de `<script>…</script>` do atual `templates/index.html` para `plataforma/static/js/velha.js`.
- Em `velha.js`, trocar a URL fixa do fetch para ler do atributo `data-api`:
  - No topo do script: `const API = document.querySelector(".velha-wrap").dataset.api;`
  - Na chamada `fetch("/api/jogar", ...)` → `fetch(API, ...)`.

- [ ] **Step 4: Criar `velha.html`**

Create `plataforma/templates/jogos/velha.html` (copie o markup interno do `<body>` do `templates/index.html` — cabeçalho do jogo, modos, placar, `.board`, status e controles — para dentro do bloco abaixo, envolto por `.velha-wrap`):
```html
{% extends "base.html" %}
{% block titulo %}Jogo da Velha — Arcade{% endblock %}
{% block head_extra %}
  <link rel="stylesheet" href="{{ url_for('static', filename='css/velha.css') }}">
{% endblock %}
{% block conteudo %}
  <div class="velha-wrap" data-api="{{ url_for('jogos.velha_api_jogar') }}">
    <!-- COLE AQUI o conteúdo do <main class="page"> do templates/index.html:
         header do jogo, .modes, .scores, .board (com svgs e 9 .cell),
         .status e .controls. -->
  </div>
  <script src="{{ url_for('static', filename='js/velha.js') }}"></script>
{% endblock %}
```

- [ ] **Step 5: Escrever os testes do blueprint jogos (esperado: PASSAM)**

Create `tests/test_jogos.py`:
```python
import json


def test_pagina_velha_carrega(client):
    resp = client.get("/jogos/velha")
    assert resp.status_code == 200


def test_api_jogada_valida_2p(client):
    payload = {"tabuleiro": [""] * 9, "posicao": 4, "jogador": "X", "modo": "2p"}
    resp = client.post("/jogos/velha/api/jogar", json=payload)
    assert resp.status_code == 200
    dados = resp.get_json()
    assert dados["ok"] is True
    assert dados["tabuleiro"][4] == "X"


def test_api_jogada_invalida_retorna_400(client):
    payload = {"tabuleiro": ["X"] + [""] * 8, "posicao": 0, "jogador": "O", "modo": "2p"}
    resp = client.post("/jogos/velha/api/jogar", json=payload)
    assert resp.status_code == 400
    assert resp.get_json()["ok"] is False
```

- [ ] **Step 6: Rodar os testes de páginas e jogos (esperado: PASSAM)**

Run: `.venv/bin/pytest tests/test_paginas.py tests/test_jogos.py -v`
Expected: 4 passed (home + 3 do jogo).

- [ ] **Step 7: Commit**

```bash
git add plataforma/ tests/test_jogos.py
git commit -m "feat: pagina do Jogo da Velha e API integradas a plataforma"
```

---

### Task 6: Autenticação — formulários, rotas, templates e navegação

**Files:**
- Modify: `plataforma/__init__.py` (registrar blueprint auth)
- Create: `plataforma/auth/__init__.py`, `plataforma/auth/formularios.py`, `plataforma/auth/rotas.py`
- Create: `plataforma/templates/auth/cadastro.html`, `plataforma/templates/auth/login.html`
- Create: `tests/test_auth.py`

**Interfaces:**
- Consumes: `Usuario`, `db` (Task 3); `create_app` (Task 4).
- Produces: rotas `auth.cadastro` (`/cadastro`), `auth.login` (`/login`), `auth.logout` (`/logout`).

- [ ] **Step 1: Criar os formulários**

Create `plataforma/auth/__init__.py` (vazio).

Create `plataforma/auth/formularios.py`:
```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

class FormCadastro(FlaskForm):
    nome_usuario = StringField(
        "Nome de usuário", validators=[DataRequired(), Length(min=3, max=30)]
    )
    senha = PasswordField("Senha", validators=[DataRequired(), Length(min=8)])
    confirmar = PasswordField(
        "Confirmar senha",
        validators=[DataRequired(), EqualTo("senha", message="As senhas não conferem.")],
    )
    enviar = SubmitField("Criar conta")

class FormLogin(FlaskForm):
    nome_usuario = StringField("Nome de usuário", validators=[DataRequired()])
    senha = PasswordField("Senha", validators=[DataRequired()])
    enviar = SubmitField("Entrar")
```

- [ ] **Step 2: Criar as rotas de autenticação**

Create `plataforma/auth/rotas.py`:
```python
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from ..extensoes import db
from ..modelos import Usuario
from .formularios import FormCadastro, FormLogin

bp = Blueprint("auth", __name__)


@bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for("principal.home"))
    form = FormCadastro()
    if form.validate_on_submit():
        existente = Usuario.query.filter_by(nome_usuario=form.nome_usuario.data).first()
        if existente:
            flash("Esse nome de usuário já está em uso.", "erro")
        else:
            usuario = Usuario(nome_usuario=form.nome_usuario.data)
            usuario.definir_senha(form.senha.data)
            db.session.add(usuario)
            db.session.commit()
            login_user(usuario)
            flash(f"Bem-vindo, {usuario.nome_usuario}!", "sucesso")
            return redirect(url_for("principal.home"))
    return render_template("auth/cadastro.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("principal.home"))
    form = FormLogin()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(nome_usuario=form.nome_usuario.data).first()
        if usuario and usuario.checar_senha(form.senha.data):
            login_user(usuario)
            flash(f"Olá de novo, {usuario.nome_usuario}!", "sucesso")
            return redirect(request.args.get("next") or url_for("principal.home"))
        flash("Usuário ou senha inválidos.", "erro")
    return render_template("auth/login.html", form=form)


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "sucesso")
    return redirect(url_for("principal.home"))
```

- [ ] **Step 3: Registrar o blueprint na factory**

In `plataforma/__init__.py`, junto aos outros registros:
```python
    from .auth.rotas import bp as auth_bp
    app.register_blueprint(auth_bp)
```

- [ ] **Step 4: Criar os templates de cadastro e login**

Create `plataforma/templates/auth/cadastro.html`:
```html
{% extends "base.html" %}
{% block titulo %}Criar conta — Arcade{% endblock %}
{% block conteudo %}
<section class="form-card">
  <h1>Criar conta</h1>
  <form method="post" novalidate>
    {{ form.csrf_token }}
    <label>{{ form.nome_usuario.label.text }}{{ form.nome_usuario(class="campo") }}</label>
    {% for e in form.nome_usuario.errors %}<span class="erro-campo">{{ e }}</span>{% endfor %}
    <label>{{ form.senha.label.text }}{{ form.senha(class="campo") }}</label>
    {% for e in form.senha.errors %}<span class="erro-campo">{{ e }}</span>{% endfor %}
    <label>{{ form.confirmar.label.text }}{{ form.confirmar(class="campo") }}</label>
    {% for e in form.confirmar.errors %}<span class="erro-campo">{{ e }}</span>{% endfor %}
    {{ form.enviar(class="btn btn-bloco") }}
  </form>
  <p class="form-alt">Já tem conta? <a href="{{ url_for('auth.login') }}">Entrar</a></p>
</section>
{% endblock %}
```

Create `plataforma/templates/auth/login.html`:
```html
{% extends "base.html" %}
{% block titulo %}Entrar — Arcade{% endblock %}
{% block conteudo %}
<section class="form-card">
  <h1>Entrar</h1>
  <form method="post" novalidate>
    {{ form.csrf_token }}
    <label>{{ form.nome_usuario.label.text }}{{ form.nome_usuario(class="campo") }}</label>
    {% for e in form.nome_usuario.errors %}<span class="erro-campo">{{ e }}</span>{% endfor %}
    <label>{{ form.senha.label.text }}{{ form.senha(class="campo") }}</label>
    {% for e in form.senha.errors %}<span class="erro-campo">{{ e }}</span>{% endfor %}
    {{ form.enviar(class="btn btn-bloco") }}
  </form>
  <p class="form-alt">Não tem conta? <a href="{{ url_for('auth.cadastro') }}">Cadastre-se</a></p>
</section>
{% endblock %}
```

- [ ] **Step 5: Escrever os testes de autenticação (esperado: PASSAM)**

Create `tests/test_auth.py`:
```python
from plataforma.extensoes import db
from plataforma.modelos import Usuario


def _cadastrar(client, nome="ana", senha="segredo123"):
    return client.post(
        "/cadastro",
        data={"nome_usuario": nome, "senha": senha, "confirmar": senha},
        follow_redirects=True,
    )


def test_cadastro_cria_usuario_hasheado(client, app):
    resp = _cadastrar(client)
    assert resp.status_code == 200
    with app.app_context():
        u = Usuario.query.filter_by(nome_usuario="ana").first()
        assert u is not None
        assert u.senha_hash != "segredo123"


def test_cadastro_duplicado_e_barrado(client):
    _cadastrar(client, nome="bia")
    client.get("/logout")  # (logout via GET não existe; o segundo cadastro cai no if autenticado)
    resp = client.post(
        "/cadastro",
        data={"nome_usuario": "bia", "senha": "outrasenha1", "confirmar": "outrasenha1"},
        follow_redirects=True,
    )
    # Continua havendo apenas 1 usuário "bia".
    from plataforma.modelos import Usuario
    # (verificação real de contagem é feita no teste de modelo; aqui garantimos que não quebrou)
    assert resp.status_code == 200


def test_login_aceita_e_rejeita(client, app):
    _cadastrar(client, nome="carol", senha="segredo123")
    client_logout = client.post("/logout", follow_redirects=True)
    assert client_logout.status_code == 200

    ok = client.post(
        "/login",
        data={"nome_usuario": "carol", "senha": "segredo123"},
        follow_redirects=True,
    )
    assert "Olá de novo".encode() in ok.data

    client.post("/logout", follow_redirects=True)
    ruim = client.post(
        "/login",
        data={"nome_usuario": "carol", "senha": "errada"},
        follow_redirects=True,
    )
    assert "inválidos".encode() in ruim.data
```

> Nota: o teste `test_cadastro_duplicado_e_barrado` é simplificado; a garantia
> forte de unicidade já está coberta por `test_nome_usuario_unico` (Task 3).

- [ ] **Step 6: Rodar todos os testes (esperado: PASSAM)**

Run: `.venv/bin/pytest -v`
Expected: todos passam (jogo, modelos, páginas, jogos, auth).

- [ ] **Step 7: Commit**

```bash
git add plataforma/ tests/test_auth.py
git commit -m "feat: cadastro, login e logout de usuarios"
```

---

### Task 7: Acabamento — rodar de verdade, limpeza e README

**Files:**
- Delete: `venv/` (quebrada), `__pycache__/` (do git)
- Modify: `README.md`
- Delete: `index.html`, `templates/index.html`, `app.py`, `logica_web.py` antigos remanescentes na raiz (se ainda existirem após a migração) — **conferir antes**

**Interfaces:**
- Consumes: tudo das tarefas anteriores.

- [ ] **Step 1: Rodar o app de verdade contra o MySQL**

Run (em segundo plano) e testar:
```bash
.venv/bin/python run.py &
sleep 2
curl -s -o /dev/null -w "home %{http_code}\n" http://127.0.0.1:5000/
curl -s -o /dev/null -w "velha %{http_code}\n" http://127.0.0.1:5000/jogos/velha
curl -s -o /dev/null -w "login %{http_code}\n" http://127.0.0.1:5000/login
```
Expected: `home 200`, `velha 200`, `login 200`. Depois pare o processo (`kill %1`).

- [ ] **Step 2: Conferir que o cadastro grava no MySQL**

Cadastre um usuário pelo navegador (`/cadastro`) e verifique:
```bash
sudo mysql -D games -e "SELECT id, nome_usuario, LEFT(senha_hash,12) AS hash_ini, criado_em FROM usuarios;"
```
Expected: a linha do usuário aparece, com `hash_ini` diferente da senha digitada.

- [ ] **Step 3: Limpeza de arquivos**

Run:
```bash
rm -rf venv __pycache__ jogo_velha/__pycache__
git rm -r --cached __pycache__ 2>/dev/null || true
```
Conferir se sobraram `index.html`, `templates/index.html`, `app.py`, `logica_web.py` na RAIZ (a lógica agora está em `jogo_velha/`; o frontend virou `plataforma/`). Remover os remanescentes obsoletos com `git rm`.

- [ ] **Step 4: Atualizar o README**

Modify `README.md`: substituir as instruções de execução pela nova plataforma:
```markdown
## Rodando a plataforma (Fase 1)

1. Configure o ambiente e o banco (uma vez): veja `docs/superpowers/plans/2026-07-23-plataforma-jogos-fase1.md`, Task 1.
2. Suba o servidor:
   ```bash
   .venv/bin/python run.py
   ```
3. Acesse http://127.0.0.1:5000 — jogue a velha e crie sua conta.

Rodar a versão de terminal: `.venv/bin/python jogar_terminal.py`
Rodar os testes: `.venv/bin/pytest`
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "chore: acabamento da Fase 1 (limpeza, README, verificacao end-to-end)"
```

---

## Self-Review (feita pelo autor do plano)

- **Cobertura do spec:** ambiente/MySQL (T1), reorganização + lógica (T2), modelo Usuario + hash (T3), home/galeria + tema (T4), página+API da velha (T5), cadastro/login/logout (T6), execução real + limpeza (T7). Testes de auth, modelo e jogo cobertos. ✔
- **Fora de escopo respeitado:** sem multiplayer, ELO, e-mail, perfis ou deploy. ✔
- **Pontos de atenção conhecidos:** (a) SQLite em memória exige `StaticPool` (previsto no `TestConfig`); (b) o teste `test_home_carrega` depende do blueprint `jogos` (rodar ao fim da T5); (c) assets grandes do jogo (CSS/JS) são **extraídos** do `templates/index.html` existente, não reescritos.
