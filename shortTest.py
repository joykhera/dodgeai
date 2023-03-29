import gymnasium as gym
import mediapy as media
import numpy as np
import pygame

from gymnasium import spaces
from gymnasium.wrappers.time_limit import TimeLimit
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize, VecTransposeImage
import tensorboard
pygame.init()

CNN = True
MAX_ENEMIES = 5 if CNN else 1
ENEMY_R = 0.05
PLAYER_R = 0.05
ACTION_DIR = [np.r_[-1, 0], np.r_[1, 0], np.r_[0, -1], np.r_[0, 1]]

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

font = pygame.font.SysFont(None, 20)


class DodgeGameEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}

    def __init__(self, render_mode=None):
        self.render_mode = render_mode
        self.reset()
        self.action_space = spaces.Discrete(4)
        if CNN:
            self.observation_space = spaces.Box(0, 255, (64, 64, 3), dtype=np.uint8)
        else:
            self.observation_space = spaces.Dict({
                "agent": spaces.Box(0, 1, shape=(2,)),
                "enemy": spaces.Box(0, 1, shape=(self.num_enemies, 2)),
            })

    def _get_obs(self):
        if CNN:
            return self.render()
        else:
            return {
                "agent": self.player_pos,
                "enemy": self.player_pos - self.enemy_pos,
            }

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.num_enemies = self.np_random.integers(1, MAX_ENEMIES) if CNN else MAX_ENEMIES
        self.score = 0
        self.hp = 10
        self.player_pos = np.r_[0.5, 0.5]
        self.enemy_pos = self.np_random.random((self.num_enemies, 2))
        self.enemy_speed = self.np_random.random((self.num_enemies, 1)) * 0.02 + 0.01
        # self.enemy_direction = self.np_random.random((self.num_enemies, 1)) * 360
        # print(self.player_pos - self.enemy_pos)
        # print('aaa', np.linalg.norm(dir, axis=1, keepdims=True))
        self.enemy_dir = (self.player_pos - self.enemy_pos)
        self.enemy_dir /= np.linalg.norm(self.enemy_dir, axis=1, keepdims=True)
        # print(self.enemy_direction)
        return self._get_obs(), {}

    def step(self, action):
        self.player_pos += ACTION_DIR[action] * 0.04
        print(self.player_pos)
        # dir = self.player_pos - self.enemy_pos
        # dir /= np.linalg.norm(dir, axis=1, keepdims=True)
        # dir = (math.cos(math.radians(self.enemy_direction)), math.sin(math.radians(self.enemy_direction)))
        # self.enemy_pos += dir * self.enemy_speed

        # for i in range(len(self.enemy_pos)):
        # if math.dist(self.enemy_pos[i], self.player_pos) > 64:
        #   self.enemy_dir = (self.player_pos - self.enemy_pos)
        #   self.enemy_dir /= np.linalg.norm(self.enemy_dir, axis=1, keepdims=True)

        self.enemy_pos += self.enemy_dir * self.enemy_speed
        # print(self.enemy_pos, self.enemy_dir)
        # print(len(self.enemy_pos) == len(self.enemy_dir))
        for i in range(len(self.enemy_pos)):
            if self.enemy_pos[i][0] < 0 or self.enemy_pos[i][0] > 64 or self.enemy_pos[i][1] < 0 or self.enemy_pos[i][1] > 64:
                # self.enemy_dir[i] = (self.player_pos - self.enemy_pos[i])
                # self.enemy_dir[i] /= np.linalg.norm(self.enemy_dir[i], axis=1, keepdims=True)
                self.enemy_dir[i] *= -1

        game_over = self.is_game_over()
        self.hp -= game_over
        reward = 1 + game_over * -20
        done = self.hp == 0
        self.score += reward
        return self._get_obs(), reward, done, False, {}

    def is_game_over(self):
        return np.any(np.linalg.norm(self.player_pos - self.enemy_pos, axis=1) < (PLAYER_R + ENEMY_R)) or \
            np.any((self.player_pos < 0) | (self.player_pos > 1))

    def render(self):
        return self._render_frame()

    def _render_frame(self):
        r = 64 if CNN else 150
        canvas = pygame.Surface((r, r))
        canvas.fill(BLACK)
        pygame.draw.rect(canvas, WHITE, (0, 0, r, r), 2)
        pygame.draw.circle(canvas, WHITE, self.player_pos * r, PLAYER_R * r)
        for p in self.enemy_pos:
            pygame.draw.circle(canvas, RED, p * r, ENEMY_R * r)
            # pygame.draw.line(canvas, RED, p * r, self.player_pos * r, 2)
        if not CNN:
            canvas.blit(font.render(f"Score: {self.score}", True, WHITE), (10, 10))
            obs = self._get_obs()

            def fmt_obs(key, y):
                canvas.blit(font.render(f"{key}: {np.round(obs[key], 2)}", True, WHITE), (10, y))
            fmt_obs("agent", 30)
            fmt_obs("enemy", 50)
        return np.transpose(np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2))


def make_env():
    env = DodgeGameEnv(render_mode="rgb_array")
    env = TimeLimit(env, 5000)
    env = Monitor(env)
    return env


def make_vec_env(n):
    env = VecNormalize(DummyVecEnv([make_env] * n), norm_obs=not CNN)
    return VecTransposeImage(env) if CNN else env

def make_env():
    env = DodgeGameEnv(render_mode="rgb_array")
    env = TimeLimit(env, 300)
    env = Monitor(env)
    return env


def make_vec_env(n):
    env = VecNormalize(DummyVecEnv([make_env] * n), norm_obs=not CNN)
    print(env.observation_space)
    print(VecTransposeImage(env))
    return VecTransposeImage(env) if CNN else env

def train():
    env = make_vec_env(64)
    model = PPO("CnnPolicy" if CNN else "MultiInputPolicy", env, learning_rate=lambda x: x * 2.5e-4,
                n_steps=128, batch_size=256, n_epochs=4, gamma=0.95, clip_range=0.1, ent_coef=0.01,
                verbose=1, tensorboard_log="./training/logs/CnnPolicy/homing")
    eval_cb = EvalCallback(make_vec_env(1), eval_freq=500)
    model.learn(total_timesteps=1_000_000, callback=eval_cb)
    model.save("./model")
    env.save("./env")

def test():
    frames = []
    env = VecNormalize.load("./env", DummyVecEnv([make_env] * 16))
    env.training = False
    env.norm_reward = False
    model = PPO.load("./model", env=env)
    obs = env.reset()
    for _ in range(500):
        action, _state = model.predict(obs, deterministic=True)
        obs, _reward, _done, _info = env.step(action)
        frames.append(env.render())
    media.show_video(frames, fps=30, width=600)

train()