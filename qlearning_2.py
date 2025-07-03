import itertools
import random

import numpy as np

from game_logic import GameLogic, Sequence, LS

WIN_VALUE = 15.0
CAUTION_VALUE = -0.1
LOSS_VALUE = -1.0

class QLearningAlgo:
    def __init__(self, game_logic:GameLogic):
        self.game_logic = game_logic
        # Criar um array com todos os padrões de Five-In-A-Row:
        simbolos = ['1', '0', '-']
        padroes = [''.join(p) for p in itertools.product(simbolos, repeat=6)]
        # Criar um set, um conjunto, para diminuir o número de padrões:
        padroes_unicos = set()
        for p in padroes:
            padroes_unicos.add(p)
        del padroes, simbolos
        # Criar um dicionário:
        self.q_table = {}
        for p in padroes_unicos:
            # Se o espaço já é ocupado, o peso é -1.0
            self.q_table[p] = {i: 0.0 if c == '-' else -999999.0 for i, c in enumerate(p)}
        # Tabela criada.
        self.current_anchor_white = None
        self.current_anchor_black = None
        self.anchor_white_count = 0
        self.anchor_black_count = 0

    # Função de pegar o caractere da peça que está jogando:
    def get_symbol(self, val):
        if val == 0: return "0"
        if val == 1: return "1"
        return "-"
    # Função de inverter o caractere que está jogando:
    def get_opposite_symbol(self, val):
        return "1" if val == "0" else "0" if val == "1" else "-"
    # Função para pegar sequências:
    def get_sequences(self, game_logic:GameLogic):
        grid_size = game_logic.grid_size
        sequences = set()
        for i in range(grid_size):
            for j in range(grid_size):
                # Horizontal direita:
                if j <= grid_size - 6:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i][j + k]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), LS.HORIZONTAL_DIREITA))
                # Horizontal esquerda:
                if j >= 5:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i][j - k]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), LS.HORIZONTAL_ESQUERDA))
                # Vertical descendo:
                if i <= grid_size - 6:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i + k][j]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), LS.VERTICAL_DESCENDO))
                # Vertical subindo:
                if i >= 5:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i - k][j]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), LS.VERTICAL_SUBINDO))
                # Diagonal esquerda cima -> direita baixo:
                if i <= grid_size - 6 and j <= grid_size - 6:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i + k][j + k]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), LS.DIAGONAL_ESQUERDA_CIMA_DIREITA_BAIXO))
                # Diagonal esquerda baixo -> direita cima:
                if i >= 5 and j <= grid_size - 6:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i - k][j + k]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), LS.DIAGONAL_ESQUERDA_BAIXO_DIREITA_CIMA))
                # Diagonal direita cima -> esquerda baixo:
                if i <= grid_size - 5 and j >= 5:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i + k][j - k]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), LS.DIAGONAL_DIREITA_CIMA_ESQUERDA_BAIXO))
                # Diagonal direita baixo -> esquerda cima:
                if i >= 5 and j >= 5:
                    seq = ''.join(self.get_symbol(self.game_logic.matrix[i - k][j - k]) for k in range(6))
                    sequences.add(Sequence(seq, (i, j), LS.DIAGONAL_DIREITA_BAIXO_ESQUERDA_CIMA))
        return sequences

    # Função para "avaliar" a jogada:
    def analyze_play(self, last_sequence:Sequence, played_move:int, white:bool):
        plays_white = {
            "must": ['11-11', '111-1', '1-111', '1111-','-1111','1-11-1', '-1-111', '11-1-1', '1--111', '111--1', '1-1-11', '11--11',  '-111-1', '1-111-'],
            "loss": ['00-00', '000-0', '0-000', '0000-', '-0000', '0-00-0', '-0-000', '00-0-0', '0--000', '000--0','0-0-00', '00--00', '-000-0', '0-000-'],
            "caution": ['11000-', '01000-', '-1000-', '-00011', '-00010', '-0001-', '-00101', '-00100',
            '-0010-', '10100-''00100-', '-0100-', '-000-0', '-000-1', '-000--', '1-000-', '0-000-', '--000-']
        }
        plays_black = {
            "must": ['00-00', '000-0', '0-000', '0000-', '-0000', '0-00-0', '-0-000', '00-0-0', '0--000', '000--0','0-0-00', '00--00', '-000-0', '0-000-'],
            "loss": ['11-11', '111-1', '1-111', '1111-','-1111','1-11-1', '-1-111', '11-1-1', '1--111', '111--1', '1-1-11', '11--11',  '-111-1', '1-111-'],
            "caution": ['00111-', '10111-', '-0111-', '-11100', '-11101', '-1110-', '-11010', '-11011',
            '-1101-', '01011-''11011-', '-1011-', '-111-1', '-111-0', '-111--', '0-111-', '1-111-', '--111-']
        }
        score = 0.0
        plays = plays_white if white else plays_black
        sequences = self.get_sequences(self.game_logic)
        for sequence in sequences:
            if sequence.string in plays["must"]: score += WIN_VALUE
            elif sequence.string in plays["loss"]: score += LOSS_VALUE
            elif sequence.string in plays["caution"]: score += CAUTION_VALUE
        #print(score)
        self.q_table[last_sequence.string][played_move] += score

    def is_board_full(self):
        for i in range(15):
            for j in range(15):
                if self.game_logic.matrix[i][j] == -1:
                    return False
        return True

    def find_best_direction(self, x: int, y: int, white: bool):
        max_count = -1
        chosen_direction = None
        for direction in LS:
            dx, dy = self.game_logic.dicionario_direcoes[direction]
            count = 0
            for i in range(6):
                nx = x + dy * i
                ny = y + dx * i
                if 0 <= nx < 15 and 0 <= ny < 15:
                    if self.game_logic.matrix[nx][ny] == white:
                        count += 1
                    else:
                        break
                else:
                    break
            if count > max_count:
                max_count = count
                chosen_direction = direction
        if max_count <= 0:
            chosen_direction = random.choice(list(LS))
        return (chosen_direction, max_count)

    # Função para tentar criar uma fileira, se não existir ameaça:
    def attempt_to_fill_row(self, sequence: Sequence, white: bool):
        direction, _ = self.find_best_direction(sequence.start[0], sequence.start[1], white)
        dx, dy = self.game_logic.dicionario_direcoes[direction]
        anchor_count = self.anchor_white_count if white else self.anchor_black_count
        x = sequence.start[0] + dy * anchor_count
        y = sequence.start[1] + dx * anchor_count

        if 0 <= x < 15 and 0 <= y < 15 and self.game_logic.matrix[x][y] == -1:
            self.game_logic.make_move(white, x, y)
            if white:
                if not self.current_anchor_white:
                    self.current_anchor_white = sequence
                self.anchor_white_count += 1
            else:
                if not self.current_anchor_black:
                    self.current_anchor_black = sequence
                self.anchor_black_count += 1
            return True

        if white:
            self.current_anchor_white = None
            self.anchor_white_count = 0
        else:
            self.current_anchor_black = None
            self.anchor_black_count = 0
        return False

    # Função para achar sequências de 3 ou mais do símbolo oposto:
    def find_row_to_place_move_agaisnt(self, white:bool):
        count_4 = set()
        count_3 = set()
        count_2 = set()
        count_1 = set()
        count_free = set()
        sequences = self.get_sequences(self.game_logic)
        for sequence in sequences:
            if sequence.string.count('-') >= 1:
                if sequence.string.count(self.get_opposite_symbol(self.get_symbol(white))) >= 4:
                    count_4.add(sequence)
                elif sequence.string.count(self.get_opposite_symbol(self.get_symbol(white))) >= 3:
                    count_3.add(sequence)
                elif sequence.string.count(self.get_opposite_symbol(self.get_symbol(white))) >= 2:
                    count_2.add(sequence)
                elif sequence.string.count(self.get_opposite_symbol(self.get_symbol(white))) >= 1:
                    count_1.add(sequence)
                else:
                    count_free.add(sequence)
        # retornar sequência aleatória que tiver 4 em linha do outro jogador
        # .. se não tiver, retornar sequência aleatória que tiver 3
        # .. se não tiver, retornar a sequência aleatória que estiver mais livre
        if count_4: return (random.choice(tuple(count_4)), True)
        if count_3: return (random.choice(tuple(count_3)), True)
        if count_free: return (random.choice(tuple(count_free)), False)
        if count_1: return (random.choice(tuple(count_1)), False)
        if count_2: return (random.choice(tuple(count_2)), False)
        return None
    def place_move_agaist_sequence(self, sequence:Sequence, white:bool):
        indices_livres = [i for i, c in enumerate(sequence.string) if c == '-']
        candidatos = []
        for i in indices_livres:
            score = self.q_table[sequence.string][i]
            candidatos.append((score, i))
        candidatos.sort(reverse=True, key=lambda t: t[0])
        if random.randint(0, 100) > 30:
            escolhido = candidatos[0][1]
        else:
            escolhido = random.choice(indices_livres)
        dx, dy = self.game_logic.dicionario_direcoes[sequence.shape]
        x, y = sequence.start
        #print(indices_livres, (x+dy*escolhido, y+dx*escolhido), escolhido)
        self.game_logic.make_move(white, x+dy*escolhido, y+dx*escolhido)
        self.analyze_play(sequence, escolhido, white)


QLearningAlgo(GameLogic())
