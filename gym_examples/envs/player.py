import pygame
import math
import numpy as np
import random

class Player:
    def __init__(self, window_width, window_height, color, max_radius=10, max_speed=10, action_space=4, randomize_radius=False, randomize_speed=False, normalize=True):
        self.window_width = window_width
        self.window_height = window_height
        self.game_width = 1 if normalize else window_width
        self.game_height = 1 if normalize else window_height
        self.normalize = normalize
        self.initx = self.game_width / 2
        self.inity = self.game_height / 2
        self.x = self.initx
        self.y = self.inity
        self.color = color
        self.randomize_speed = randomize_speed
        self.randomize_radius = randomize_radius
        self.max_radius = max_radius
        self.max_speed = max_speed
        self.radius = random.uniform(1, max_radius) if randomize_radius else max_radius
        self.speed = random.uniform(1, max_speed) if randomize_speed else max_speed
        self.last_locations = []
        self.pos = np.array((self.x, self.y))
        self.action_space = action_space

    def draw(self, window):
        if self.normalize:
            x, y, r = self.x * self.window_width, self.y * self.window_height, self.radius * self.window_width
        else:
            x, y, r = self.x, self.y, self.radius
        # print('player', self.x, self.y, self.radius, x, y, r)
        # print('player', self.color, (x, y), r)
        pygame.draw.circle(window, self.color, (x, y), r)
        
    def aiMove(self, move):
        if isinstance(move, np.int64) or isinstance(move, int) or isinstance(move, np.ndarray):
            if self.action_space == 4:
                if move == 0:
                    self.x -= self.speed
                elif move == 1:
                    self.x += self.speed
                elif move == 2:
                    self.y -= self.speed
                else:
                    self.y += self.speed
            elif self.action_space == 5:
                if move == 0:
                    return 
                elif move == 1:
                    self.x -= self.speed
                elif move == 2:
                    self.x += self.speed
                elif move == 3:
                    self.y -= self.speed
                else:
                    self.y += self.speed
                        
        elif isinstance(move, tuple):
            self.x += move[0] * self.speed
            self.y += move[1] * self.speed
            
        self.pos[0] = self.x
        self.pos[1] = self.y
            
        # if len(self.last_locations) > 20:
        #     self.last_locations.pop(0)
        # self.last_locations.append((self.x, self.y))
        # print(move, self.speed, self.x, self.y, self.pos)

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        if keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.y += self.speed

    def is_colliding_with(self, other):
        distance = ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
        return distance < self.radius + other.radius
    
    def touch_wall(self):
        if self.x < self.radius:
            return True
        if self.x > self.game_width - self.radius:
            return True
        if self.y < self.radius:
            return True
        if self.y > self.game_height - self.radius:
            return True

    def reset(self):
        self.x = self.initx
        self.y = self.inity
        
        if self.randomize_radius:
            self.radius = random.uniform(0.01, self.max_radius)
        
        if self.randomize_speed:
            self.radius = random.uniform(0.005, self.max_radius)
        
    def getState(self, radius=False, speed=False):
        state = (self.x, self.y)
        
        if radius:
            state += (self.radius,)

        if speed:
            state += (self.speed,)
            
        return state
    
    def getWalls(self):
        return (self.x - self.radius, self.game_width - self.radius - self.x, self.y - self.radius, self.game_height - self.radius - self.y)
    
