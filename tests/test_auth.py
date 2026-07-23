from plataforma.extensoes import db
from plataforma.modelos import Usuario


def _cadastrar(client, nome="ana", senha="segredo123"):
    return client.post(
        "/cadastro",
        data={"nome_usuario": nome, "senha": senha, "confirmar": senha},
        follow_redirects=True,
    )


def test_cadastro_cria_usuario_hasheado(client, app):
    resp = _cadastrar(client)
    assert resp.status_code == 200
    with app.app_context():
        u = Usuario.query.filter_by(nome_usuario="ana").first()
        assert u is not None
        assert u.senha_hash != "segredo123"


def test_cadastro_duplicado_e_barrado(client, app):
    _cadastrar(client, nome="bia")                    # cria e já loga "bia"
    client.post("/logout", follow_redirects=True)     # logout é POST
    resp = client.post(
        "/cadastro",
        data={"nome_usuario": "bia", "senha": "outrasenha1", "confirmar": "outrasenha1"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "já está em uso".encode() in resp.data
    with app.app_context():
        assert Usuario.query.filter_by(nome_usuario="bia").count() == 1


def test_login_aceita_e_rejeita(client):
    _cadastrar(client, nome="carol", senha="segredo123")
    client.post("/logout", follow_redirects=True)

    ok = client.post(
        "/login",
        data={"nome_usuario": "carol", "senha": "segredo123"},
        follow_redirects=True,
    )
    assert "Olá de novo".encode() in ok.data

    client.post("/logout", follow_redirects=True)
    ruim = client.post(
        "/login",
        data={"nome_usuario": "carol", "senha": "errada"},
        follow_redirects=True,
    )
    assert "inválidos".encode() in ruim.data


def test_logout_exige_login(client):
    # /logout é protegido por login_required: visitante deslogado é redirecionado.
    resp = client.post("/logout")
    assert resp.status_code == 302
