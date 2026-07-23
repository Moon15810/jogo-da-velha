def test_pagina_velha_carrega(client):
    resp = client.get("/jogos/velha")
    assert resp.status_code == 200


def test_api_jogada_valida_2p(client):
    payload = {"tabuleiro": [""] * 9, "posicao": 4, "jogador": "X", "modo": "2p"}
    resp = client.post("/jogos/velha/api/jogar", json=payload)
    assert resp.status_code == 200
    dados = resp.get_json()
    assert dados["ok"] is True
    assert dados["tabuleiro"][4] == "X"


def test_api_jogada_invalida_retorna_400(client):
    payload = {"tabuleiro": ["X"] + [""] * 8, "posicao": 0, "jogador": "O", "modo": "2p"}
    resp = client.post("/jogos/velha/api/jogar", json=payload)
    assert resp.status_code == 400
    assert resp.get_json()["ok"] is False


def test_api_entrada_malformada_retorna_400(client):
    # posicao ausente
    assert client.post("/jogos/velha/api/jogar", json={"tabuleiro": [""] * 9}).status_code == 400
    # tabuleiro curto
    assert client.post("/jogos/velha/api/jogar", json={"tabuleiro": [], "posicao": 0}).status_code == 400
    # corpo não-dict
    assert client.post("/jogos/velha/api/jogar", json=[]).status_code == 400
    # posicao fora do range
    assert client.post("/jogos/velha/api/jogar", json={"tabuleiro": [""] * 9, "posicao": 99}).status_code == 400


def test_api_funciona_com_csrf_ligado():
    # Garante que a isenção de CSRF na API não regrida: mesmo com CSRF ligado,
    # a jogada deve funcionar (200), pois o fetch do frontend não envia token.
    from plataforma import create_app
    from config import TestConfig

    class ConfigCSRF(TestConfig):
        WTF_CSRF_ENABLED = True

    cliente = create_app(ConfigCSRF).test_client()
    resp = cliente.post(
        "/jogos/velha/api/jogar",
        json={"tabuleiro": [""] * 9, "posicao": 4, "jogador": "X", "modo": "2p"},
    )
    assert resp.status_code == 200
