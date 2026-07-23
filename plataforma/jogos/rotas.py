from flask import Blueprint, render_template, request, jsonify

from jogo_velha.logica_web import processar_jogada
from ..extensoes import csrf

bp = Blueprint("jogos", __name__, url_prefix="/jogos")


@bp.route("/velha")
def velha():
    return render_template("jogos/velha.html")


@bp.route("/velha/api/jogar", methods=["POST"])
@csrf.exempt  # API stateless, sem sessão/DB: CSRF não protege nada aqui
def velha_api_jogar():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify({"ok": False, "erro": "Requisição inválida."}), 400

    tabuleiro = dados.get("tabuleiro")
    posicao = dados.get("posicao")
    humano = dados.get("jogador", "X")
    modo = dados.get("modo", "2p")

    # Valida a entrada ANTES de chamar a lógica (evita 500 em entrada malformada).
    if (
        not isinstance(tabuleiro, list)
        or len(tabuleiro) != 9
        or not all(casa in ("", "X", "O") for casa in tabuleiro)
        or isinstance(posicao, bool)
        or not isinstance(posicao, int)
        or not (0 <= posicao <= 8)
        or humano not in ("X", "O")
        or modo not in ("2p", "ia")
    ):
        return jsonify({"ok": False, "erro": "Jogada inválida."}), 400

    resultado = processar_jogada(lista=tabuleiro, posicao=posicao, humano=humano, modo=modo)
    return jsonify(resultado), (200 if resultado["ok"] else 400)
