# app.py
# A "PONTE" entre o navegador e o Python: um servidor web feito com Flask.
#
# Este arquivo é PROPOSITALMENTE fino: ele só cuida do "encanamento" web
# (servir a página e receber/responder JSON). Toda a REGRA do jogo mora em
# logica_web.py, que por sua vez usa tabuleiro.py e ia.py.

from flask import Flask, request, jsonify, render_template

from logica_web import processar_jogada

app = Flask(__name__)


@app.route("/")
def index():
    """Entrega a página do jogo (templates/index.html)."""
    return render_template("index.html")


@app.route("/api/jogar", methods=["POST"])
def jogar():
    """
    Recebe uma jogada do navegador em JSON, processa no Python e responde.

    Corpo esperado:
        {
          "tabuleiro": ["X","","O", ...],  # 9 posições ANTES da jogada
          "posicao": 4,                     # índice 0..8 onde o humano jogou
          "jogador": "X",                   # símbolo do humano
          "modo": "ia"                      # "ia" (contra IA) ou "2p"
        }
    """
    dados = request.get_json(force=True)
    resultado = processar_jogada(
        lista=dados.get("tabuleiro", [""] * 9),
        posicao=dados.get("posicao"),
        humano=dados.get("jogador", "X"),
        modo=dados.get("modo", "2p"),
    )
    # Jogada inválida -> HTTP 400; caso contrário -> 200.
    return jsonify(resultado), (200 if resultado["ok"] else 400)


if __name__ == "__main__":
    # debug=True recarrega o servidor ao salvar arquivos (útil no desenvolvimento).
    app.run(host="127.0.0.1", port=5000, debug=True)
