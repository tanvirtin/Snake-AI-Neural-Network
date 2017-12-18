from Player import Player
from Snake import Snake
import pygame
import random
from util import *
from collision_checker import *
from RLAgent import RLAgent
import sys

class RLAgentPlayer(Player):
    def __init__(self, screen, speed):
        super().__init__(screen)
        # takes in x, y of the snake and the speed of the snake
        self.agent = RLAgent(speed)
        self.go_through_boundary = True
        # total number of games required to train
        self.total_training_games = 10000
        # number of frames rendered to collect the data
        self.goal_steps = 2000
        for i in range(8):
            self.agent.body.grow()

    def consumption_check(self):
        if collision(self.agent.body, self.food_stack[0]):
            return True
        else:
            return False

    def display_info(self):
        pygame.font.init()

        default_font = pygame.font.get_default_font()
        font_renderer = pygame.font.Font(default_font, 10)

        # To create a surface containing `Some Text`
        label = font_renderer.render("Score - {}".format(self.agent.body.score), 1, (0,0,0)) # RGB Color
        self.screen.blit(label, (0,0))

        # draw the food
        for food in self.food_stack:
            food.draw(self.screen)

    def map_keys(self, pred):
        if self.agent.body.current_direction == "right":
            # left from current point of view
            if pred == -1:
                self.agent.body.change_direction("up")
            # right from current point of view
            elif pred == 1:
                self.agent.body.change_direction("down")

        elif self.agent.body.current_direction == "left":
            # left from current point of view
            if pred == -1:
                self.agent.body.change_direction("down")
            # right from current point of view
            elif pred == 1:
                self.agent.body.change_direction("up")

        elif self.agent.body.current_direction == "up":
            # left from current point of view
            if pred == -1:
                self.agent.body.change_direction("left")
            # right from current point of view
            elif pred == 1:
                self.agent.body.change_direction("right")

        elif self.agent.body.current_direction == "down":
            # left from current point of view
            if pred == -1:
                self.agent.body.change_direction("right")
            # right from current point of view
            elif pred == 1:
                self.agent.body.change_direction("left")


    def get_input_data(self, action):
        # all the prediction of the next frame's collision movements
        coll_pred = self.agent.body.self_collision_prediction()
        # get distance from the snake and food
        distance_from_food = self.agent.body.distance_from_food(self.food_stack[0])
        return [coll_pred[0], coll_pred[1], coll_pred[2], distance_from_food, action]


    def train_agent(self):
        training_data = []
        for i in range(self.total_training_games):
            prev_score = 0
            prev_food_distance = self.agent.body.distance_from_food(self.food_stack[0])
            for j in range(self.goal_steps):
                end, nn_data = self.render_training_frame()
                if end:
                    training_data.append([nn_data, -1])
                    # when game ends we reconstruct the body of the snake
                    self.agent.create_new_body()
                    break
                else:
                    food_distance = self.agent.body.distance_from_food(self.food_stack[0])
                    if self.agent.body.score > prev_score or food_distance < prev_food_distance:
                        training_data.append([nn_data, 1])
                    else:
                        training_data.append([nn_data, 0])
                    prev_food_distance = food_distance
        agent.learn(training_data)

    def render_training_frame(self):
        pygame.event.pump()

        self.screen.fill(self.background_color)

        self.display_info()

        for food in self.food_stack:
            food.draw(self.screen)

        action = random.randint(-1, 1)

        nn_data = self.get_input_data(action)

        self.map_keys(action)

        end = self.agent.body.draw(self.screen, self.go_through_boundary)

        # check here if the snake ate the food
        if self.consumption_check():
            self.spawn_food()
            # finally we grow the snake as well by adding a new segment to the snake's body
            self.agent.body.grow()

        pygame.display.flip()

        return end, nn_data



    def game_loop(self, key_input = None):
        pygame.event.pump()

        self.screen.fill(self.background_color)

        self.display_info()

        for food in self.food_stack:
            food.draw(self.screen)

        action = random.randint(-1, 1)

        nn_data = self.get_input_data(action)

        self.map_keys(action)

        print(nn_data)

        end = self.agent.body.draw(self.screen, self.go_through_boundary)

        # check here if the snake ate the food
        if self.consumption_check():

            self.spawn_food()

            # finally we grow the snake as well by adding a new segment to the snake's body
            self.agent.body.grow()

        pygame.display.flip()

        return end
