import gym
# import gym_examples
from gym_examples import DodgeGameEnv
from gym_examples import GridWorldEnv
import os
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy
import tensorboard

def train(timestep=2000000, load_model='model1000k'):
    env = DodgeGameEnv()
    log_path = os.path.join('training', 'logs')
    load_path = os.path.join('training', 'savedModels', load_model)
    model = None
    if load_path:
        model = PPO.load(load_path)
        model.set_env(env)
    else:
        model = PPO('MultiInputPolicy', env, verbose=1, tensorboard_log=log_path)

    model.learn(total_timesteps=timestep)
    save_path = os.path.join('training', 'savedModels', 'model{}k'.format(timestep//1000))
    model.save(save_path)


def test(modelName='model2000k'):
    ppo_path = os.path.join('training', 'savedModels', modelName)
    env = DodgeGameEnv(render_mode='human')
    model = PPO.load(ppo_path)
    print(evaluate_policy(model, env, n_eval_episodes=20))

train()
# test()