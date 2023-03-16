from gym.envs.registration import register
# from envs.grid_world import GridWorldEnv
from gym_examples.envs.grid_world import GridWorldEnv
from gym_examples.envs.dodge_game import DodgeGameEnv

register(
    id="gym_examples/GridWorld-v0",
    entry_point="gym_examples.envs:GridWorldEnv",
)

register(
    id="gym_examples/DodgeGame-v0",
    entry_point="gym_examples.envs:DodgeGameEnv",
)
