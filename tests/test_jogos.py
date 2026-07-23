import json


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
