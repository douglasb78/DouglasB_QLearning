import random
import pygame
from enum import Enum


class Move(Enum):
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    UP = (0, -1)
    DOWN = (0, 1)

class QLearningAgent:
    def __init__(self, labyrinth, starting_pos, goal_pos, game_speed):
        self.labyrinth = labyrinth
        self.width, self.height = labyrinth.get_labyrinth_size()
        self.character_position = starting_pos
        self.goal_position = goal_pos
        self.starting_pos = starting_pos
        self.game_speed = game_speed
        self.moves = list(Move)

        self.q_table = []
        for col in range(self.width):
            matrix_2d = []
            for row in range(self.height):
                action_list = []
                for action in self.moves:
                    action_list.append(0.0)
                matrix_2d.append(action_list)
            self.q_table.append(matrix_2d)


    def obtain_reward(self, pos):
        row, col = pos
        cell = self.labyrinth.get_matrix()[col][row]
        if pos == self.goal_position: return 200
        if cell == 2: return -200
        else: return -1

    def get_q_table(self):
        return self.q_table

    def get_list_of_actions(self, position):
        list_of_actions = []
        for action in range(4):
            offset_row, offset_col = self.moves[action].value
            new_position = (position[0] + offset_row, position[1] + offset_col)
            if self.labyrinth.is_movement_valid(new_position):
                list_of_actions.append(action)
        return list_of_actions

    def choose_move(self, position):
        valid_actions = self.get_list_of_actions(position)
        if not valid_actions:
            return None

        if random.random() < 0.3:
            return random.choice(valid_actions)

        q_values = []
        row, col = position
        for action in valid_actions:
            value = self.q_table[row][col][action]
            q_values.append(value)

        valid_actions = valid_actions[q_values.index(max(q_values))]
        return valid_actions

    def update_q_table(self, previous_position, action, reward, next_position):
        if action is None:
            return
        row_prev, col_prev = previous_position
        row_next, col_next = next_position
        current_value = self.q_table[row_prev][col_prev][action]
        next_value = max(self.q_table[row_next][col_next])
        self.q_table[row_prev][col_prev][action] = current_value + 0.7 * (reward + 0.8 * next_value - current_value)

    def run_simulation(self, display, game_screen, clock):
        self.character_position = self.starting_pos
        total_reward = 0

        while True:
            current_position = self.character_position
            selected_action = self.choose_move(current_position)

            if self.character_position == self.goal_position:
                break
            elif selected_action:
                offset_row, offset_col = self.moves[selected_action].value
                next_pos = (current_position[0] + offset_row, current_position[1] + offset_col)
                if self.labyrinth.is_movement_valid(next_pos):
                    self.character_position = next_pos

            reward = self.obtain_reward(self.character_position)
            total_reward += reward

            self.update_q_table(current_position, selected_action, reward, self.character_position)

            if display and game_screen:
                self.labyrinth.draw_labyrinth(game_screen, self.character_position, q_table=self.get_q_table())
                pygame.event.pump()
                pygame.display.flip()
                clock.tick(self.game_speed)
        return self.character_position == self.goal_position, total_reward

    def find_best_path(self):
        path = [self.starting_pos]
        pos = self.starting_pos
        for step in range(100):
            if pos == self.goal_position:
                break
            list_of_actions = self.get_list_of_actions(pos)
            q_values = []
            for action in list_of_actions:
                row, col = pos
                q = self.q_table[row][col][action]
                q_values.append(q)
            best = list_of_actions[q_values.index(max(q_values))]
            offset_row, offset_col = self.moves[best].value
            pos = (pos[0] + offset_row, pos[1] + offset_col)
            path.append(pos)
        return path
