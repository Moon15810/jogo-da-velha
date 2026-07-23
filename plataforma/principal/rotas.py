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
