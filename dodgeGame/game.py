import pygame
import random
from .player import Player
from .enemy import Enemy
import math

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
        self.player = Player(self.window_width // 2, self.window_height // 2, 10, RED, 10, self.window_width, self.window_height)
        self.enemies = []
        for i in range(ENEMY_NUM):
            self.enemies.append(Enemy(self.window_width, self.window_height))
        self.score = 0
        self.game_over = False
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 30)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # self.game_over = True
                pygame.quit()

        keys = pygame.key.get_pressed()
        self.player.move(keys)

    def move_enemies(self):
        for enemy in self.enemies:
            enemy.move()

            # Check for collisions with the player
            if self.player.is_colliding_with(enemy):
                self.game_over = True

        # Increment the score
        self.score = round(self.score + 0.1, 1)

    def draw(self):
        self.window.fill(BLACK)
        self.player.draw(self.window)
        for enemy in self.enemies:
            enemy.draw(self.window)

        # Draw the score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.window.blit(score_text, (10, 10))

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
                
    def loop(self, move, draw=True):
        self.player.aiMove(move)
        self.move_enemies()
        
        if self.player.touch_wall():
            self.game_over = True
        
        # if self.game_over:
        #     self.reset()
            
        if draw:
            self.draw()
            pygame.display.update()
        
        
    def reset(self):
        """Resets the entire game."""
        self.game_over = False
        self.player.reset()
        [enemy.reset() for enemy in self.enemies]
        self.score = 0
        
    def get_state(self):
        state = self.player.getState()
        for enemy in self.enemies:
            state += ((enemy.x - self.player.x) / self.window_width, (enemy.y - self.player.y) / self.window_height)
            state += enemy.getState()
        return state

