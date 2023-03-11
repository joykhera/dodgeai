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
        self.last_locations = []

    def draw(self, window):
        # print(self.last_locations)
        pygame.draw.circle(window, self.color, (self.x, self.y), self.radius)
        
    def aiMove(self, move):
        # print(move)
        if len(move) == 1:
            if move[0] < -0.5:
                self.x -= self.speed
            elif move[0] < 0:
                self.x += self.speed
            if move[0] < 0.5:
                self.y -= self.speed
            else:
                self.y += self.speed
        elif (len(move)) == 2:
            if move[0] < 0:
                self.x -= self.speed
            else:
                self.x += self.speed
            if move[1] < 0:
                self.y -= self.speed
            else:
                self.y += self.speed
        elif (len(move)) == 4:
            if move == 0:
                self.x -= self.speed
            elif move == 1:
                self.x += self.speed
            elif move == 2:
                self.y -= self.speed
            else:
                self.y += self.speed
                
        if len(self.last_locations) > 10:
            self.last_locations.pop(0)
        self.last_locations.append((self.x, self.y))
        # print(self.last_locations)

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
        
    def getState(self):
        return (self.x / self.window_width, self.y / self.window_height, (self.x - self.radius) / self.window_width, (self.window_width - self.radius - self.x) / self.window_width, (self.y - self.radius) / self.window_height, (self.window_height - self.radius - self.y) / self.window_height)
