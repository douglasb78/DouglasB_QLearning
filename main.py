import pygame

from labyrinth import Labyrinth
from qlearning import QLearningAgent


def main():
    # Criar tela do jogo:
    pygame.init()
    pygame.display.set_caption("Labirinto QLearning")
    # Criar labirinto:
    matrix = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 2, 1],
        [1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
        [1, 2, 0, 2, 0, 0, 0, 2, 0, 2, 2, 0, 0, 1],
        [1, 0, 2, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1],
        [1, 1, 1, 1, 1, 0, 0, 2, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 0, 0, 2, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    labyrinth = Labyrinth(14, 12, matrix)
    # Definir tamanho da tela do jogo:
    largura_px = labyrinth.width * labyrinth.cell_size
    altura_px = labyrinth.height * labyrinth.cell_size
    game_screen = pygame.display.set_mode((largura_px, altura_px))
    # Temporizador, de velocidade:
    clock = pygame.time.Clock()
    game_speed = 20
    skip_amount = 1000
    # Criar agente do Q-Learning:
    character = QLearningAgent(labyrinth, (5, 10), (12, 5), game_speed)

    # Só rodar a cada 'step' simulações, para agilizar o processo:
    for sim in range(5000):
        if not sim % skip_amount:
            character.run_simulation(True, game_screen, clock)
            print(f"Rodando etapa {sim}...")
        else:
            character.run_simulation(False, game_screen, clock)

    # Caminho final:
    best_path = character.find_best_path()
    print(f"Melhor caminho encontrado:\n {best_path}")

    while True:
        pygame.event.get()
        for step in best_path:
            pos = step
            if not step == best_path[-1]:
                labyrinth.draw_labyrinth(game_screen, pos, q_table=character.get_q_table())
            else:
                labyrinth.draw_labyrinth(game_screen, pos, best_path, character.get_q_table(), True)
        pygame.display.flip()
        clock.tick(game_speed)

if __name__ == "__main__":
    main()
