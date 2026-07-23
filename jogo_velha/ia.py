# ia.py
# Inteligência artificial IMBATÍVEL para o Jogo da Velha, usando o
# algoritmo MINIMAX.
#
# Ideia do Minimax:
#   A IA simula TODAS as jogadas possíveis até o fim de cada partida.
#   - Quando ela mesma joga, escolhe o caminho de MAIOR pontuação (maximiza).
#   - Quando o adversário joga, assume que ele fará a MELHOR jogada dele,
#     ou seja, o caminho de MENOR pontuação para a IA (minimiza).
#   Como o Jogo da Velha é pequeno, dá para explorar todas as possibilidades
#   e a IA nunca perde: no máximo empata.

from .tabuleiro import verificar_vitoria, verificar_empate, CASA_VAZIA


def _casas_vazias(tabuleiro):
    """Devolve a lista de posições (linha, coluna) que ainda estão livres."""
    return [
        (linha, coluna)
        for linha in range(3)
        for coluna in range(3)
        if tabuleiro[linha][coluna] == CASA_VAZIA
    ]


def _minimax(tabuleiro, simbolo_ia, simbolo_humano, vez_da_ia, profundidade):
    """
    Retorna a "nota" da posição atual do ponto de vista da IA.

    Notas usadas:
        +10  -> a IA venceu
        -10  -> o humano venceu
          0  -> empate
    Subtraímos/somamos a 'profundidade' para a IA preferir vencer RÁPIDO
    e, se for perder, perder o mais TARDE possível.
    """
    # --- Casos-base: a partida acabou nesta simulação? ---
    if verificar_vitoria(tabuleiro, simbolo_ia):
        return 10 - profundidade
    if verificar_vitoria(tabuleiro, simbolo_humano):
        return profundidade - 10
    if verificar_empate(tabuleiro):
        return 0

    if vez_da_ia:
        # A IA quer MAXIMIZAR a nota.
        melhor = -1000
        for linha, coluna in _casas_vazias(tabuleiro):
            tabuleiro[linha][coluna] = simbolo_ia          # tenta a jogada
            nota = _minimax(tabuleiro, simbolo_ia, simbolo_humano, False, profundidade + 1)
            tabuleiro[linha][coluna] = CASA_VAZIA          # desfaz (backtracking)
            melhor = max(melhor, nota)
        return melhor
    else:
        # O humano (adversário) quer MINIMIZAR a nota da IA.
        pior = 1000
        for linha, coluna in _casas_vazias(tabuleiro):
            tabuleiro[linha][coluna] = simbolo_humano
            nota = _minimax(tabuleiro, simbolo_ia, simbolo_humano, True, profundidade + 1)
            tabuleiro[linha][coluna] = CASA_VAZIA
            pior = min(pior, nota)
        return pior


def melhor_jogada(tabuleiro, simbolo_ia, simbolo_humano):
    """
    Decide a MELHOR jogada para a IA no tabuleiro atual.

    Retorna:
        tuple[int, int] | None: a posição (linha, coluna) escolhida,
        ou None se não houver casas livres.
    """
    melhor_nota = -1000
    escolha = None

    for linha, coluna in _casas_vazias(tabuleiro):
        tabuleiro[linha][coluna] = simbolo_ia
        # Depois da jogada da IA, é a vez do humano -> vez_da_ia=False.
        nota = _minimax(tabuleiro, simbolo_ia, simbolo_humano, False, 0)
        tabuleiro[linha][coluna] = CASA_VAZIA

        if nota > melhor_nota:
            melhor_nota = nota
            escolha = (linha, coluna)

    return escolha
