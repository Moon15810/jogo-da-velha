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
            proximo = request.args.get("next", "")
            # Só aceita caminho local relativo (evita open redirect para domínio externo).
            if not proximo.startswith("/") or proximo.startswith("//") or "\\" in proximo:
                proximo = url_for("principal.home")
            return redirect(proximo)
        flash("Usuário ou senha inválidos.", "erro")
    return render_template("auth/login.html", form=form)


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "sucesso")
    return redirect(url_for("principal.home"))
