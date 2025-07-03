import numpy as np
import pygame, sys, os
from qlearning_2 import QLearningAlgo

from game_logic import GameLogic


class GameScreen:
    def __init__(self):
        # Pygame:
        pygame.init()
        self.screen_size = 600
        self.game_screen = pygame.display.set_mode((self.screen_size, self.screen_size))
        pygame.display.set_caption("Cinco em linha")
        self.timer = pygame.time.Clock()
        # Lógica:
        self.game_logic = GameLogic()
        self.fully_ai = True
        self.draw_empate = False
        self.qlearning = QLearningAlgo(self.game_logic)
        self.jogador_atual = 0 # 0 = preto | 1 = branco
        self.cell_size = self.screen_size/self.game_logic.grid_size

        self.vitorias_pretas = 0
        self.vitorias_brancas = 0
        self.empates = 0
        self.numero_jogos = 0

    def encontrar_centro(self, linha, coluna, tamanho_celula):
        x = coluna * tamanho_celula + tamanho_celula // 2
        y = linha * tamanho_celula + tamanho_celula // 2
        return (x, y)

    def encontrar_posicao_do_mouse(self, pos, tamanho_celula):
        x, y = pos
        coluna = x // tamanho_celula
        linha = y // tamanho_celula
        #print(linha, coluna)
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
        # Checar vitória:
        color = self.game_logic.check_win()
        if color >= 0:
            color = "PRETAS" if color == 0 else "BRANCAS"
            if color == "PRETAS":
                self.vitorias_pretas += 1
            if color == "BRANCAS":
                self.vitorias_brancas += 1
            #print("VITÓRIA DAS " + color)
            pygame.event.get()
            pygame.event.get()
        if self.qlearning.is_board_full() or self.draw_empate:
            self.draw_empate = True
            self.empates += 1
        if self.draw_empate or type(color) == str:
            self.numero_jogos += 1
            print("\n"*100)
            print(f"Jogos: {self.numero_jogos}\n"
                  f"Vitórias pretas: {self.vitorias_pretas}\n"
                  f"Vitorias brancas: {self.vitorias_brancas}\n"
                  f"Empates: {self.empates}")
            #if self.draw_empate: print("EMPATE")
            self.draw_empate = False
            self.game_logic.matrix = np.full((self.game_logic.grid_size+6, self.game_logic.grid_size+6), -1)
        else:
            if self.fully_ai:
                pygame.event.get()
                if self.jogador_atual == 0:
                    teste = self.qlearning.find_row_to_place_move_agaisnt(False)
                    if teste:
                        # Há ameaça de três, ou quatro:
                        if teste[1]:
                            #print(teste[0].string)
                            self.qlearning.place_move_agaist_sequence(teste[0], False)
                            self.jogador_atual = 1
                        else:
                            teste2 = None
                            # Criar fileira:
                            if(self.qlearning.current_anchor_black):
                                teste2 = self.qlearning.attempt_to_fill_row(self.qlearning.current_anchor_black, False)
                            else:
                                teste2 = self.qlearning.attempt_to_fill_row(teste[0], False)
                            if teste2:
                                self.jogador_atual = 1
                    else:
                        self.draw_empate = True
                else:
                        teste = self.qlearning.find_row_to_place_move_agaisnt(True)
                        if teste:
                            # Há ameaça de três, ou quatro:
                            if teste[1]:
                                #print(teste[0].string)
                                self.qlearning.place_move_agaist_sequence(teste[0], True)
                                self.jogador_atual = 0
                            else:
                                teste2 = None
                                # Criar fileira:
                                if(self.qlearning.current_anchor_white):
                                    teste2 = self.qlearning.attempt_to_fill_row(self.qlearning.current_anchor_white, True)
                                else:
                                    teste2 = self.qlearning.attempt_to_fill_row(teste[0], True)
                                if teste2:
                                    self.jogador_atual = 0
                        else:
                            self.draw_empate = True
            else:
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if self.jogador_atual == 0:
                        if evento.type == pygame.MOUSEBUTTONDOWN:
                            linha, coluna = self.encontrar_posicao_do_mouse(pygame.mouse.get_pos(), self.cell_size)
                            if self.game_logic.matrix[linha][coluna] == -1:
                                self.game_logic.make_move(False, linha, coluna)
                            self.jogador_atual = 1
                    elif self.jogador_atual == 1:
                        teste = self.qlearning.find_row_to_place_move_agaisnt(True)
                        if teste:
                            # Há ameaça de três, ou quatro:
                            if teste[1]:
                                self.qlearning.place_move_agaist_sequence(teste[0], True)
                                self.jogador_atual = 0
                            else:
                                teste2 = None
                                # Criar fileira:
                                if(self.qlearning.current_anchor_white):
                                    teste2 = self.qlearning.attempt_to_fill_row(self.qlearning.current_anchor_white, True)
                                else:
                                    teste2 = self.qlearning.attempt_to_fill_row(teste[0], True)
                                if teste2:
                                    self.jogador_atual = 0
                        else:
                            self.draw_empate = True
        self.desenhar_tabuleiro()
        pygame.display.flip()
        self.timer.tick(5)

game_screen = GameScreen()

while True:
    game_screen.idle()
