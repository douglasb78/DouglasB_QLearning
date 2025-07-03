from enum import Enum

import numpy as np

class LS(Enum):
    HORIZONTAL_DIREITA = 1
    HORIZONTAL_ESQUERDA = 2
    VERTICAL_DESCENDO = 3
    VERTICAL_SUBINDO = 4
    DIAGONAL_ESQUERDA_CIMA_DIREITA_BAIXO = 5 # \
    DIAGONAL_ESQUERDA_BAIXO_DIREITA_CIMA = 6 # /
    DIAGONAL_DIREITA_CIMA_ESQUERDA_BAIXO = 7 # /
    DIAGONAL_DIREITA_BAIXO_ESQUERDA_CIMA = 8 # \

class Sequence:
    def __init__(self, string, start:(int, int), shape:LS):
        self.string = string
        self.start = start
        self.shape = shape
    def __hash__(self):
        return hash((self.string, self.start))
    def __eq__(self, other):
        return self.string == other.string and self.start == other.start

class GameLogic:
    def __init__(self, grid_size=15, win_condition=5):
        self.grid_size = grid_size
        self.matrix = np.full((grid_size+6, grid_size+6), -1)
        self.win_condition = win_condition
        self.dicionario_direcoes = {
            LS.HORIZONTAL_DIREITA: (1, 0),
            LS.HORIZONTAL_ESQUERDA: (-1, 0),
            LS.VERTICAL_DESCENDO: (0, 1),
            LS.VERTICAL_SUBINDO: (0, -1),
            LS.DIAGONAL_ESQUERDA_CIMA_DIREITA_BAIXO: (1, 1),  # \
            LS.DIAGONAL_ESQUERDA_BAIXO_DIREITA_CIMA: (1, -1),  # /
            LS.DIAGONAL_DIREITA_CIMA_ESQUERDA_BAIXO: (-1, 1),  # /
            LS.DIAGONAL_DIREITA_BAIXO_ESQUERDA_CIMA: (-1, -1),  # \
        }
    def check_win(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.matrix[i, j] == -1: continue
                for color in range(2):
                    # Horizontal:
                    if all(self.matrix[i][j + k] == color for k in range(5)):
                        return color
                    # Vertical
                    if all(self.matrix[i + k][j] == color for k in range(5)):
                        return color
                    # Diagonal 1º caso:
                    if all(self.matrix[i + k][j + k] == color for k in range(5)):
                        return color
                    # Diagonal 2º caso:
                    if all(self.matrix[i - k][j + k] == color for k in range(5)):
                        return color
        return -1

    def make_move(self, white:int, x:int, y:int):
        self.matrix[x, y] = white