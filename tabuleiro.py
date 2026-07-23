# tabuleiro.py
# Responsável por tudo que diz respeito ao TABULEIRO do jogo:
# criar, exibir, atualizar as casas e verificar vitória/empate.

# CASA_VAZIA é uma "constante": um valor que não muda durante o programa.
# Por convenção, constantes são escritas em MAIÚSCULAS.
# Usar uma constante (em vez de espalhar " " pelo código todo) facilita a
# manutenção: se um dia quisermos mudar o símbolo de "vazio", mudamos só aqui.
CASA_VAZIA = " "


def criar_tabuleiro():
    """
    Cria e devolve um tabuleiro 3x3 vazio.

    O tabuleiro é uma MATRIZ: uma lista que contém 3 listas.
    Cada lista interna representa uma LINHA com 3 colunas.

    Retorna:
        list[list[str]]: matriz 3x3 preenchida com casas vazias.
    """
    tabuleiro = []  # Começamos com uma lista vazia (que vai guardar as linhas).

    # O loop 'for' repete o bloco abaixo 3 vezes (uma por linha).
    # Usamos '_' como nome da variável porque não vamos usar o número da
    # repetição — é só uma convenção para dizer "não me importo com esse valor".
    for _ in range(3):
        # Cada linha é uma lista NOVA com 3 casas vazias.
        linha = [CASA_VAZIA, CASA_VAZIA, CASA_VAZIA]
        tabuleiro.append(linha)  # Adiciona a linha ao tabuleiro.

    return tabuleiro  # Devolve a matriz pronta para quem chamou a função.


def mostrar_tabuleiro(tabuleiro):
    """
    Desenha o tabuleiro no terminal, com números de linha e coluna
    para o jogador se orientar. Exemplo:

           1   2   3
        1  X | O | X
          ---+---+---
        2    | X |
          ---+---+---
        3  O |   | O
    """
    # Cabeçalho com os números das colunas (1, 2, 3).
    print("   " + "   ".join(["1", "2", "3"]))

    # enumerate() devolve, a cada volta, o índice (i) e o valor (linha).
    # i vai de 0 a 2; mostramos i + 1 (1 a 3) porque é mais natural ao jogador.
    for i, linha in enumerate(tabuleiro):
        # " | ".join(...) junta os símbolos da linha com " | " no meio.
        # Ex.: [" ", "X", " "] vira "  | X |  ".
        print(f"{i + 1}  " + " | ".join(linha))

        # Imprime a linha separadora entre as linhas — mas não depois da última.
        if i < 2:
            print("  " + "+".join(["---", "---", "---"]))

    print()  # Linha em branco no final, só para dar um respiro visual.


def validar_jogada(tabuleiro, linha, coluna):
    """
    Verifica se uma jogada é válida.

    Recebe linha e coluna já convertidas para índices (0 a 2).
    Retorna uma TUPLA (valido, mensagem):
        - valido (bool): True se a jogada pode ser feita.
        - mensagem (str): explicação do erro (vazia se estiver tudo certo).
    """
    # 1) A posição precisa estar dentro do tabuleiro (índices de 0 a 2).
    if linha < 0 or linha > 2 or coluna < 0 or coluna > 2:
        return False, "Posição fora do tabuleiro! Use números de 1 a 3."

    # 2) A casa escolhida não pode estar ocupada.
    if tabuleiro[linha][coluna] != CASA_VAZIA:
        return False, "Essa casa já está ocupada! Escolha outra."

    # Passou nas duas checagens → jogada válida.
    return True, ""


def realizar_jogada(tabuleiro, linha, coluna, simbolo):
    """
    Coloca o símbolo do jogador (X ou O) na posição escolhida.
    Assume que a jogada já foi validada por validar_jogada().
    """
    tabuleiro[linha][coluna] = simbolo


def combo_vencedor(tabuleiro, simbolo):
    """
    Descobre QUAL trio de casas forma a vitória do 'simbolo'.

    Uma vitória acontece quando 3 símbolos iguais formam uma
    LINHA, uma COLUNA ou uma DIAGONAL.

    Retorna:
        list[tuple[int, int]] | None: as 3 posições (linha, coluna) vencedoras,
        ou None se o símbolo ainda não venceu. Serve, por exemplo, para
        destacar a linha vencedora na tela.
    """
    # Montamos uma lista com TODAS as combinações que dão vitória.
    # Aqui guardamos as POSIÇÕES (linha, coluna), não os valores.
    combinacoes = []

    # As 3 linhas.
    for i in range(3):
        combinacoes.append([(i, 0), (i, 1), (i, 2)])

    # As 3 colunas.
    for j in range(3):
        combinacoes.append([(0, j), (1, j), (2, j)])

    # As 2 diagonais.
    combinacoes.append([(0, 0), (1, 1), (2, 2)])
    combinacoes.append([(0, 2), (1, 1), (2, 0)])

    for trio in combinacoes:
        # all(...) só é True se TODAS as casas do trio forem o símbolo.
        if all(tabuleiro[linha][coluna] == simbolo for linha, coluna in trio):
            return trio

    return None  # Nenhuma combinação fechada por esse símbolo.


def verificar_vitoria(tabuleiro, simbolo):
    """
    Verifica se o jogador do 'simbolo' venceu (linha, coluna ou diagonal).

    Reaproveita combo_vencedor(): se existe um trio vencedor, houve vitória.

    Retorna:
        bool: True se houver vitória, False caso contrário.
    """
    return combo_vencedor(tabuleiro, simbolo) is not None


def verificar_empate(tabuleiro):
    """
    Verifica se a partida terminou em empate ("deu velha").

    Deve ser chamada DEPOIS de checar a vitória. Se não houve vencedor
    e não sobrou nenhuma casa vazia, é empate.

    Retorna:
        bool: True se o tabuleiro estiver cheio, False se ainda há espaço.
    """
    for linha in tabuleiro:
        if CASA_VAZIA in linha:
            return False  # Achou casa vazia → o jogo ainda pode continuar.
    return True  # Nenhuma casa vazia → empate.
