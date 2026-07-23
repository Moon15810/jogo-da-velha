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
