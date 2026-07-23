def test_home_carrega(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Jogo da Velha".encode() in resp.data
