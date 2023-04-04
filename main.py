import gym
from gym_examples import DodgeGameEnv
import os
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnRewardThreshold
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize, VecTransposeImage
from stable_baselines3.common.monitor import Monitor
from gymnasium.wrappers.time_limit import TimeLimit
from gymnasium.wrappers.frame_stack import FrameStack
from gymnasium.wrappers.resize_observation import ResizeObservation
import tensorboard

stop_callback = StopTrainingOnRewardThreshold(reward_threshold=100000, verbose=1)


def play(env_params, policy='CnnPolicy'):
    game = DodgeGameEnv(
        policy=policy,
        render_mode='human',
        window_size=env_params['window_size'],
        enemy_movement=env_params['enemy_movement'],
        enemy_num=env_params['enemy_num'],
        normalize=env_params['normalize'],
        player_speed=env_params['player_speed'],
        enemy_speed=env_params['enemy_speed'],
        player_radius=env_params['player_radius'],
        enemy_radius=env_params['enemy_radius'],
        randomize_player_speed=env_params['randomize_player_speed'],
        randomize_enemy_speed=env_params['randomize_enemy_speed'],
        randomize_player_radius=env_params['randomize_player_radius'],
        randomize_enemy_radius=env_params['randomize_enemy_radius'],
        randomize_enemy_num=env_params['randomize_enemy_num'],
    )
    # game.run()
    game.reset()
    while True:
        observation, reward, terminated, _, info = game.step(game.action_space.sample())
        if terminated:
            game.reset()


def make_env(env_params, policy='CnnPolicy', render_mode='rgb_array'):

    env = DodgeGameEnv(
        render_mode=render_mode,
        policy=policy,
        window_size=env_params['window_size'],
        enemy_movement=env_params['enemy_movement'],
        enemy_num=env_params['enemy_num'],
        normalize=env_params['normalize'],
        player_speed=env_params['player_speed'],
        enemy_speed=env_params['enemy_speed'],
        player_radius=env_params['player_radius'],
        enemy_radius=env_params['enemy_radius'],
        randomize_player_speed=env_params['randomize_player_speed'],
        randomize_enemy_speed=env_params['randomize_enemy_speed'],
        randomize_player_radius=env_params['randomize_player_radius'],
        randomize_enemy_radius=env_params['randomize_enemy_radius'],
        randomize_enemy_num=env_params['randomize_enemy_num'],
    )

    # env = TimeLimit(env, 1000)
    if render_mode == 'rgb_array':
        env = Monitor(env)
    return env


def make_vec_env(
    env_params,
    policy='CnnPolicy',
    render_mode='rgb_array',
    vec_env_num=64,
):
    env = VecNormalize(
        DummyVecEnv([lambda: make_env(env_params, render_mode=render_mode, policy=policy)] * vec_env_num), norm_obs=policy != 'CnnPolicy')
    return VecTransposeImage(env) if policy == 'CnnPolicy' else env


def train(env_params,
          timestep=100000,
          load_file=None,
          save_file=None,
          policy='CnnPolicy',
          stop_callback=stop_callback,
          vec_env_num=64,
          learning_rate=0.00025,
          n_steps=128,
          batch_size=256,
          n_epochs=4,
          gamma=0.95,
          clip_range=0.1,
          ent_coef=0.01,
          verbose=1,
          ):

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

    if isinstance(vec_env_num, int):
        env = make_vec_env(env_params, vec_env_num=vec_env_num, policy=policy, render_mode='rgb_array')
    else:
        env = make_env(env_params, policy=policy, env_params=env_params)

    if not load_file:
        model = PPO(
            env=env,
            tensorboard_log=log_path,
            policy=policy,
            learning_rate=learning_rate,
            # learning_rate=lambda x: x * learning_rate,
            n_steps=n_steps,
            batch_size=batch_size,
            n_epochs=n_epochs,
            gamma=gamma,
            clip_range=clip_range,
            ent_coef=ent_coef,
            verbose=verbose,
        )

    model.set_env(env)
    if stop_callback:
        # eval_callback = EvalCallback(env, callback_on_new_best=stop_callback, eval_freq=10000, best_model_save_path=save_dir, verbose=1)
        eval_cb = EvalCallback(make_vec_env(1), eval_freq=500)
        model.learn(total_timesteps=timestep, callback=eval_cb)
    else:
        model.learn(total_timesteps=timestep)
    model.save(save_path)


def test(
    env_params,
    load_file,
    vec_env_num=16,
    policy='CnnPolicy',
):
    save_dir = os.path.join('training', 'savedModels', policy)
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


env_params = {
    'window_size': 64,
    'enemy_movement': 'aimed',
    'enemy_num': 5,
    'normalize': True,
    'player_speed': 0.03,
    'enemy_speed': 0.02,
    'player_radius': 0.05,
    'enemy_radius': 0.05,
    'randomize_player_speed': False,
    'randomize_enemy_speed': False,
    'randomize_player_radius': False,
    'randomize_enemy_radius': False,
    'randomize_enemy_num': False,
}


# add funtionality to to make save_file name in function
# train(timestep=5000000, policy='CnnPolicy', learning_rate=0.00005, window_size=100, save_file='learning_rate=0.00005,window_size=100')
# run(timestep=100000000, method='train', save_file='n_steps=500000,learning_rate=0.000005,enemy_num=5', enemy_num=5)
# test(policy='CnnPolicy', max_enemy_num=5, enemy_movement='random', enemy_speed=0.02, load_file='learning_rate=0.00005,max_enemy_num=5,enemy_movement=random,enemy_speed=0.02')
# test(policy='CnnPolicy', max_enemy_num=5, enemy_speed=0.01, enemy_movement='random', load_file='vec_env_num=64,learning_rate=0.00005,enemy_num=5,enemy_speed=0.01')
# play(env_params)
