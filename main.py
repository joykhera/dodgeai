import gym
# import gym_examples
from gym_examples import DodgeGameEnv
import os
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy

import tensorboard


def run(timestep=100000, method='both', load_file=None, save_file=None, policy='CnnPolicy', n_eval_episodes=10):
    assert not (method == 'test' and not load_file)
    
    save_dir = os.path.join('training', 'savedModels', policy)
    if save_file:
        log_path = os.path.join('training', 'logs', policy, save_file)
        save_path = os.path.join(save_dir, save_file)
    else:
        log_path = os.path.join('training', 'logs', policy)
        save_path = os.path.join(save_dir, str(timestep))

    if load_file:
        load_path = os.path.join(save_dir, load_file)
        model = PPO.load(load_path)
    
    if method == 'train' or method == 'both':
        trainEnv = DodgeGameEnv(render_mode='rgb_array', policy=policy)
        
        if not load_file:
            model = PPO(policy, env=trainEnv, verbose=1, tensorboard_log=log_path)
            
        model.set_env(trainEnv)
        model.learn(total_timesteps=timestep)
        model.save(save_path)
        
    if method == 'test':
        model = PPO.load(load_path)
        
    if method == 'test' or method == 'both':
        testEnv = DodgeGameEnv(render_mode='human', policy=policy)
        model.set_env(testEnv)
        print(evaluate_policy(model, testEnv, n_eval_episodes=n_eval_episodes))
        

run(timestep=10000000, method='train', policy='MultiInputPolicy', n_eval_episodes=20, save_file='speed1')
# run(timestep=5000000, method='train', policy='MultiInputPolicy', n_eval_episodes=20)
# run(timestep=1000000, method='both', policy='CnnPolicy', n_eval_episodes=20)
