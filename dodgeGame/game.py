import pygame
import random
from .player import Player
from .enemy import Enemy
import math
from collections import Counter

# Set up the window
pygame.init()
pygame.display.set_caption("Dodger")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ENEMY_NUM = 1

class Game:
    def __init__(self, window, width, height):
        self.window_width = width
        self.window_height = height
        self.window = window
        self.player = Player(self.window_width, self.window_height, RED)
        self.enemies = []
        self.score = [0]
        self.game_over = False
        self.game_over_wall = False
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 30)
        
        for i in range(ENEMY_NUM):
            self.enemies.append(Enemy(self.window_width, self.window_height))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # self.game_over = True
                pygame.quit()

        keys = pygame.key.get_pressed()
        self.player.move(keys)

    def move_enemies(self):
        for enemy in self.enemies:
            # enemy.move()
            enemy.move((self.player.x, self.player.y), self.score)

            # Check for collisions with the player
            if self.player.is_colliding_with(enemy):
                self.game_over = True

        # Increment the score
        # self.score = round(self.score + 0.001, 3)

    def draw(self):
        self.window.fill(BLACK)
        self.player.draw(self.window)
        for enemy in self.enemies:
            enemy.draw(self.window)
            pygame.draw.line(self.window, RED, (enemy.x, enemy.y), (self.player.x, self.player.y), 2)
        score_text = self.font.render(f"Score: {self.score[0]}", True, WHITE)
        self.window.blit(score_text, (10, 10))
        # print(self.player.last_locations, set(self.player.last_locations))
        # elemCounts = Counter(self.player.last_locations).values().sort(reverse=True)
        # if elemCounts[0] + elemCounts[1] > 15:
        #     self.game_over = True

    def run(self):
        while True:
            self.handle_events()
            self.move_enemies()
            self.draw()
            
            if self.player.touch_wall():
                self.game_over = True
            
            pygame.display.update()
            self.clock.tick(60)
            
            if self.game_over:
                self.reset()
                
            # print(self.get_state())
                
    def loop(self, move, numGames, numGamesDrawAfter=50000, scoreDrawAfter=10000):
        self.player.aiMove(move)
        self.move_enemies()
        
        if self.player.touch_wall():
            self.game_over_wall = True
        
        # if max(self.player.last_locations) - min(self.player.last_locations) < 20:
        #     self.game_over = True
        # if self.score > 0.01:
        #     print(self.player.last_locations, set(self.player.last_locations), len(set(self.player.last_locations)))
        # if self.score > 0.01 and len(set(self.player.last_locations)) < 4:
        #     self.game_over = True
        
        # if self.score[0] > 0.01:
        #     maxDist = 0
        #     for coord1 in self.player.last_locations:
        #         for coord2 in self.player.last_locations:
        #             if coord1 != coord2:
        #                 dist = math.sqrt((coord2[0] - coord1[0]) ** 2 + (coord2[1] - coord1[1]) ** 2)
        #                 if dist > maxDist:
        #                     maxDist = dist
        #     # print(self.player.last_locations, maxDist)
        #     if maxDist < 35:
        #         self.game_over = True
                
        blackScreen = True
        if numGames >= numGamesDrawAfter or self.score[0] >= scoreDrawAfter:
            self.draw()
            pygame.display.update()
            blackScreen = False
        if not blackScreen:
            self.window.fill(BLACK)
            blackScreen = True
        
        
    def reset(self):
        self.game_over = False
        self.game_over_wall = False
        self.player.reset()
        [enemy.reset() for enemy in self.enemies]
        self.score[0] = 0
        
    def get_state(self):
        state = self.player.getState()
        for enemy in self.enemies:
            state += ((enemy.x - self.player.x) / self.window_width, (enemy.y - self.player.y) / self.window_height)
            state += enemy.getState()
            # playerEnemyDir = math.atan2(self.player.y - enemy.y, self.player.x - enemy.x)
            # state += (((playerEnemyDir + 3.14) / 6.28),)
        return state

