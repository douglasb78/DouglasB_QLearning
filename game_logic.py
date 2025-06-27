import numpy as np


class GameLogic:
    def __init__(self, grid_size=15, win_condition=5):
        self.grid_size = grid_size
        self.matrix = np.full((grid_size + 6, grid_size + 6), -1)
        self.win_condition = win_condition

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

    def make_move(self, white: int, x: int, y: int):
        self.matrix[y, x] = white
