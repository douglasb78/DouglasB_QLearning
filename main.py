import pygame, sys

from game_logic import GameLogic
from qlearning import QLearning, LS, Sequence


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
        self.threat = None
        self.jogador_atual = 0 # 0 = preto | 1 = branco
        self.cell_size = self.screen_size/self.game_logic.grid_size

    def set_threat(self, threat:Sequence):
        self.threat = threat

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
        if self.threat:
            pygame.draw.line(self.game_screen, "red", self.encontrar_centro(self.threat.start[0], self.threat.start[1], self.cell_size), self.encontrar_centro(self.threat.end[0], self.threat.end[1], self.cell_size))

    def idle(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if self.jogador_atual == 0:
                print(self.jogador_atual)
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    linha, coluna = self.encontrar_posicao_do_mouse(pygame.mouse.get_pos(), self.cell_size)
                    if self.game_logic.matrix[linha][coluna] == -1:
                        self.game_logic.matrix[linha][coluna] = self.jogador_atual
                    self.jogador_atual = 1
            else:
                self.qlearning.play_move(self.threat, self.game_logic)
                self.jogador_atual = 0
        # Checar vitória:
        color = self.game_logic.check_win()
        if color >= 0:
            color = "PRETAS" if color == 0 else "BRANCAS"
            print("VITÓRIA DAS " + color)
        if self.jogador_atual == 1:
            threat = self.qlearning.detect_threats()
            if threat:
                print(threat.string, threat.seq_type, threat.start, threat.end)
                print(self.qlearning.get_sequence(threat))
                self.set_threat(threat)
            else:
                self.set_threat(None)
        self.desenhar_tabuleiro()
        pygame.display.flip()
        self.timer.tick(180)

game_screen = GameScreen()

while True:
    game_screen.idle()
