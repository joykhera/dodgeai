import pygame
import random
import numpy as np
import math

# Define the Enemy class


class Enemy:
    def __init__(self, window_width, window_height, color=(255, 0, 0), max_speed=5, max_radius=50, enemy_movement='aimed', random_radius=False, random_speed=False, normalize=False):
        self.window_width = window_width
        self.window_height = window_height
        self.game_width = 1 if normalize else window_width
        self.game_height = 1 if normalize else window_height
        self.normalize = normalize
        self.x = random.randint(0, self.game_width)
        self.y = random.randint(0, self.game_height)
        self.color = color
        self.random_speed = random_speed
        self.random_radius = random_radius
        self.max_radius = max_radius
        self.max_speed = max_speed
        self.radius = random.randint(1, max_radius) if random_radius else max_radius
        self.speed = random.randint(1, max_speed) if random_speed else max_speed
        self.direction = [random.randint(5, 85), random.randint(95, 175), random.randint(185, 265), random.randint(175, 355)][random.randint(0, 3)]  # random.randint(0, 360)
        self.enemy_movement = enemy_movement
        self.reset()
        self.reached = False
        self.pos = np.array((self.x, self.y))

    def draw(self, window):
        if self.normalize:
            x, y, r = self.x * self.window_width, self.y * self.window_height, self.radius * self.window_width
        else:
            x, y, r = self.x, self.y, self.radius
        # print(window, self.color, (x, y), r)
        pygame.draw.circle(window, self.color, (x, y), r)

    def reset(self, playerCoords=None, normalize=False):
        if self.enemy_movement == 'aimed':
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

            if playerCoords is not None:
                dist_to_target = math.sqrt((self.x - playerCoords[0]) ** 2 + (self.y - playerCoords[1]) ** 2)
                self.dx = self.speed * (playerCoords[0] - self.x) / dist_to_target
                self.dy = self.speed * (playerCoords[1] - self.y) / dist_to_target
            else:
                self.dx = self.speed * math.cos(math.radians(self.direction))
                self.dy = self.speed * math.sin(math.radians(self.direction))
        else:
            while math.dist((self.x, self.y), (self.game_width / 2, self.game_height / 2)) < self.max_radius + self.game_height * 0.1:
                self.x = random.randint(0, self.game_width)
                self.y = random.randint(0, self.game_height)
            
            self.direction = [random.randint(5, 85), random.randint(95, 175), random.randint(185, 265), random.randint(175, 355)][random.randint(0, 3)]  # random.randint(0, 360)
            
            self.dx = self.speed * math.cos(math.radians(self.direction))  # random.randint(-self.speed, self.speed)
            self.dy = self.speed * math.sin(math.radians(self.direction))  # random.randint(-self.speed, self.speed)
            
        if self.random_radius:
            self.radius = random.randint(1, self.max_radius)

        if self.random_speed:
            self.speed = random.randint(1, self.max_speed)
        
        # print(self.pos, self.reached)
            

    def move(self, playerCoords=None):
        if self.enemy_movement == 'aimed':
            new_x = self.x + self.dx
            new_y = self.y + self.dy
            if new_x < 0 or new_y < 0 or new_x > self.game_width or new_y > self.game_height:
                self.reached = True
                self.reset(playerCoords)
            else:
                if self.reached:
                    self.reached = False
                self.x = new_x
                self.y = new_y
        else:
            # print(dx, dy, self.direction)
            new_x = self.x + self.dx
            new_y = self.y + self.dy

            if new_x < self.radius or new_x > self.game_width - self.radius:
                # If the new position would be outside the screen boundaries, move the enemy to just inside the boundary
                if new_x < self.radius:
                    self.x = self.radius
                else:
                    self.x = self.game_width - self.radius
                # Reverse the direction of movement
                self.direction = 180 - self.direction + random.uniform(0, 1)  # random.uniform(-1, 1)
            else:
                self.x = new_x

            if new_y < self.radius or new_y > self.game_height - self.radius:
                # If the new position would be outside the screen boundaries, move the enemy to just inside the boundary
                if new_y < self.radius:
                    self.y = self.radius
                else:
                    self.y = self.game_height - self.radius
                # Reverse the direction of movement
                self.direction = -self.direction + random.uniform(0, 1)  # random.uniform(-1, 1)
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
