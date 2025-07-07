import pygame

class Labyrinth:
    def __init__(self, width, height, matrix):
        self.cell_size = 48
        self.width = width
        self.height = height
        self.matrix = matrix

    def get_matrix(self):
        return self.matrix

    def get_labyrinth_size(self):
        return self.width, self.height

    def find_center(self, row, col):
        x = row * self.cell_size + self.cell_size // 2
        y = col * self.cell_size + self.cell_size // 2
        return (x, y)

    def draw_labyrinth(self, tela: pygame.Surface, character_position, best_path=None, q_table=None, last=False):
        tela.fill((238, 238, 238))
        fonte = pygame.font.SysFont("Arial", 8)
        # Bordas, obstáculos e destino final:
        for col in range(self.height):
            for row in range(self.width):
                cell_rect = pygame.Rect(row * self.cell_size, col * self.cell_size, self.cell_size, self.cell_size)
                match self.matrix[col][row]:
                    case 1:
                        pygame.draw.rect(tela, "black", cell_rect)
                    case 2:
                        pygame.draw.circle(tela, "blue", self.find_center(row, col), self.cell_size * 0.3 / 2)
                    case 3:
                        pygame.draw.circle(tela, "green", self.find_center(row, col), self.cell_size * 0.3 / 2)
                # Desenhar texto:
                if q_table:
                    deslocamento = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                    for i in range(4):
                        valor = f"{q_table[row][col][i]:.1f}"
                        texto = fonte.render(valor, True, (0, 0, 0))
                        center = self.find_center(row, col)
                        new_center = (center[0] + 16.0 * deslocamento[i][0], center[1] + 16.0 * deslocamento[i][1])
                        text_rect = texto.get_rect(center=new_center)
                        tela.blit(texto, text_rect)
        # Personagem:
        if character_position:
            row, col = character_position
            pygame.draw.circle(tela, "black", self.find_center(row, col), self.cell_size * 0.3 / 2)
        # Linhas da grade:
        for i in range(16):
            pygame.draw.line(tela, "black", (0, i * self.cell_size), (16 * self.cell_size, i * self.cell_size))
        for j in range(16):
            pygame.draw.line(tela, "black", (j * self.cell_size, 0), (j * self.cell_size, 16 * self.cell_size))
        # Caminho final:
        if last and best_path:
            for node in best_path:
                pygame.draw.circle(tela, "yellow", self.find_center(node[0], node[1]), self.cell_size * 0.3 / 2)

    def is_movement_valid(self, position):
        row, col = position
        if 0 <= col < self.height and 0 <= row < self.width:
            return self.matrix[col][row] != 1
        return False
