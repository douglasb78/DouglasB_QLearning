import pygame, sys

from game_logic import GameLogic
from qlearning import QLearning

class GameScreen:
    def __init__(self):
        # Pygame:
        pygame.init()
        self.screen_size = 600
        self.game_screen = pygame.display.set_mode((self.screen_size, self.screen_size))
        pygame.display.set_caption("Five-in-a-row")
        self.timer = pygame.time.Clock()
        # Lógica:
        self.game_logic = GameLogic()
        self.qlearning = QLearning(self.game_logic)
        self.jogador_atual = 0 # 0 = preto | 1 = branco
        self.cell_size = self.screen_size/self.game_logic.grid_size

    def encontrar_centro(self, linha, coluna, tamanho_celula):
        x = coluna * tamanho_celula + tamanho_celula // 2
        y = linha * tamanho_celula + tamanho_celula // 2
        return (x, y)

    def encontrar_posicao_do_mouse(self, pos, tamanho_celula):
        x, y = pos
        coluna = x // tamanho_celula
        linha = y // tamanho_celula
        print(linha, coluna)
        return int(linha), int(coluna)

    def desenhar_tabuleiro(self):
        self.game_screen.fill("white")
        for i in range(self.game_logic.grid_size + 1):
            pygame.draw.line(self.game_screen, "gray", (0, i * self.cell_size), (self.screen_size, i * self.cell_size))
        for j in range(self.game_logic.grid_size):
            pygame.draw.line(self.game_screen, "gray", (j * self.cell_size, 0), (j * self.cell_size, self.screen_size))

        for i in range(self.game_logic.grid_size):
            for j in range(self.game_logic.grid_size):
                if self.game_logic.matrix[i][j] == 0:
                    pygame.draw.circle(self.game_screen, "black", self.encontrar_centro(i, j, self.cell_size), self.cell_size/2.5)
                elif self.game_logic.matrix[i][j] == 1:
                    pygame.draw.circle(self.game_screen, "gray", self.encontrar_centro(i, j, self.cell_size), self.cell_size/2.5)

    def idle(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                linha, coluna = self.encontrar_posicao_do_mouse(pygame.mouse.get_pos(), self.cell_size)
                if self.game_logic.matrix[linha][coluna] == -1:
                    self.game_logic.matrix[linha][coluna] = self.jogador_atual
                    # trocar jogador:
                    self.jogador_atual = 0 if self.jogador_atual == 1 else 1
        if self.jogador_atual == 1:
            threat = self.qlearning.detect_threats()
            if threat:
                print(threat.string, threat.seq_type, threat.start, threat.end)
            # TODO: Pôr detecção de double threat.
            # TODO: Ele tá caindo fora se acha um useful, um caution. Tem que priorizar salvar de derrota.
        color = self.game_logic.check_win()
        if color >= 0:
            color = "PRETAS" if color == 0 else "BRANCAS"
            print("VITÓRIA DAS " + color)
        self.desenhar_tabuleiro()
        pygame.display.flip()
        self.timer.tick(180)

game_screen = GameScreen()

while True:
    game_screen.idle()
