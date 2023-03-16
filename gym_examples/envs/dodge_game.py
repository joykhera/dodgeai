import gym
from gym import spaces
import pygame
import numpy as np
from random import randint
import math
from .player import Player
from .enemy import Enemy

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ENEMY_NUM = 1


class DodgeGameEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 200}

    def __init__(self, render_mode=None, window_size=800):
        self.window_size = window_size  # The size of the PyGame window
        self.player = Player(self.window_size, self.window_size, RED)
        self.enemies = []
        self.score = 0
        self.game_over = False
        
        for i in range(ENEMY_NUM):
            self.enemies.append(Enemy(self.window_size, self.window_size))

        # Observations are dictionaries with the agent's and the target's location.
        # Each location is encoded as an element of {0, ..., `size`}^2, i.e. MultiDiscrete([size, size]).
        self.observation_space = spaces.Dict(
            {
                "agent": spaces.Box(0, window_size - 1, shape=(2,), dtype=int),
                "enemy": spaces.Box(0, window_size - 1, shape=(3,), dtype=int),
                "walls": spaces.Box(0, window_size - 1, shape=(4,), dtype=int),
            }
        )

        # We have 4 actions, corresponding to "right", "up", "left", "down", "right"
        self.action_space = spaces.Discrete(4)

        """
        The following dictionary maps abstract actions from `self.action_space` to 
        the direction we will walk in if that action is taken.
        I.e. 0 corresponds to "right", 1 to "up" etc.
        """
        self._action_to_direction = {
            0: np.array([1, 0]),
            1: np.array([0, 1]),
            2: np.array([-1, 0]),
            3: np.array([0, -1]),
        }

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        """
        If human-rendering is used, `self.window` will be a reference
        to the window that we draw to. `self.clock` will be a clock that is used
        to ensure that the environment is rendered at the correct framerate in
        human-mode. They will remain `None` until human-mode is used for the
        first time.
        """
        self.window = None
        self.clock = None

    def _get_obs(self):
        return {
            "agent": self.player.getState(),
            "enemy": self.enemies[0].getState(),
            "walls": self.player.getWalls(),
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
            self._render_frame()

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
        reward = 1 if self.enemies[0].reached else 0  # Binary sparse rewards
        self.score += reward
        observation = self._get_obs()
        info = self._get_info()
        
        if self.render_mode == "human":
            self._render_frame()

        # return observation, reward, terminated, False, info
        return observation, reward, terminated, info

    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_frame()

    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.font = pygame.font.SysFont(None, 30)
            self.window = pygame.display.set_mode((self.window_size, self.window_size))
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface((self.window_size, self.window_size))
        canvas.fill(BLACK)

        self.player.draw(canvas)
        for enemy in self.enemies:
            enemy.draw(canvas)
            pygame.draw.line(canvas, RED, (enemy.x, enemy.y), (self.player.x, self.player.y), 2)
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        canvas.blit(score_text, (10, 10))

        if self.render_mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(self.metadata["render_fps"])
        else:  # rgb_array
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )
            
    def move_enemies(self):
        for enemy in self.enemies:
            # enemy.move()
            enemy.move((self.player.x, self.player.y))

            # Check for collisions with the player
            if self.player.is_colliding_with(enemy):
                self.game_over = True

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
