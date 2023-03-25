import gym
from gym import spaces
import pygame
import numpy as np
from random import randint
import math
from .player import Player
from .enemy import Enemy
from matplotlib import pyplot as plt
from skimage.transform import resize
import itertools

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)


class DodgeGameEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 300}

    def __init__(self, render_mode=None, window_size=500, policy='CnnPolicy', enemy_movement='aimed', enemy_num=1, random_player_speed=False, random_enemy_speed=False, random_player_radius=False, random_enemy_radius=False):
        self.window_size = window_size  # The size of the PyGame window
        self.player = Player(self.window_size, self.window_size, RED, random_radius=random_player_radius, random_speed=random_player_speed)
        self.enemies = []
        self.score = 0
        self.game_over = False
        self.policy = policy
        self.enemy_movement = enemy_movement
        self.enemy_num = enemy_num
        self.hp = 10

        for i in range(enemy_num):
            self.enemies.append(Enemy(self.window_size, self.window_size, enemy_movement=enemy_movement, random_radius=random_enemy_radius, random_speed=random_enemy_speed))
        # Observations are dictionaries with the agent's and the target's location.
        # Each location is encoded as an element of {0, ..., `size`}^2, i.e. MultiDiscrete([size, size]).

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        if policy == 'CnnPolicy':
            self.observation_space = spaces.Box(low=0, high=255, shape=(50, 50, 3), dtype=np.uint8)
        elif policy == 'MultiInputPolicy':
            if enemy_num > 0:
                self.observation_space = spaces.Dict(
                    {
                        "agent": spaces.Box(0, window_size - 1, shape=(2,), dtype=int),
                        "enemy": spaces.Box(1 - window_size, window_size - 1, shape=(4 * enemy_num,), dtype=int),
                        "walls": spaces.Box(1 - window_size, window_size - 1, shape=(4,), dtype=int),
                    }
                )
            else:
                self.observation_space = spaces.Dict(
                    {
                        "agent": spaces.Box(0, window_size - 1, shape=(2,), dtype=int),
                        "walls": spaces.Box(1 - window_size, window_size - 1, shape=(4,), dtype=int),
                    }
                )
        elif policy == 'MathPolicy':
            self.observation_space = spaces.Dict(
                {
                    "agent": spaces.Box(0, window_size - 1, shape=(3,), dtype=int),
                    "enemy": spaces.Box(1 - window_size, window_size - 1, shape=(4 * enemy_num,), dtype=int),
                }
            )

        # We have 4 actions, corresponding to "right", "up", "left", "down", "right"
        self.action_space = spaces.Discrete(4)

        self.clock = None
        if render_mode == 'human' or policy == 'CnnPolicy':
            self.window = pygame.display.set_mode((self.window_size, self.window_size))

        if render_mode == 'human':
            pygame.init()
            pygame.display.init()
            self.font = pygame.font.SysFont(None, 30)

    def _get_obs(self):
        if self.policy == 'CnnPolicy':
            arr = np.transpose(
                np.array(pygame.surfarray.pixels3d(self.window)), axes=(1, 0, 2)
            )
            resizedArr = resize(arr, (50, 50))
            # plt.ion()
            # plt.imshow(resizedArr, interpolation='nearest')
            # plt.show()
            # print(resizedArr.shape)
            return resizedArr
        
        elif self.policy == 'MultiInputPolicy':
            if self.enemy_num > 0:
                return {
                    "agent": self.player.getState(),
                    "enemy": tuple(itertools.chain(*[enemy.getState(player=self.player) for enemy in self.enemies])),
                    # "enemy": tuple(itertools.chain(*[enemy.getState() for enemy in self.enemies])),
                    "walls": self.player.getWalls(),
                }
            else:
                return {
                    "agent": self.player.getState(),
                    "walls": self.player.getWalls(),
                }
                
        elif self.policy == 'MathPolicy':
            return {
                "agent": self.player.getState(radius=True),
                "enemy": tuple(itertools.chain(*[enemy.getState(radius=True) for enemy in self.enemies])),
            }
            

    def _get_info(self):
        return {
            # "distance": np.linalg.norm(
            #     self.player.location() - self.enemies[0].location(), ord=1
            # )
        }

    def reset(self, seed=None, options=None):
        self.game_over = False
        self.player.reset()
        [enemy.reset() for enemy in self.enemies]
        self.score = 0

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self.render()

        # return observation, info
        return observation

    def step(self, action):
        self.player.aiMove(action)
        self.move_enemies()

        if self.player.touch_wall():
            self.game_over = True

        # An episode is done iff the agent has reached the target
        # terminated = np.array_equal(self._agent_location, self._target_location)
        terminated = self.game_over
        if len(self.enemies) and self.enemy_movement == 'aimed':
            # reward = 0.1 if not self.game_over else -1
            # reward = 1 if self.enemies[0].reached else 0  # Binary sparse rewards
            # reward = 1 - math.dist((self.player.x, self.player.y), (self.window_size // 2, self.window_size // 2)) / self.window_size
            
            minEnemyDist = self.window_size
            maxEnemyRadius = 0
            for enemy in self.enemies:
                dist = math.dist((self.player.x, self.player.y), (enemy.x, enemy.y))
                if dist < minEnemyDist:
                    minEnemyDist = dist
                if enemy.radius > maxEnemyRadius:
                    maxEnemyRadius = enemy.radius
            # reward = minEnemyDist / self.window_size
            
            # if self.game_over:
            #     reward = -1
            # elif minEnemyDist < (self.player.radius + maxEnemyRadius) * 2:
            #     reward = -0.5
            # elif min(self.player.getWalls()) < self.player.radius * 2:
            #     reward = -0.5
            # else:
            #     reward = 0.1
            
            self.hp -= self.game_over
            reward = 1 + self.game_over * -20
            done = self.hp == 0
            # print(self.game_over, self.hp, reward)
            self.score += reward
            
            # reward = min(self.player.x - self.player.radius, self.window_size - self.player.radius - self.player.x, self.player.y -
            #              self.player.radius, self.window_size - self.player.radius - self.player.y) / self.window_size
        else:
            reward = 0.1
        self.score += reward
        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self.render()

        # return observation, reward, terminated, False, info
        # return observation, reward, terminated, info
        return observation, reward, done, info

    def render(self):
        # if self.window is None and self.render_mode == "human":
        #     pygame.init()
        #     pygame.display.init()
        #     self.font = pygame.font.SysFont(None, 30)
        #     self.window = pygame.display.set_mode((self.window_size, self.window_size))
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface((self.window_size, self.window_size))
        canvas.fill(BLACK)

        self.player.draw(canvas)
        for enemy in self.enemies:
            enemy.draw(canvas)
            # pygame.draw.line(canvas, RED, (enemy.x, enemy.y), (self.player.x, self.player.y), 2)
        score_text = self.font.render(f"Score: {round(self.score)}", True, WHITE)
        canvas.blit(score_text, (10, 10))
        borderWidth = 2
        pygame.draw.line(canvas, WHITE, (0, 0), (0, self.window_size - borderWidth), borderWidth)
        pygame.draw.line(canvas, WHITE, (0, 0), (self.window_size - borderWidth, 0), borderWidth)
        pygame.draw.line(canvas, WHITE, (0, self.window_size - borderWidth), (self.window_size - borderWidth, self.window_size - borderWidth), borderWidth)
        pygame.draw.line(canvas, WHITE, (self.window_size - borderWidth, 0), (self.window_size - borderWidth, self.window_size - borderWidth), borderWidth)

        if self.render_mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(self.metadata["render_fps"])
        # else:  # rgb_array
        #     return np.transpose(
        #         np.array(pygame.surfarray.pixels3d(self.window)), axes=(1, 0, 2)
        #     )

    def move_enemies(self):
        for enemy in self.enemies:
            # enemy.move()
            enemy.move((self.player.x, self.player.y))

            # Check for collisions with the player
            if self.player.is_colliding_with(enemy):
                self.game_over = True

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # self.game_over = True
                    pygame.quit()

            keys = pygame.key.get_pressed()
            self.player.move(keys)
            self.move_enemies()
            self.render()

            if self.player.touch_wall():
                self.game_over = True

            pygame.display.update()
            self.clock.tick(60)

            if self.game_over:
                self.reset()
                
            self.score += 0.1
