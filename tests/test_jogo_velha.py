from jogo_velha.tabuleiro import criar_tabuleiro, verificar_vitoria, combo_vencedor, CASA_VAZIA
from jogo_velha.ia import melhor_jogada
from jogo_velha.logica_web import processar_jogada

E = CASA_VAZIA


def test_ia_fecha_vitoria():
    tab = [["O", "O", E], ["X", "X", E], [E, E, E]]
    assert melhor_jogada(tab, "O", "X") == (0, 2)


def test_ia_bloqueia_humano():
    tab = [["X", "X", E], [E, "O", E], [E, E, E]]
    assert melhor_jogada(tab, "O", "X") == (0, 2)


def test_combo_vencedor_diagonal():
    tab = [["X", E, E], [E, "X", E], [E, E, "X"]]
    assert combo_vencedor(tab, "X") == [(0, 0), (1, 1), (2, 2)]
    assert verificar_vitoria(tab, "X") is True


def test_humano_nunca_vence_a_ia():
    def humano_nunca_ganha(tab, vez_humano):
        if verificar_vitoria(tab, "X"):
            return False
        if verificar_vitoria(tab, "O"):
            return True
        livres = [(l, c) for l in range(3) for c in range(3) if tab[l][c] == E]
        if not livres:
            return True
        if vez_humano:
            for l, c in livres:
                tab[l][c] = "X"
                ok = humano_nunca_ganha(tab, False)
                tab[l][c] = E
                if not ok:
                    return False
            return True
        l, c = melhor_jogada(tab, "O", "X")
        tab[l][c] = "O"
        ok = humano_nunca_ganha(tab, True)
        tab[l][c] = E
        return ok

    assert humano_nunca_ganha(criar_tabuleiro(), True) is True


def test_processar_jogada_2p():
    r = processar_jogada([""] * 9, 0, "X", "2p")
    assert r["ok"] and r["tabuleiro"][0] == "X" and r["proximo"] == "O"


def test_processar_jogada_casa_ocupada():
    r = processar_jogada(["X"] + [""] * 8, 0, "O", "2p")
    assert r["ok"] is False and "ocupada" in r["erro"]


def test_processar_jogada_ia_responde():
    r = processar_jogada([""] * 9, 4, "X", "ia")
    assert r["tabuleiro"][4] == "X"
    assert r["jogada_ia"] in (0, 2, 6, 8)
    assert r["tabuleiro"].count("O") == 1
