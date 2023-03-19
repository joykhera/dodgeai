import gym
# import gym_examples
from gym_examples import DodgeGameEnv
import os
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnRewardThreshold

import tensorboard

stop_callback = StopTrainingOnRewardThreshold(reward_threshold=10000, verbose=1)


def play(enemy_num=1):
    game = DodgeGameEnv(render_mode='human', enemy_num=enemy_num)
    game.run()


def run(timestep=100000, method='both', load_file=None, save_file=None, policy='MultiInputPolicy', n_eval_episodes=20, enemy_movement='aimed', stop_callback=stop_callback, enemy_num=1):
    assert not (method == 'test' and not load_file and not save_file)
    
    save_dir = os.path.join('training', 'savedModels', policy)
    if save_file:
        log_path = os.path.join('training', 'logs', policy, save_file)
        save_path = os.path.join(save_dir, save_file)
    elif load_file:
        log_path = os.path.join('training', 'logs', policy, load_file)
        save_path = os.path.join(save_dir, load_file)
    else:
        log_path = os.path.join('training', 'logs', policy)
        save_path = os.path.join(save_dir, str(timestep))

    if load_file:
        load_path = os.path.join(save_dir, load_file)
        model = PPO.load(load_path)
        
    if method == 'train' or method == 'both':
        trainEnv = DodgeGameEnv(render_mode='rgb_array', policy=policy, enemy_movement=enemy_movement, enemy_num=enemy_num)
        
        if not load_file:
            model = PPO(policy, env=trainEnv, verbose=1, tensorboard_log=log_path)
            
        model.set_env(trainEnv)
        if stop_callback:
            eval_callback = EvalCallback(trainEnv, callback_on_new_best=stop_callback, eval_freq=10000, best_model_save_path=save_dir, verbose=1)
            model.learn(total_timesteps=timestep, callback=eval_callback)
        else:
            model.learn(total_timesteps=timestep)
        model.save(save_path)
        
    if method == 'test':
        model = PPO.load(load_path)
        
    if method == 'test' or method == 'both':
        testEnv = DodgeGameEnv(render_mode='human', policy=policy, enemy_movement=enemy_movement, enemy_num=enemy_num)
        model.set_env(testEnv)
        print(evaluate_policy(model, testEnv, n_eval_episodes=n_eval_episodes))
        

run(timestep=1000000, method='train', load_file='reward_stay_alive')
# run(timestep=10000000, method='train', save_file='reward_mult_enemy_dist', enemy_num=10)
# run(timestep=10000000, method='test', load_file='best_model')

# play(enemy_num=5)