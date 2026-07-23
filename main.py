# main.py
# PONTO DE ENTRADA do programa. É este arquivo que você executa:
#     python main.py
# A responsabilidade dele é mínima: apenas "ligar o motor" do jogo.

from jogo import iniciar_jogo

# Esta condição garante que o jogo só rode quando executamos ESTE arquivo
# diretamente — e não quando ele for importado por outro módulo.
# É uma boa prática muito comum em Python.
if __name__ == "__main__":
    iniciar_jogo()
