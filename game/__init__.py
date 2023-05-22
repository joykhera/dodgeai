from gym.envs.registration import register
from game.env.dodge_game import DodgeGameEnv

register(
    id="gym_examples/DodgeGame-v0",
    entry_point="gym_examples.envs:DodgeGameEnv",
)
