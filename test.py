import os
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize, VecTransposeImage
from utils import get_different_params, make_vec_env, make_env
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnRewardThreshold
from defaultParams import default_model_hyperparams, default_env_params


def test(env_params, model_hyperparams, load_file=None, vec_env_num=16, policy='CnnPolicy'):
    save_dir = os.path.join('training', 'savedModels', policy)
    if not load_file:
        different_params = get_different_params(default_model_hyperparams, default_env_params, model_hyperparams, env_params)
        load_file = ','.join(different_params)
    load_path = os.path.join(save_dir, load_file)

    if isinstance(vec_env_num, int):
        env = make_vec_env(env_params, render_mode='human', vec_env_num=vec_env_num, policy=policy)
        env.save("./env")
        frames = []
        env = VecNormalize.load("./env", DummyVecEnv([lambda: make_env(env_params)] * vec_env_num))
        env.training = False
        env.norm_reward = False
        model = PPO.load(load_path, env=env)
        obs = env.reset()
        while True:
            action, _state = model.predict(obs, deterministic=True)
            obs, _reward, _done, _info = env.step(action)
            frames.append(env.render())
    else:
        env = make_env(env_params, render_mode='human')
        model = PPO.load(load_path, env)
        obs = env.reset()
        while True:
            action, _state = model.predict(obs, deterministic=True)
            obs, _reward, _done, _, _info = env.step(action)
            if _done:
                env.reset()