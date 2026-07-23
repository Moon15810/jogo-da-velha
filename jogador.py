# jogador.py
# Responsável por representar os JOGADORES e a alternância de turnos.

def criar_jogador(nome, simbolo):
    """
    Cria um jogador.

    Representamos cada jogador como um DICIONÁRIO (dict), que guarda
    pares "chave: valor". É uma forma simples de agrupar informações
    relacionadas — aqui, o nome e o símbolo (X ou O) do jogador.

    Retorna:
        dict: por exemplo {"nome": "Jogador 1", "simbolo": "X"}.
    """
    return {"nome": nome, "simbolo": simbolo}


def trocar_jogador(jogador_atual, jogador_x, jogador_o):
    """
    Alterna o turno: dado o jogador atual, devolve o OUTRO jogador.

    Usamos 'is' para comparar se é o MESMO objeto na memória (identidade),
    o que deixa a intenção bem clara.
    """
    if jogador_atual is jogador_x:
        return jogador_o
    return jogador_x
