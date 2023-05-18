import tensorboard
from utils import get_different_params
from play import play
from train import train
from test import test
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnRewardThreshold
from defaultParams import default_model_hyperparams, default_env_params

model_hyperparams = {
    'timestep': 5000000,
    'vec_env_num': 64,
    'learning_rate': 0.00075,
    'learning_rate_lambda': True,
    'n_steps': 128,
    'batch_size': 256,
    'n_epochs': 4,
    'gamma': 0.95,
    'gae_lambda': 0.95,
    'clip_range': 0.1,
    'ent_coef': 0.01,
    'vf_coef': 0.5,
    'max_grad_norm': 0.5,
}

env_params = {
    'window_size': 64,
    'model_window_size': 64,
    'enemy_movement': 'aimed',
    # 'enemy_movement': 'aimed_bounce',
    # 'enemy_movement': 'random',
    'enemy_num': 1,
    'hp': 10,
    'death_penalty': 20,
    'normalize': True,
    'player_speed': 0.03,
    'enemy_speed': 0.02,
    'player_radius': 0.05,
    'enemy_radius': 0.05,
    'action_space': 4,
    'randomize_player_speed': False,
    'randomize_enemy_speed': False,
    'randomize_player_radius': False,
    'randomize_enemy_radius': False,
    'randomize_enemy_num': False,
}

# make test() get get default load file name from env_params
print(get_different_params(default_model_hyperparams, default_env_params, model_hyperparams, env_params))
# train(env_params, model_hyperparams, policy='CnnPolicy')
test(env_params, model_hyperparams, policy='CnnPolicy', vec_env_num=None, load_file='learning_rate=7.5e-05,learning_rate_lambda=True')
# test(env_params, model_hyperparams,  policy='CnnPolicy', window_size=128)
# play(env_params)
