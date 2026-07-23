# logica_web.py
# Lógica que processa uma jogada vinda do navegador, SEM depender do Flask.
#
# Por que separar isto do app.py?
#   - O app.py cuida do "encanamento" web (rotas, JSON, HTTP).
#   - Este módulo cuida das REGRAS. Como não importa o Flask, ele pode ser
#     testado com um simples 'python' — outra aplicação de SEPARAÇÃO DE
#     RESPONSABILIDADES.
#
# Formato do tabuleiro trocado com o navegador: uma LISTA de 9 posições,
# onde cada posição é "X", "O" ou "" (vazia). Aqui convertemos para a
# MATRIZ 3x3 usada pelo restante do projeto e vice-versa.

from .tabuleiro import (
    validar_jogada,
    realizar_jogada,
    verificar_vitoria,
    verificar_empate,
    combo_vencedor,
    CASA_VAZIA,
)
from .ia import melhor_jogada


def para_matriz(lista):
    """Lista de 9 posições -> matriz 3x3 do jogo ('' vira CASA_VAZIA)."""
    return [
        [(lista[linha * 3 + coluna] or CASA_VAZIA) for coluna in range(3)]
        for linha in range(3)
    ]


def para_lista(tabuleiro):
    """Matriz 3x3 do jogo -> lista de 9 posições (CASA_VAZIA vira '')."""
    return [
        (tabuleiro[linha][coluna] if tabuleiro[linha][coluna] != CASA_VAZIA else "")
        for linha in range(3)
        for coluna in range(3)
    ]


def combo_em_indices(tabuleiro, simbolo):
    """Trio vencedor como índices 0..8 (ou None), para o frontend desenhar."""
    trio = combo_vencedor(tabuleiro, simbolo)
    if trio is None:
        return None
    return [linha * 3 + coluna for linha, coluna in trio]


def _resultado(tabuleiro, jogada_ia, status, vencedor, proximo):
    """Monta o dicionário-padrão de resposta."""
    return {
        "ok": True,
        "tabuleiro": para_lista(tabuleiro),
        "jogada_ia": jogada_ia,       # índice 0..8 que a IA jogou, ou None
        "status": status,             # "em_andamento" | "vitoria" | "empate"
        "vencedor": vencedor,         # "X" | "O" | None
        "combo": combo_em_indices(tabuleiro, vencedor) if vencedor else None,
        "proximo": proximo,           # de quem é a próxima vez, ou None
    }


def processar_jogada(lista, posicao, humano="X", modo="2p"):
    """
    Processa uma jogada do humano e devolve o novo estado do jogo (um dict).

    Passos:
      1. valida a jogada;
      2. aplica a jogada do humano;
      3. checa vitória/empate;
      4. no modo "ia", o computador responde na mesma chamada.
    """
    tabuleiro = para_matriz(lista)
    linha, coluna = posicao // 3, posicao % 3

    # 1) Valida (mesma regra do jogo de terminal).
    valido, mensagem = validar_jogada(tabuleiro, linha, coluna)
    if not valido:
        return {"ok": False, "erro": mensagem}

    # 2) Aplica a jogada do humano.
    realizar_jogada(tabuleiro, linha, coluna, humano)

    # 3) O humano venceu ou empatou já nesta jogada?
    if verificar_vitoria(tabuleiro, humano):
        return _resultado(tabuleiro, None, "vitoria", humano, None)
    if verificar_empate(tabuleiro):
        return _resultado(tabuleiro, None, "empate", None, None)

    adversario = "O" if humano == "X" else "X"

    # 4) Modo contra a IA: o computador joga em seguida.
    if modo == "ia":
        linha_ia, coluna_ia = melhor_jogada(tabuleiro, adversario, humano)
        realizar_jogada(tabuleiro, linha_ia, coluna_ia, adversario)
        jogada_ia = linha_ia * 3 + coluna_ia

        if verificar_vitoria(tabuleiro, adversario):
            return _resultado(tabuleiro, jogada_ia, "vitoria", adversario, None)
        if verificar_empate(tabuleiro):
            return _resultado(tabuleiro, jogada_ia, "empate", None, None)
        return _resultado(tabuleiro, jogada_ia, "em_andamento", None, humano)

    # 5) Modo 2 jogadores: passa a vez.
    return _resultado(tabuleiro, None, "em_andamento", None, adversario)
