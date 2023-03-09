import pygame


class Player:
    def __init__(self, x, y, radius, color, speed, window_width, window_height):
        self.initx = x
        self.inity = y
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = speed
        self.window_width = window_width
        self.window_height = window_height

    def draw(self, window):
        pygame.draw.circle(window, self.color, (self.x, self.y), self.radius)
        
    def aiMove(self, move):
        if move == 0:
            self.x -= self.speed
        elif move == 1:
            self.x += self.speed
        elif move == 2:
            self.y -= self.speed
        else:
            self.y += self.speed

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
        if self.x > self.window_width - self.radius:
            return True
        if self.y < self.radius:
            return True
        if self.y > self.window_height - self.radius:
            return True

    def reset(self):
        self.x = self.initx
        self.y = self.inity
        
    def getState(self):
        return (self.x / self.window_width, self.y / self.window_height, (self.x - self.radius) / self.window_width, (self.window_width - self.radius - self.x) / self.window_width, (self.y - self.radius) / self.window_height, (self.window_height - self.radius - self.y) / self.window_height)
