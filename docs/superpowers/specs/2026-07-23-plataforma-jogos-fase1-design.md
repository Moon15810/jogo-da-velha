# Spec — Plataforma de Jogos · Fase 1: Fundação (Plataforma + Contas)

- **Data:** 2026-07-23
- **Status:** Aprovado (design)
- **Autor:** Cleiton + assistente
- **Projeto maior:** Site público de jogos, tendo o Jogo da Velha como primeiro jogo.

---

## 1. Contexto e visão

O projeto começou como um Jogo da Velha em Python (terminal, web offline e web
com Flask + IA). A nova visão é transformá-lo em um **site público de jogos**, com
o Jogo da Velha sendo o primeiro título.

A visão completa inclui: contas de usuário, **multiplayer online** (humano x
humano) e **ranking competitivo (ELO)**. Por ser grande e composta de vários
subsistemas independentes, a visão foi **decomposta em fases**, cada uma com seu
próprio ciclo design → plano → implementação.

### Roadmap das fases
1. **Fase 1 — Fundação: plataforma + contas** ← *este documento*
2. **Fase 2 — Multiplayer online** (WebSockets, salas, pareamento, servidor-juiz)
3. **Fase 3 — Ranking competitivo (ELO)** (rating, partidas gravadas, perfis)
4. **Fase 4+ — Mais jogos**, usando a arquitetura de "encaixar um jogo".

Construir a fundação primeiro **derrisca** MySQL, login e organização antes da
parte difícil (tempo real), pois o multiplayer depende de contas e da plataforma
já existirem.

---

## 2. Escopo da Fase 1

Entregar um **site público funcionando**, com:

- Estrutura de aplicação Flask organizada (app factory + blueprints).
- Banco **MySQL** acessado via **SQLAlchemy (ORM)**.
- **Contas de usuário:** cadastro, login, logout, sessões, senhas com hash.
- **Casca do site:** página inicial com **galeria de jogos** e página do Jogo da
  Velha integrada ao layout.
- **Jogo da Velha jogável** (2 jogadores local + vs IA), reaproveitando a lógica
  atual. Jogar é **aberto a todos** (não exige login).
- Identidade visual "tinta sobre papel quadriculado" estendida ao site todo.

### Critérios de sucesso
- Um visitante consegue abrir o site, ver a galeria e jogar a velha sem login.
- Um visitante consegue se cadastrar, sair e entrar novamente.
- Senhas ficam **hasheadas** no banco (nunca em texto puro).
- Testes automatizados de autenticação e da lógica do jogo passam.

---

## 3. Fora de escopo (YAGNI nesta fase)

Multiplayer / WebSockets · ranking / ELO · páginas de perfil · e-mail e
recuperação de senha ("esqueci a senha") · outros jogos além da velha ·
hospedagem/deploy público. Tudo isso pertence às fases seguintes.

---

## 4. Decisões e justificativas

| Decisão | Escolha | Por quê |
|---|---|---|
| Ambição do site | Público, sem exigir login para jogar | Acessibilidade; conta serve para salvar/rankear (futuro). |
| Contas | Cadastro obrigatório para salvar/rankear | Necessário para o ranking das próximas fases. |
| Banco | **MySQL**, banco `games` | Escolha do usuário. |
| Acesso ao banco | **SQLAlchemy (ORM)** | Segurança (anti-injeção), facilita relações/partidas/ELO das próximas fases. |
| Autenticação | Flask-Login + hash Werkzeug | Padrão, seguro, simples. |
| Formulários | Flask-WTF (com CSRF) | Validação + proteção CSRF de graça. |
| Cadastro | `nome_usuario` + `senha` | E-mail só quando existir recuperação de senha (YAGNI). |
| Identidade do jogador | Nome de usuário (público) | Sem login social; simples. |
| Testes | SQLite em memória | Rápidos e sem depender do MySQL no CI/local. |

---

## 5. Arquitetura

Aplicação **Flask** no padrão *app factory*, dividida em **blueprints** por área.
**Flask-SQLAlchemy** cuida da persistência no MySQL; **Flask-Login** cuida das
sessões; **Flask-WTF** dos formulários. A **lógica do jogo** permanece um pacote
Python **puro e reutilizável** — a camada web apenas a consome.

### Estrutura de pastas
```
jogo-da-velha/                 (repositório — a "plataforma de jogos")
├── run.py                     # ponto de entrada: cria e roda o app
├── config.py                  # configurações lidas do .env
├── .env.example               # modelo das variáveis (sem segredos)
├── .env                       # real (no .gitignore)
├── .gitignore
├── requirements.txt
│
├── plataforma/                # PACOTE da aplicação web (Flask)
│   ├── __init__.py            # app factory: cria app, extensões, blueprints
│   ├── extensoes.py           # db (SQLAlchemy), login_manager
│   ├── modelos.py             # modelo Usuario
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── rotas.py           # /cadastro, /login, /logout
│   │   └── formularios.py     # FormCadastro, FormLogin (Flask-WTF)
│   ├── principal/
│   │   ├── __init__.py
│   │   └── rotas.py           # / (home + galeria de jogos)
│   ├── jogos/
│   │   ├── __init__.py
│   │   └── rotas.py           # /jogos/velha + /jogos/velha/api/jogar
│   ├── templates/             # base.html + páginas (estendem base)
│   └── static/                # css/ (tema), js/ (jogo da velha)
│
├── jogo_velha/                # LÓGICA do jogo (pura) — módulos atuais migrados
│   ├── __init__.py
│   ├── tabuleiro.py
│   ├── ia.py
│   ├── logica_web.py
│   ├── jogador.py
│   └── terminal/              # versão de terminal (main/jogo/utils) — opcional
│
└── docs/superpowers/specs/    # specs do projeto
```

