import numpy as np
from game_logic import GameLogic

class Sequence:
    def __init__(self, string, start:(int, int), end:(int, int)):
        self.string = string
        self.start = start
        self.end = end
        self.seq_type = None
    def __hash__(self):
        return hash((self.string, self.start, self.end))
    def __eq__(self, other):
        return self.string == other.string and self.start == other.start and self.end == other.end

class QLearning:
    def __init__(self, game_logic:GameLogic):
        self.game_logic = game_logic
        self.q_table = np.zeros((3^6, 6), dtype=np.float32) # [729][6]
        # TODO: pôr detecção de double threat
        # TODO: agora só falta fazer jogar onde tiver '-' e pôr o treinamento.

    def get_symbol(self, val):
        if val == 0: return "0"
        if val == 1: return "1"
        return "-"

    # Retorna sequência
    # É o seguinte .. tabuleiro 15x15 com 6 caracteres
    def detect_threats(self):
        grid_size = self.game_logic.grid_size
        sequences = set()
        for i in range(grid_size):
            for j in range(grid_size):
                # if self.matrix[i, j] == -1: continue
                # Horizontal direita:
                if j <= grid_size - 6:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i][j + k]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), (i, j + 6)))
                # Horizontal esquerda:
                if j >= 4:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i][j - k]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), (i, j - 6)))
                # Vertical descendo:
                if i <= grid_size - 6:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i + k][j]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), (i + 6, j)))
                # Vertical subindo:
                if i >= 4:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i - k][j]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), (i - 6, j)))
                # Diagonal 1º caso:
                if i <= grid_size - 6 and j <= grid_size - 6:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i + k][j + k]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), (i + 6, j + 6)))
                # Diagonal 2º caso:
                if i >= 4 and j <= grid_size - 6:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i - k][j + k]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), (i - 6, j + 6)))
                # Diagonal 3º caso:
                if i <= grid_size - 6 and j >= 4:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i + k][j - k]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), (i + 6, j - 6)))
                # Diagonal 4º caso:
                if i >= 4 and j >= 4:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i - k][j - k]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), (i - 6, j - 6)))
        # https://github.com/bluemapleman/Reinforcement-Learning-FiveInARow/blob/09a17f4db2c0600d73115360a187e3ed09859f65/AIPlayer.py#L25
        must = ['11-11', '111-1', '1-111', '1111-', '-1111']  # vitória
        loss = ['00-00', '000-0', '0-000', '0000-', '-0000']  # derrota
        caution = ['-1000-', '-0001-', '-0010-', '-0100-']  # perigo
        useful = ['-110-', '-011-', '11100', '00111', '11-01', '10-11', '-101-', '-1001-']  # oportunidade
        step_in = None
        for seq in sequences:
            for pattern in must:
                if pattern in seq.string:
                    step_in = seq
                    step_in.seq_type = "must"
                    break
            for pattern in loss:
                if pattern in seq.string:
                    step_in = seq
                    step_in.seq_type = "loss"
                    break
            for pattern in caution:
                if pattern in seq.string:
                    step_in = seq
                    step_in.seq_type = "caution"
                    break
            for pattern in useful:
                if pattern in seq.string:
                    step_in = seq
                    step_in.seq_type = "useful"
                    break
        return step_in