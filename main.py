import gym
# import gym_examples
from gym_examples import DodgeGameEnv
from gym_examples import GridWorldEnv
import os
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnRewardThreshold

import tensorboard

stop_callback = StopTrainingOnRewardThreshold(reward_threshold=10, verbose=1)

def train(timestep=2000000, load_model='model2000k'):
    env = DodgeGameEnv()
    log_path = os.path.join('training', 'logs')
    load_path = os.path.join('training', 'savedModels', load_model)
    model = None
    if load_path:
        model = PPO.load(load_path)
        model.set_env(env)
    else:
        model = PPO('MultiInputPolicy', env, verbose=1, tensorboard_log=log_path)


    save_path = os.path.join('training', 'savedModels', 'model{}k'.format(timestep//1000))
    eval_callback = EvalCallback(env, callback_on_new_best=stop_callback, eval_freq=10000, best_model_save_path=os.path.join('training', 'savedModels'), verbose=1)
    model.learn(total_timesteps=timestep, callback=eval_callback)
    model.save(save_path)


def test(modelName='best_model'):
    ppo_path = os.path.join('training', 'savedModels', modelName)
    env = DodgeGameEnv(render_mode='human')
    model = PPO.load(ppo_path)
    print(evaluate_policy(model, env, n_eval_episodes=20))

# train()
test()