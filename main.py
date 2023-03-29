import gym
from gym_examples import DodgeGameEnv
import os
from stable_baselines3 import PPO, A2C
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnRewardThreshold
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize, VecTransposeImage
from stable_baselines3.common.monitor import Monitor
from gymnasium.wrappers.time_limit import TimeLimit
from gymnasium.wrappers.frame_stack import FrameStack
from gymnasium.wrappers.resize_observation import ResizeObservation
import mediapy as media
import tensorboard

stop_callback = StopTrainingOnRewardThreshold(reward_threshold=100000, verbose=1)


def play(enemy_num=1, random_player_speed=False, random_enemy_speed=False, random_player_radius=False, random_enemy_radius=False, enemy_movement='aimed', normalize=False):
    game = DodgeGameEnv(render_mode='human', enemy_num=enemy_num, enemy_movement=enemy_movement, normalize=normalize, random_player_speed=random_player_speed,
                        random_enemy_speed=random_enemy_speed, random_player_radius=random_player_radius, random_enemy_radius=random_enemy_radius)
    # game.run()
    game.reset()
    while True:
        observation, reward, terminated, _, info = game.step(game.action_space.sample())
        if terminated:
            game.reset()


def run(timestep=100000,
        model_type='PPO',
        method='both',
        load_file=None,
        save_file=None,
        policy='MultiInputPolicy',
        n_eval_episodes=20,
        enemy_movement='aimed',
        normalize=False,
        stop_callback=stop_callback,
        vec_env_num=None,
        train_window_size=64,
        test_window_size=64,
        learning_rate=0.00025,
        n_steps=128,
        batch_size=256,
        n_epochs=4,
        gamma=0.95,
        clip_range=0.1,
        ent_coef=0.01,
        verbose=1,
        enemy_num=1,
        random_player_speed=False,
        random_enemy_speed=False,
        random_player_radius=False,
        random_enemy_radius=False,
        ):

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
        if model_type == 'PPO':
            model = PPO.load(load_path)
        elif model_type == 'A2C':
            model = A2C.load(load_path)

    def make_env(render_mode='rgb_array'):
        window_size = train_window_size if render_mode == 'rgb_array' else test_window_size
        env = DodgeGameEnv(render_mode=render_mode, policy=policy, window_size=window_size, enemy_movement=enemy_movement, enemy_num=enemy_num, normalize=normalize, random_player_speed=random_player_speed,
                           random_enemy_speed=random_enemy_speed, random_player_radius=random_player_radius, random_enemy_radius=random_enemy_radius)

        # env = TimeLimit(env, 1000)
        if render_mode == 'rgb_array':
            env = Monitor(env)
        # env = ResizeObservation(env, (50, 50))
        # print(env)
        # env = FrameStack(env, 4)
        return env

    def make_vec_env(n, render_mode='rgb_array'):
        env = VecNormalize(DummyVecEnv([lambda: make_env(render_mode=render_mode)] * n), norm_obs=policy != 'CnnPolicy')
        return VecTransposeImage(env) if policy == 'CnnPolicy' else env

    if method == 'train' or method == 'both':
        if isinstance(vec_env_num, int):
            trainEnv = make_vec_env(vec_env_num)
        else:
            trainEnv = make_env()

        if not load_file:
            if model_type == 'PPO':
                model = PPO(
                    env=trainEnv,
                    tensorboard_log=log_path,
                    policy=policy,
                    learning_rate=learning_rate,
                    n_steps=n_steps,
                    batch_size=batch_size,
                    n_epochs=n_epochs,
                    gamma=gamma,
                    clip_range=clip_range,
                    ent_coef=ent_coef,
                    verbose=verbose,
                )
                # model = PPO(policy, env=trainEnv, learning_rate=lambda x: x * 2.5e-4, batch_size=256, n_epochs=4,
                #             gamma=0.95, clip_range=0.2, ent_coef=0.01,
                #             verbose=1, tensorboard_log=log_path)
                # model = PPO(policy, env=trainEnv, verbose=1, tensorboard_log=log_path, n_steps=500000, learning_rate=0.000005)
            elif model_type == 'A2C':
                model = A2C(policy, trainEnv, verbose=1, tensorboard_log=log_path)

        model.set_env(trainEnv)
        if stop_callback:
            # eval_callback = EvalCallback(trainEnv, callback_on_new_best=stop_callback, eval_freq=10000, best_model_save_path=save_dir, verbose=1)
            eval_cb = EvalCallback(make_vec_env(1), eval_freq=500)
            model.learn(total_timesteps=timestep, callback=eval_cb)
            # model.learn(total_timesteps=timestep)
        else:
            model.learn(total_timesteps=timestep)
        model.save(save_path)

    if method == 'test':
        if model_type == 'PPO':
            model = PPO.load(load_path)
        elif model_type == 'A2C':
            model = A2C.load(load_path)

    if method == 'test' or method == 'both':
        # if isinstance(vec_env_num, int):
        #     testEnv = make_vec_env(vec_env_num, render_mode='human')
        # else:
        #     testEnv = make_env(render_mode='human')

        if isinstance(vec_env_num, int):
            testEnv = make_vec_env(vec_env_num)
        else:
            testEnv = make_env()

        model.set_env(testEnv)
        testEnv.save("./env")
        # print(evaluate_policy(model, testEnv, n_eval_episodes=n_eval_episodes))

        frames = []
        env = VecNormalize.load("./env", DummyVecEnv([make_env] * 16))
        env.training = False
        env.norm_reward = False
        model = PPO.load(load_path, env=env)
        obs = env.reset()
        for _ in range(1000):
            action, _state = model.predict(obs, deterministic=True)
            obs, _reward, _done, _info = env.step(action)
            # print('aa', env.render())
            frames.append(env.render())
            # print(env.score, env.hp)
        # media.show_video(frames, fps=30, width=600)


# run(timestep=1000000, method='train', policy='CnnPolicy', vec_env_num=64, normalize=True, save_file='normalize=True,vec_env_num=64')
# run(timestep=2000000, method='train', policy='CnnPolicy', save_file='atari_params,FrameStack=4')
# run(timestep=5000000, model_type='A2C', method='train', policy='CnnPolicy', save_file='default_params')
# run(timestep=100000000, method='train', save_file='n_steps=500000,learning_rate=0.000005,enemy_num=5', enemy_num=5)
# run(method='test', policy='CnnPolicy', normalize=True, load_file='normalize=True,vec_env_num=64')
run(method='test', policy='CnnPolicy', vec_env_num=64, normalize=True, test_window_size=100, load_file='normalize=True,vec_env_num=64,learning_rate=0.0001')
# run(timestep=100000000, policy='CnnPolicy', method='test', load_file='atari_params', n_eval_episodes=5)
# play(normalize=True)
