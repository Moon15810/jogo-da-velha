# Arcade — Plataforma de Jogos 🎮

Um site de jogos escrito em Python/Flask, com o **Jogo da Velha** como primeiro
título. Os jogos rodam no navegador; a lógica e a validação ficam no servidor
Python, e há contas de usuário (cadastro/login) como base para o ranking das
próximas fases.

> **Status:** Fase 1 (fundação) concluída — plataforma, contas e o Jogo da Velha
> jogável (2 jogadores e vs. IA). Multiplayer online e ranking (ELO) são as
> próximas fases. Veja `docs/superpowers/specs/` e `docs/superpowers/plans/`.

## Como rodar

Requer Python 3.12+ e MySQL.

### 1. Banco de dados (uma vez)

```bash
sudo apt install -y python3-venv mysql-server
sudo mysql -e "CREATE DATABASE IF NOT EXISTS games CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
               CREATE USER IF NOT EXISTS 'games_user'@'localhost' IDENTIFIED BY '12345678';
               GRANT ALL PRIVILEGES ON games.* TO 'games_user'@'localhost'; FLUSH PRIVILEGES;"
```

> A senha `12345678` é só para desenvolvimento local. Troque por uma senha forte
> (e ajuste o `.env`) antes de qualquer exposição pública.

### 2. Ambiente e dependências

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Crie o arquivo `.env` (veja `.env.example`):

```
SECRET_KEY=<gere com: python3 -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=mysql+pymysql://games_user:12345678@localhost/games
```

### 3. Suba o servidor

```bash
.venv/bin/python run.py
# abra http://127.0.0.1:5000
```

## Testes

Os testes usam SQLite em memória (não precisam do MySQL):

```bash
.venv/bin/python -m pytest
```

## Versão de terminal

O Jogo da Velha também roda no terminal (dois jogadores ou vs. IA):

```bash
.venv/bin/python jogar_terminal.py
```

## Estrutura do projeto

| Caminho | Responsabilidade |
| --- | --- |
| `run.py` | Ponto de entrada do servidor web. |
| `config.py` | Configuração (lê do `.env`); `Config` e `TestConfig`. |
| `plataforma/` | Aplicação Flask (app factory + blueprints). |
| `plataforma/__init__.py` | App factory: extensões e registro dos blueprints. |
| `plataforma/extensoes.py` | Instâncias de `db` (SQLAlchemy), `login_manager`, `csrf`. |
| `plataforma/modelos.py` | Modelo `Usuario` (senha hasheada). |
| `plataforma/auth/` | Cadastro, login e logout. |
| `plataforma/principal/` | Página inicial e galeria de jogos. |
| `plataforma/jogos/` | Página do Jogo da Velha e sua API. |
| `plataforma/templates/`, `plataforma/static/` | HTML, CSS e JS. |
| `jogo_velha/` | Lógica **pura** do Jogo da Velha (tabuleiro, IA Minimax, regras). |
| `tests/` | Testes (pytest). |
| `docs/superpowers/` | Specs e planos de implementação. |

## Segurança

- Senhas guardadas apenas como **hash** (Werkzeug).
- **CSRF** nos formulários (Flask-WTF); a API do jogo é isenta por ser stateless.
- Segredos no `.env` (fora do versionamento).
