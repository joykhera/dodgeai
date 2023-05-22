import pygame
import random
import numpy as np
import math

class Enemy:
    def __init__(self, window_width, window_height, color=(255, 0, 0), max_speed=5, max_radius=50, enemy_movement='aimed', randomize_radius=False, randomize_speed=False, normalize=True):
        self.window_width = window_width
        self.window_height = window_height
        self.game_width = 1 if normalize else window_width
        self.game_height = 1 if normalize else window_height
        self.normalize = normalize
        self.x = random.randint(0, self.game_width)
        self.y = random.randint(0, self.game_height)
        self.color = color
        self.randomize_speed = randomize_speed
        self.randomize_radius = randomize_radius
        self.max_radius = max_radius
        self.max_speed = max_speed
        self.radius = random.uniform(1, max_radius) if randomize_radius else max_radius
        self.speed = random.uniform(1, max_speed) if randomize_speed else max_speed
        self.direction = [random.randint(5, 85), random.randint(95, 175), random.randint(185, 265), random.randint(275, 355)][random.randint(0, 3)]  # random.randint(0, 360)
        self.enemy_movement = enemy_movement
        self.reset()
        self.reached = False
        self.pos = np.array((self.x, self.y))

    def draw(self, window):
        if self.normalize:
            x, y, r = self.x * self.window_width, self.y * self.window_height, self.radius * self.window_width
        else:
            x, y, r = self.x, self.y, self.radius
            
        pygame.draw.circle(window, self.color, (x, y), r)

    def reset(self, playerCoords=None, normalize=False):
        # self.x = 0
        # self.y = 0
        side = random.randint(1, 4)
        if side == 1:  # top
            self.x = random.uniform(0, self.game_width)
            self.y = 0
        elif side == 2:  # right
            self.x = self.game_width
            self.y = random.uniform(0, self.game_height)
        elif side == 3:  # bottom
            self.x = random.uniform(0, self.game_width)
            self.y = self.game_height
        else:  # left
            self.x = 0
            self.y = random.uniform(0, self.game_height)
            
        if (self.enemy_movement == 'aimed' or self.enemy_movement == 'aimed_bounce') and playerCoords is not None:
                dist_to_target = math.sqrt((self.x - playerCoords[0]) ** 2 + (self.y - playerCoords[1]) ** 2)
                self.dx = self.speed * (playerCoords[0] - self.x) / dist_to_target
                self.dy = self.speed * (playerCoords[1] - self.y) / dist_to_target
        else:            
            self.direction = [random.randint(5, 85), random.randint(95, 175), random.randint(185, 265), random.randint(175, 355)][random.randint(0, 3)]  # random.randint(0, 360)
            self.dx = self.speed * math.cos(math.radians(self.direction))  # random.randint(-self.speed, self.speed)
            self.dy = self.speed * math.sin(math.radians(self.direction))  # random.randint(-self.speed, self.speed)
            
        if self.randomize_radius:
            self.radius = random.uniform(0.02, self.max_radius)

        if self.randomize_speed:
            self.speed = random.uniform(0.005, self.max_speed)
            

    def move(self, playerCoords=None):
        if self.enemy_movement == 'aimed' or self.enemy_movement == 'aimed_bounce':
            new_x = self.x + self.dx
            new_y = self.y + self.dy
            
            if new_x < 0 or new_y < 0 or new_x > self.game_width or new_y > self.game_height:
                self.reached = True
                if self.enemy_movement == 'aimed':
                    self.reset(playerCoords)
                elif self.enemy_movement == 'aimed_bounce':
                    dist_to_target = math.sqrt((self.x - playerCoords[0]) ** 2 + (self.y - playerCoords[1]) ** 2)
                    randomness = self.speed * 0.1
                    self.dx = self.speed * (playerCoords[0] - self.x) / dist_to_target + random.uniform(-randomness, randomness)
                    self.dy = self.speed * (playerCoords[1] - self.y) / dist_to_target + random.uniform(-randomness, randomness)
            else:
                if self.reached:
                    self.reached = False
                self.x = new_x
                self.y = new_y
                
        else:
            randomness = self.speed * 0.1
            # print(dx, dy, self.direction)
            new_x = self.x + self.dx
            new_y = self.y + self.dy

            if new_x < self.radius or new_x > self.game_width - self.radius:
                if new_x < self.radius:
                    self.x = self.radius
                else:
                    self.x = self.game_width - self.radius
                # self.direction = 180 - self.direction + random.uniform(0, 1)  # random.uniform(-1, 1)
                # self.dx *= -1
                self.dx *= -1 + random.uniform(-randomness, randomness)
            else:
                self.x = new_x

            if new_y < self.radius or new_y > self.game_height - self.radius:
                if new_y < self.radius:
                    self.y = self.radius
                else:
                    self.y = self.game_height - self.radius
                # self.direction = -self.direction + random.uniform(0, 1)  # random.uniform(-1, 1)
                # self.dy *= -1
                self.dy *= -1 + random.uniform(-randomness, randomness)
            else:
                self.y = new_y
                
        self.pos[0] = self.x
        self.pos[1] = self.y
        # print(self.pos, self.reached)

    def getState(self, player=None, direction=True, radius=False, speed=False):
        if player:
            state = (player.x - self.x, player.y - self.y)
        else:
            state = (self.x, self.y)
            
        if direction:
            # state += (self.direction,)
            state += (self.dx, self.dy)
        
        if radius:
            state += (self.radius,)
            
        if speed:
            state += (self.speed,)
            
        return state
