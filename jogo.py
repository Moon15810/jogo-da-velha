# jogo.py
# O "cérebro" do jogo: controla o fluxo da partida, junta as peças
# (tabuleiro, jogadores e utilitários) e decide quando o jogo termina.

# Importamos apenas as funções que precisamos de cada módulo.
from tabuleiro import (
    criar_tabuleiro,
    mostrar_tabuleiro,
    validar_jogada,
    realizar_jogada,
    verificar_vitoria,
    verificar_empate,
)
from jogador import criar_jogador, trocar_jogador
from utils import limpar_tela, ler_inteiro


def jogar_partida(jogador_x, jogador_o):
    """
    Executa UMA partida completa, do tabuleiro vazio até o fim
    (vitória ou empate).
    """
    tabuleiro = criar_tabuleiro()   # (1) Tabuleiro novinho em folha.
    jogador_atual = jogador_x       # X sempre começa.

    # O loop principal do jogo. Só sai daqui quando alguém vence ou empata.
    while True:
        limpar_tela()
        mostrar_tabuleiro(tabuleiro)  # (1) Mostra o tabuleiro atual.

        # (2) Informa de quem é a vez.
        print(f"Vez de {jogador_atual['nome']} ({jogador_atual['simbolo']})")

        # (3) Solicita linha e coluna. O jogador digita de 1 a 3, mas
        # internamente o tabuleiro usa índices de 0 a 2 — por isso o "- 1".
        linha = ler_inteiro("Escolha a linha (1-3): ") - 1
        coluna = ler_inteiro("Escolha a coluna (1-3): ") - 1

        # (4) Valida a jogada.
        valido, mensagem = validar_jogada(tabuleiro, linha, coluna)
        if not valido:
            print(mensagem)
            input("Pressione Enter para tentar de novo...")
            continue  # Volta ao início do loop SEM trocar de jogador.

        # (5) Atualiza o tabuleiro com a jogada.
        realizar_jogada(tabuleiro, linha, coluna, jogador_atual["simbolo"])

        # (6) Verifica vitória do jogador que acabou de jogar.
        if verificar_vitoria(tabuleiro, jogador_atual["simbolo"]):
            limpar_tela()
            mostrar_tabuleiro(tabuleiro)
            print(f"🎉 {jogador_atual['nome']} ({jogador_atual['simbolo']}) venceu!")
            break

        # (7) Verifica empate (tabuleiro cheio, sem vencedor).
        if verificar_empate(tabuleiro):
            limpar_tela()
            mostrar_tabuleiro(tabuleiro)
            print("Deu velha! O jogo terminou em empate.")
            break

        # (8) Ninguém venceu e não empatou → troca o jogador e (9) repete.
        jogador_atual = trocar_jogador(jogador_atual, jogador_x, jogador_o)


def reiniciar_partida():
    """
    (10) Pergunta se o jogador quer jogar de novo.

    Retorna:
        bool: True se a resposta começar com 's' (sim), False caso contrário.
    """
    resposta = input("Deseja jogar novamente? (s/n): ").strip().lower()
    return resposta.startswith("s")


def iniciar_jogo():
    """
    Ponto de partida da lógica do jogo:
      - cria os dois jogadores;
      - joga partidas em sequência enquanto o usuário quiser.
    """
    jogador_x = criar_jogador("Jogador 1", "X")
    jogador_o = criar_jogador("Jogador 2", "O")

    print("=== JOGO DA VELHA ===")
    print(f"{jogador_x['nome']} é o X e {jogador_o['nome']} é o O. O X começa!\n")
    input("Pressione Enter para começar...")

    # Joga uma partida; se o jogador quiser, joga outra, e assim por diante.
    continuar = True
    while continuar:
        jogar_partida(jogador_x, jogador_o)
        continuar = reiniciar_partida()

    print("Obrigado por jogar! 👋")
