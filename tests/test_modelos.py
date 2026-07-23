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
