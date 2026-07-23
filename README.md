# Jogo da Velha (Tic-Tac-Toe) 🎮

Um Jogo da Velha completo, escrito em Python com foco em boas práticas e
separação de responsabilidades. Vem em **três formas de jogar**:

1. **Terminal** — dois jogadores no console.
2. **Web offline** — uma página HTML autossuficiente (abre direto no navegador).
3. **Web + Python (Flask)** — o navegador conversa com o Python, que valida as
   jogadas e ainda oferece um **modo contra a IA** imbatível (algoritmo Minimax).

---

## 1. Versão terminal

```bash
python3 main.py
```

- Digite o **número da linha** (1 a 3) e o **número da coluna** (1 a 3).
- Vence quem alinhar 3 símbolos em linha, coluna ou diagonal; senão, é empate.

## 2. Versão web offline

Abra o arquivo [`index.html`](index.html) no navegador (duplo-clique). Não precisa
de servidor. As regras rodam em JavaScript, no próprio navegador. Modo 2 jogadores.

## 3. Versão web com Python + IA (Flask)

Aqui o navegador só desenha: **quem manda nas regras é o Python**. Inclui o
**modo contra a IA**.

```bash
# 1) Crie um ambiente virtual e instale o Flask dentro dele (recomendado)
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 2) Suba o servidor
.venv/bin/python app.py

# 3) Abra no navegador
#    http://127.0.0.1:5000
```

> **Debian/Ubuntu:** se `python3 -m venv` reclamar de `ensurepip`, instale antes
> o pacote do venv: `sudo apt install python3-venv`. Como alternativa rápida (sem
> venv), dá para instalar direto com `pip install --break-system-packages -r
> requirements.txt` — mas isso mexe no Python do sistema, então o venv é preferível.

Escolha **"Contra a IA"** no topo da página para desafiar o computador. A IA usa
o algoritmo **Minimax**, então ela nunca perde — o melhor que dá é empatar. 😉

---

## Estrutura do projeto

| Arquivo               | Responsabilidade                                                              |
| --------------------- | ---------------------------------------------------------------------------- |
| `main.py`             | Ponto de entrada da versão de **terminal**.                                  |
| `jogo.py`             | Fluxo da partida no terminal (o "cérebro").                                  |
| `tabuleiro.py`        | Cria, exibe e atualiza o tabuleiro; verifica vitória (e qual trio venceu) e empate. |
| `jogador.py`          | Representa os jogadores e alterna os turnos.                                  |
| `utils.py`            | Funções auxiliares do terminal (limpar tela, ler números com segurança).     |
| `ia.py`               | **IA imbatível** com o algoritmo **Minimax**.                                |
| `logica_web.py`       | Processa uma jogada da web (valida, aplica, checa fim, aciona a IA) — sem Flask. |
| `app.py`              | Servidor **Flask**: serve a página e a API `/api/jogar`.                     |
| `templates/index.html`| Frontend da versão web com Python (modo 2 jogadores e vs. IA).               |
| `index.html`          | Frontend da versão web **offline** (só navegador, 2 jogadores).             |
| `requirements.txt`    | Dependências da versão web com Python (Flask).                               |

## Requisitos

- **Terminal / web offline:** Python 3.6+ (nada além da biblioteca padrão).
- **Web com Flask:** Python 3.8+ e o Flask (veja `requirements.txt`).

## Como a IA funciona (Minimax)

O Minimax simula **todas** as continuações possíveis da partida. Quando é a vez
da IA, ela escolhe o caminho de maior pontuação (vencer); quando é a vez do
adversário, assume que ele jogará da melhor forma possível (menor pontuação para
a IA). Como o Jogo da Velha tem poucas posições, dá para explorar tudo — e por
isso a IA é imbatível. O código está comentado em [`ia.py`](ia.py).
