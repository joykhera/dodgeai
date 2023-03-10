import pygame
import random
import math

# Define the Enemy class


class Enemy:
    def __init__(self, window_width, window_height, x=0, y=0, color=(255, 255, 255), max_speed=5, max_radius=100):
        self.x = random.randint(0, window_width)
        self.y = random.randint(0, window_height)
        while math.dist((x, y), (window_width / 2, window_height / 2)) < max_radius + 200:
            self.x = random.randint(0, window_width)
            self.y = random.randint(0, window_height)
        self.max_radius = max_radius
        self.radius = max_radius  # random.randint(1, max_radius)
        self.color = color
        self.max_speed = max_speed
        self.speed = max_speed  # random.randint(1, max_speed)
        # self.dx = random.randint(-self.speed, self.speed)
        # self.dy = random.randint(-self.speed, self.speed)
        self.window_width = window_width
        self.window_height = window_height
        self.direction = [random.randint(5, 85), random.randint(95, 175), random.randint(185, 265), random.randint(175, 355)][random.randint(0, 3)]  # random.randint(0, 360)
        self.random_position_perimeter()

    def draw(self, window):
        pygame.draw.circle(window, self.color, (self.x, self.y), self.radius)

    def random_position_perimeter(self, playerCoords=None):
        side = random.randint(1, 4)
        if side == 1:  # top
            self.x = random.randint(0, self.window_width)
            self.y = 0
        elif side == 2:  # right
            self.x = self.window_width
            self.y = random.randint(0, self.window_height)
        elif side == 3:  # bottom
            self.x = random.randint(0, self.window_width)
            self.y = self.window_height
        else:  # left
            self.x = 0
            self.y = random.randint(0, self.window_height)

        if playerCoords is not None:
            dist_to_target = math.sqrt((self.x - playerCoords[0]) ** 2 + (self.y - playerCoords[1]) ** 2)
            self.dx = self.speed * (playerCoords[0] - self.x) / dist_to_target
            self.dy = self.speed * (playerCoords[1] - self.y) / dist_to_target
        else:
            self.dx = self.speed * math.cos(math.radians(self.direction))
            self.dy = self.speed * math.sin(math.radians(self.direction))
            

    def move(self, playerCoords=None):
        # dx = self.speed * math.cos(math.radians(self.direction))
        # dy = self.speed * math.sin(math.radians(self.direction))
        # new_x = self.x + dx
        # new_y = self.y + dy
        new_x = self.x + self.dx
        new_y = self.y + self.dy

        # if new_x < self.radius or new_x > self.window_width - self.radius:
        #     # If the new position would be outside the screen boundaries, move the enemy to just inside the boundary
        #     if new_x < self.radius:
        #         self.x = self.radius
        #     else:
        #         self.x = self.window_width - self.radius
        #     # Reverse the direction of movement
        #     self.direction = 180 - self.direction + random.uniform(0, 1)  # random.uniform(-1, 1)
        # else:
        #     self.x = new_x

        # if new_y < self.radius or new_y > self.window_height - self.radius:
        #     # If the new position would be outside the screen boundaries, move the enemy to just inside the boundary
        #     if new_y < self.radius:
        #         self.y = self.radius
        #     else:
        #         self.y = self.window_height - self.radius
        #     # Reverse the direction of movement
        #     self.direction = -self.direction + random.uniform(0, 1)  # random.uniform(-1, 1)
        # else:
        #     self.y = new_y

        if new_x < 0 or new_y < 0 or new_x > self.window_width or new_y > self.window_height:
            self.random_position_perimeter(playerCoords)
        else:
            self.x = new_x
            self.y = new_y

    def reset(self):
        while math.dist((self.x, self.y), (self.window_width / 2, self.window_height / 2)) < self.max_radius + 50:
            self.x = random.randint(0, self.window_width)
            self.y = random.randint(0, self.window_height)

        self.speed = self.max_speed  # random.randint(1, self.max_speed)
        self.radius = self.max_radius  # random.randint(1, self.max_radius)
        self.direction = [random.randint(5, 85), random.randint(95, 175), random.randint(185, 265), random.randint(175, 355)][random.randint(0, 3)]  # random.randint(0, 360)

    def getState(self):
        # return (self.x, self.y, self.radius, self.speed, self.direction)
        return (self.direction / 360,)
