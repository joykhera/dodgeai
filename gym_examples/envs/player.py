import pygame
import math
import numpy as np
import random

class Player:
    def __init__(self, window_width, window_height, color, max_radius=10, max_speed=10, random_radius=False, random_speed=False):
        self.initx = window_width // 2
        self.inity = window_height // 2
        self.x = self.initx
        self.y = self.inity
        self.color = color
        self.random_speed = random_speed
        self.random_radius = random_radius
        self.max_radius = max_radius
        self.max_speed = max_speed
        self.radius = random.randint(1, max_radius) if random_radius else max_radius
        self.speed = random.randint(1, max_speed) if random_speed else max_speed
        self.window_width = window_width
        self.window_height = window_height
        self.last_locations = []

    def draw(self, window):
        pygame.draw.circle(window, self.color, (self.x, self.y), self.radius)
        
    def aiMove(self, move):
        if isinstance(move, np.int64):
            if move == 0:
                self.x -= self.speed
            elif move == 1:
                self.x += self.speed
            elif move == 2:
                self.y -= self.speed
            else:
                self.y += self.speed
        
        elif isinstance(move, tuple):
            self.x += move[0] * self.speed
            self.y += move[1] * self.speed
            
        if len(self.last_locations) > 20:
            self.last_locations.pop(0)
        self.last_locations.append((self.x, self.y))

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
        # print((self.x - self.radius), (self.window_width - self.radius - self.x), (self.y - self.radius), (self.window_height - self.radius - self.y))
        if self.x < self.radius:
            return True
        if self.x > self.window_width - self.radius:
            return True
        if self.y < self.radius:
            return True
        if self.y > self.window_height - self.radius:
            return True

    def reset(self):
        self.x = self.initx
        self.y = self.inity
        
        if self.random_radius:
            self.radius = random.randint(1, self.max_radius)
        
        if self.random_speed:
            self.radius = random.randint(1, self.max_radius)
        
    def getState(self, radius=False, speed=False):
        state = (self.x, self.y)
        
        if radius:
            state += (self.radius,)

        if speed:
            state += (self.speed,)
            
        return state
    
    def getWalls(self):
        return (self.x - self.radius, self.window_width - self.radius - self.x, self.y - self.radius, self.window_height - self.radius - self.y)
