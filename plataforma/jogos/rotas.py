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