> A reorganização **move** os arquivos atuais para dentro dos pacotes
> `plataforma/` e `jogo_velha/`. Os imports serão atualizados de acordo.

---

## 6. Componentes (responsabilidade de cada um)

- **App factory** (`plataforma/__init__.py`): cria o app, carrega `config.py`,
  inicializa `db` e `login_manager`, registra os blueprints.
- **`extensoes.py`**: instâncias únicas de `db` (SQLAlchemy) e `login_manager`.
- **`modelos.py` → `Usuario`**: `UserMixin` + `id`, `nome_usuario`, `senha_hash`,
  `criado_em`; métodos `definir_senha()` e `checar_senha()`.
- **Blueprint `auth`**: `cadastro`, `login`, `logout`; usa `formularios.py`.
- **Blueprint `principal`**: home com a galeria (Fase 1: 1 card — Jogo da Velha).
- **Blueprint `jogos`**: página da velha (frontend dentro do `base.html`) e a API
  `POST /jogos/velha/api/jogar`, que reusa `jogo_velha.logica_web.processar_jogada`.
- **`base.html`**: cabeçalho/nav; deslogado → "Entrar / Cadastrar"; logado →
  "Olá, *nome* · Sair". Mensagens *flash* para feedback.

---

## 7. Modelo de dados (MySQL via SQLAlchemy)

Tabela **`usuarios`** (única nesta fase; schema pensado para crescer):

| coluna | tipo | restrições |
|---|---|---|
| `id` | INTEGER | PK, auto-incremento |
| `nome_usuario` | VARCHAR(30) | único, not null |
| `senha_hash` | VARCHAR(255) | not null |
| `criado_em` | DATETIME | default = agora (UTC) |

As tabelas são criadas via `db.create_all()` na Fase 1 (migrações com Alembic
ficam para quando o schema começar a evoluir, nas fases seguintes).

---

## 8. Rotas e fluxos

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Home + galeria de jogos |
| GET | `/jogos/velha` | Página do Jogo da Velha (aberta a todos) |
| POST | `/jogos/velha/api/jogar` | Processa jogada (reusa a lógica Python) |
| GET/POST | `/cadastro` | Formulário e criação de conta |
| GET/POST | `/login` | Formulário e início de sessão |
| POST | `/logout` | Encerra a sessão |

- **Cadastro:** valida (campos preenchidos, senha ≥ 8, `nome_usuario` livre) →
  cria `Usuario` com hash → autentica → redireciona para a home com flash de
  boas-vindas.
- **Login:** valida credenciais; em erro, mensagem **genérica** "usuário ou senha
  inválidos" (não revela qual dos dois falhou).
- **Logout:** encerra a sessão e volta para a home.
- **Jogar:** a página e a API funcionam com ou sem login (como hoje).

---

## 9. Segurança

- Senhas **hasheadas** (Werkzeug `generate_password_hash` / `check_password_hash`).
- **CSRF** em todos os formulários (Flask-WTF).
- SQL parametrizado pelo ORM (anti-injeção).
- `SECRET_KEY` e credenciais do banco **fora do código**, em `.env` (ignorado pelo
  git). `.env.example` documenta as variáveis sem valores sensíveis.
- Senha local `12345678` é aceita **apenas em desenvolvimento**; trocar por senha
  forte antes de qualquer exposição pública (Fase 2/hospedagem).

---

## 10. Tratamento de erros

- Formulários exibem mensagens claras por campo (usuário já existe, senha curta,
  campos vazios, credenciais inválidas).
- Banco indisponível → página/mensagem amigável em vez de stack trace.
- A API do jogo mantém `HTTP 400` + mensagem em jogada inválida (comportamento
  atual preservado).

---

## 11. Testes

- **Mantidos:** testes da lógica do jogo e da IA (Minimax) já existentes.
- **Novos (auth):** usando o *test client* do Flask com **SQLite em memória**:
  - cadastro cria usuário e grava senha **hasheada** (nunca texto puro);
  - login aceita a senha correta e rejeita a incorreta;
  - `nome_usuario` duplicado é barrado;
  - rota protegida (se houver) redireciona visitante deslogado.

---

## 12. Dependências

Somadas ao `Flask` já usado:
`Flask-SQLAlchemy`, `Flask-Login`, `Flask-WTF`, `PyMySQL` (driver MySQL),
`python-dotenv`. Registradas no `requirements.txt`.

---

## 13. Riscos e pendências

- **Setup do MySQL exige `sudo`** (instalar servidor, criar banco `games` e o
  usuário/senha). É o **passo 1 da implementação** e precisa da participação do
  Cleiton — o ambiente é restrito (PEP 668; `python3-venv` ausente).
- Instalação de dependências Python também esbarra no PEP 668 do Debian; solução:
  ambiente virtual (após `apt install python3-venv`) ou instalação isolada.
- Hospedagem pública real fica para a Fase 2 (a máquina local não serve o público
  sozinha).
