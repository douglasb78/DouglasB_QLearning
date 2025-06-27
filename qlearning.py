import random
from enum import Enum

import numpy as np
from game_logic import GameLogic


class LS(Enum):
    HORIZONTAL_DIREITA = 1
    HORIZONTAL_ESQUERDA = 2
    VERTICAL_DESCENDO = 3
    VERTICAL_SUBINDO = 4
    DIAGONAL_ESQUERDA_CIMA_DIREITA_BAIXO = 5  # \
    DIAGONAL_ESQUERDA_BAIXO_DIREITA_CIMA = 6  # /
    DIAGONAL_DIREITA_CIMA_ESQUERDA_BAIXO = 7  # /
    DIAGONAL_DIREITA_BAIXO_ESQUERDA_CIMA = 8  # \


class Sequence:
    def __init__(self, string, start: (int, int), end: (int, int), shape: LS):
        self.shape = shape
        self.string = string
        self.start = start
        self.end = end
        self.seq_type = None
        self.seq_shape = None

    def __hash__(self):
        return hash((self.string, self.start, self.end))

    def __eq__(self, other):
        return self.string == other.string and self.start == other.start and self.end == other.end


class QLearning:
    def __init__(self, game_logic: GameLogic):
        self.game_logic = game_logic
        self.q_table = np.zeros((3 ^ 6, 6), dtype=np.float32)  # [729][6]
        self.last_move = [-1, -1]
        self.last_goal = None
        self.last_path = []
        # TODO: agora só falta fazer jogar onde tiver '-' e pôr o treinamento.

    def get_symbol(self, val):
        if val == 0: return "0"
        if val == 1: return "1"
        return "-"

    # todo: editar para escolher o tipo de fileira para checar, fazer escolher o tipo de fileira em outra função
    def check_space_for_row(self, i: int, j: int):
        seq = ''
        shape = None
        posicoes = []
        # Horizontal Direita
        if j <= self.game_logic.grid_size - 6 and False:
            seq = ''.join(self.get_symbol(self.game_logic.matrix[i][j + k]) for k in range(6))
            if seq == '------':
                shape = LS.HORIZONTAL_DIREITA
            else:
                seq = ''
        # Horizontal Esquerda
        if j >= 5 and not shape and False:
            seq = ''.join(self.get_symbol(self.game_logic.matrix[i][j - k]) for k in range(6))
            if seq == '------':
                shape = LS.HORIZONTAL_ESQUERDA
            else:
                seq = ''
        # Vertical descendo:
        if i <= self.game_logic.grid_size - 6 and not shape and False:
            seq = ''.join(self.get_symbol(self.game_logic.matrix[i + k][j]) for k in range(6))
            if seq == '------':
                shape = LS.VERTICAL_DESCENDO
            else:
                seq = ''
        # Vertical subindo:
        if i >= 5 and not shape and False:
            seq = ''.join(self.get_symbol(self.game_logic.matrix[i - k][j]) for k in range(6))
            if seq == '------':
                shape = LS.VERTICAL_SUBINDO
            else:
                seq = ''
        # Diagonal Esquerda cima, Direita baixo:
        if i <= self.game_logic.grid_size - 6 and j <= self.game_logic.grid_size - 6 and not shape:
            seq = ''.join(self.get_symbol(self.game_logic.matrix[i + k][j + k]) for k in range(6))
            if seq == '------':
                shape = LS.DIAGONAL_ESQUERDA_CIMA_DIREITA_BAIXO
            else:
                seq = ''
        # Diagonal Esquerda baixo, Direita cima:
        if i >= 5 and j <= self.game_logic.grid_size - 6 and not shape:
            seq = ''.join(self.get_symbol(self.game_logic.matrix[i - k][j + k]) for k in range(6))
            if seq == '------':
                shape = LS.DIAGONAL_ESQUERDA_BAIXO_DIREITA_CIMA
            else:
                seq = ''
        # Diagonal Direita cima, Esquerda baixo:
        if i <= self.game_logic.grid_size - 5 and j >= 5 and not shape:
            seq = ''.join(self.get_symbol(self.game_logic.matrix[i + k][j - k]) for k in range(6))
            if seq == '------':
                shape = LS.DIAGONAL_DIREITA_CIMA_ESQUERDA_BAIXO
            else:
                seq = ''
        # Diagonal 4º caso:
        if i >= 5 and j >= 5 and not shape:
            seq = ''.join(self.get_symbol(self.game_logic.matrix[i - k][j - k]) for k in range(6))
            if seq == '------':
                shape = LS.DIAGONAL_DIREITA_BAIXO_ESQUERDA_CIMA
            else:
                seq = ''
        # Empate
        if not shape:
            return []
        # .. Senão retornar o caminho:
        for k in range(5):
            print(posicoes)
            if shape == LS.HORIZONTAL_DIREITA:
                posicoes.append([i, j + k])
            elif shape == LS.HORIZONTAL_ESQUERDA:
                posicoes.append(posicoes.append([i, j - k]))
            elif shape == LS.VERTICAL_DESCENDO:
                posicoes.append([i + k, j])
            elif shape == LS.VERTICAL_SUBINDO:
                posicoes.append([i - k, j])
            elif shape == LS.DIAGONAL_ESQUERDA_CIMA_DIREITA_BAIXO:
                posicoes.append([i + k, j + k])
            elif shape == LS.DIAGONAL_ESQUERDA_BAIXO_DIREITA_CIMA:
                posicoes.append([i - k, j + k])
            elif shape == LS.DIAGONAL_DIREITA_CIMA_ESQUERDA_BAIXO:
                posicoes.append([i + k, j - k])
            elif shape == LS.DIAGONAL_DIREITA_BAIXO_ESQUERDA_CIMA:
                posicoes.append([i - k, j - k])
        return posicoes

    def find_empty_place(self):
        linha_disponivel = None
        attempts = 0
        while not linha_disponivel:
            start_i = random.randint(0, self.game_logic.grid_size)
            start_j = random.randint(0, self.game_logic.grid_size)
            for i in range(start_i, self.game_logic.grid_size):
                for j in range(start_j, self.game_logic.grid_size):
                    linha_disponivel = self.check_space_for_row(i, j)
                    if linha_disponivel:
                        return linha_disponivel
                    else:
                        attempts += 1
            if attempts >= 225:
                return None

    def play_move(self, threat: Sequence, game_logic: GameLogic):
        if not threat:
            if not self.last_goal:
                self.last_goal = random.choice(list(LS))  # todo: implementar isso, senão prioriza horizontal_direita
            if not self.last_path:
                self.last_path = self.find_empty_place()
            if self.last_path:
                print(self.last_path, len(self.last_path))
                if self.get_symbol(self.game_logic.matrix[self.last_path[0][0]][self.last_path[0][1]]) != '-':
                    self.last_path = None
                    self.last_goal = None
                else:
                    self.game_logic.matrix[self.last_path[0][0]][self.last_path[0][1]] = 1
                    self.last_path.remove(self.last_path[0])
        # Se há uma ameaça:
        elif threat:
            posicoes, seq_string = self.get_sequence(threat)
            posicoes_validas = []
            for i in range(6):
                if seq_string[i] == '-' and posicoes[i][0] < 15 and posicoes[i][1] < 15:
                    print(posicoes[i], seq_string[i])
                    posicoes_validas.append(posicoes[i])
            if posicoes_validas:
                random_position = random.randint(0, len(posicoes_validas) - 1)
                print(random_position, posicoes_validas[random_position])
                x, y = posicoes_validas[random_position]
                self.game_logic.matrix[x][y] = 1
                self.last_move = posicoes_validas[random_position]
            else:
                pass

    def get_sequence(self, threat: Sequence):
        posicoes = []
        seq = ""
        for k in range(6):
            # encontrar maneira de melhorar esse código tá muito bagunçado:
            if threat.shape == LS.HORIZONTAL_DIREITA:
                posicoes.append((threat.start[0], threat.start[1] + k))
                seq += self.get_symbol(self.game_logic.matrix[threat.start[0]][threat.start[1] + k])
            elif threat.shape == LS.HORIZONTAL_ESQUERDA:
                posicoes.append((threat.start[0], threat.start[1] - k))
                seq += self.get_symbol(self.game_logic.matrix[threat.start[0]][threat.start[1] - k])
            elif threat.shape == LS.VERTICAL_DESCENDO:
                posicoes.append((threat.start[0] + k, threat.start[1]))
                seq += self.get_symbol(self.game_logic.matrix[threat.start[0] + k][threat.start[1]])
            elif threat.shape == LS.VERTICAL_SUBINDO:
                posicoes.append((threat.start[0] - k, threat.start[1]))
                seq += self.get_symbol(self.game_logic.matrix[threat.start[0] - k][threat.start[1]])
            elif threat.shape == LS.DIAGONAL_ESQUERDA_CIMA_DIREITA_BAIXO:
                posicoes.append((threat.start[0] + k, threat.start[1] + k))
                seq += self.get_symbol(self.game_logic.matrix[threat.start[0] + k][threat.start[1] + k])
            elif threat.shape == LS.DIAGONAL_ESQUERDA_BAIXO_DIREITA_CIMA:  # ----
                posicoes.append((threat.start[0] - k, threat.start[1] + k))
                seq += self.get_symbol(self.game_logic.matrix[threat.start[0] - k][threat.start[1] + k])
            elif threat.shape == LS.DIAGONAL_DIREITA_CIMA_ESQUERDA_BAIXO:
                posicoes.append((threat.start[0] + k, threat.start[1] - k))
                seq += self.get_symbol(self.game_logic.matrix[threat.start[0] + k][threat.start[1] - k])
            elif threat.shape == LS.DIAGONAL_DIREITA_BAIXO_ESQUERDA_CIMA:  # ----
                posicoes.append((threat.start[0] - k, threat.start[1] - k))
                seq += self.get_symbol(self.game_logic.matrix[threat.start[0] - k][threat.start[1] - k])
        return posicoes, seq

    # Retorna sequência
    # .. isso é para treinar o Q-Learning, se o modelo acabou com uma "ameaça", ganha pontos.
    # .. se uma ameaça é gerada depois de uma jogada, perde pontos.
    def detect_threats(self):
        grid_size = self.game_logic.grid_size
        sequences = set()
        for i in range(grid_size):
            for j in range(grid_size):
                # if self.matrix[i, j] == -1: continue
                # Horizontal direita:
                if j <= grid_size - 6:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i][j + k]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), (i, j + 6), LS.HORIZONTAL_DIREITA))
                # Horizontal esquerda:
                if j >= 5:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i][j - k]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), (i, j - 6), LS.HORIZONTAL_ESQUERDA))
                # Vertical descendo:
                if i <= grid_size - 6:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i + k][j]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), (i + 6, j), LS.VERTICAL_DESCENDO))
                # Vertical subindo:
                if i >= 5:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i - k][j]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), (i - 6, j), LS.VERTICAL_SUBINDO))
                # Diagonal 1º caso:
                if i <= grid_size - 6 and j <= grid_size - 6:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i + k][j + k]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), (i + 6, j + 6), LS.DIAGONAL_ESQUERDA_CIMA_DIREITA_BAIXO))
                # Diagonal 2º caso:
                if i >= 5 and j <= grid_size - 6:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i - k][j + k]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), (i - 6, j + 6), LS.DIAGONAL_ESQUERDA_BAIXO_DIREITA_CIMA))
                # Diagonal 3º caso:
                if i <= grid_size - 5 and j >= 5:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i + k][j - k]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), (i + 6, j - 6), LS.DIAGONAL_DIREITA_CIMA_ESQUERDA_BAIXO))
                # Diagonal 4º caso:
                if i >= 5 and j >= 5:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i - k][j - k]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), (i - 6, j - 6), LS.DIAGONAL_DIREITA_BAIXO_ESQUERDA_CIMA))
        must = ['11-11', '111-1', '1-111', '1111-', '-1111']  # vitória
        loss = ['00-00', '000-0', '0-000', '0000-', '-0000']  # derrota
        caution = ['11000-', '01000-', '-1000-', '-00011', '-00010', '-0001-', '-00101', '-00100', '-0010-', '10100-',
                   '00100-', '-0100-', '-000-0', '-000-1', '-000--', '1-000-', '0-000-', '--000-']  # perigo
        step_in = None
        for seq in sequences:
            for pattern in must:
                if pattern in seq.string:
                    step_in = seq
                    step_in.seq_type = "must"
            for pattern in loss:
                if pattern in seq.string:
                    step_in = seq
                    step_in.seq_type = "loss"
            for pattern in caution:
                if pattern in seq.string:
                    step_in = seq
                    step_in.seq_type = "caution"
        return step_in
