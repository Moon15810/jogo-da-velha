# utils.py
# "Caixa de ferramentas": funções auxiliares genéricas, que não pertencem
# especificamente ao tabuleiro nem ao jogador.

import os  # Módulo padrão do Python para interagir com o sistema operacional.


def limpar_tela():
    """
    Limpa o terminal para o tabuleiro sempre aparecer "no lugar".

    O comando muda conforme o sistema:
      - Windows (os.name == "nt")  -> 'cls'
      - Linux / macOS              -> 'clear'
    """
    os.system("cls" if os.name == "nt" else "clear")


def ler_inteiro(mensagem):
    """
    Lê um número inteiro digitado pelo usuário, com TRATAMENTO DE ERROS.

    Se o usuário digitar algo que não é um número (ex.: "abc"), o Python
    lançaria um erro (ValueError) e o programa quebraria. Com try/except,
    capturamos esse erro e simplesmente pedimos de novo, sem travar.

    O 'while True' repete até conseguirmos um inteiro válido.
    """
    while True:
        try:
            return int(input(mensagem))  # Tenta converter o texto em inteiro.
        except ValueError:
            # Só cai aqui se a conversão falhar.
            print("Entrada inválida! Digite um número inteiro.")
