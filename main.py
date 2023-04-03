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
import mediapy as media
import tensorboard

stop_callback = StopTrainingOnRewardThreshold(reward_threshold=100000, verbose=1)


def play(random_player_speed=False, random_enemy_speed=False, random_player_radius=False, random_enemy_radius=False, enemy_movement='aimed', normalize=True, max_enemy_num=1, random_enemy_num=False):
    game = DodgeGameEnv(render_mode='human', max_enemy_num=max_enemy_num, random_enemy_num=random_enemy_num, enemy_movement=enemy_movement, normalize=normalize, random_player_speed=random_player_speed,
                        random_enemy_speed=random_enemy_speed, random_player_radius=random_player_radius, random_enemy_radius=random_enemy_radius)
    # game.run()
    game.reset()
    while True:
        observation, reward, terminated, _, info = game.step(game.action_space.sample())
        if terminated:
            game.reset()


def run(timestep=100000,
        method='both',
        load_file=None,
        save_file=None,
        policy='MultiInputPolicy',
        enemy_movement='aimed',
        normalize=True,
        stop_callback=stop_callback,
        vec_env_num=64,
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
        max_enemy_num=1,
        player_speed=0.03,
        enemy_speed=0.02,
        player_radius=0.05,
        enemy_radius=0.05,
        random_player_speed=False,
        random_enemy_speed=False,
        random_player_radius=False,
        random_enemy_radius=False,
        random_enemy_num=False,
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
        model = PPO.load(load_path)

    def make_env(render_mode='rgb_array'):
        window_size = train_window_size if render_mode == 'rgb_array' else test_window_size
        env = DodgeGameEnv(render_mode=render_mode, policy=policy, window_size=window_size, enemy_movement=enemy_movement, max_enemy_num=max_enemy_num, normalize=normalize, player_speed=player_speed,
                           enemy_speed=enemy_speed, player_radius=player_radius, enemy_radius=enemy_radius, random_player_speed=random_player_speed, random_enemy_speed=random_enemy_speed, random_player_radius=random_player_radius, random_enemy_radius=random_enemy_radius, random_enemy_num=random_enemy_num)
        # env = DodgeGameEnv(render_mode, policy, window_size, enemy_movement, max_enemy_num, normalize, player_speed, enemy_speed, player_radius, enemy_radius, random_player_speed, random_enemy_speed, random_player_radius, random_enemy_radius, random_enemy_num)

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
            model = PPO(
                env=trainEnv,
                tensorboard_log=log_path,
                policy=policy,
                learning_rate=learning_rate,
                # learning_rate=lambda x: x * 0.0001,
                n_steps=n_steps,
                batch_size=batch_size,
                n_epochs=n_epochs,
                gamma=gamma,
                clip_range=clip_range,
                ent_coef=ent_coef,
                verbose=verbose,
            )

        model.set_env(trainEnv)
        if stop_callback:
            # eval_callback = EvalCallback(trainEnv, callback_on_new_best=stop_callback, eval_freq=10000, best_model_save_path=save_dir, verbose=1)
            eval_cb = EvalCallback(make_vec_env(1), eval_freq=500)
            model.learn(total_timesteps=timestep, callback=eval_cb)
            # model.learn(total_timesteps=timestep)
        else:
            model.learn(total_timesteps=timestep)
        model.save(save_path)

    if method == 'test' or method == 'both':
        if isinstance(vec_env_num, int):
            testEnv = make_vec_env(vec_env_num, render_mode='human')
            # testEnv = make_vec_env(vec_env_num)
            testEnv.save("./env")
            frames = []
            env = VecNormalize.load("./env", DummyVecEnv([make_env] * vec_env_num))
            env.training = False
            env.norm_reward = False
            model = PPO.load(load_path, env=env)
            obs = env.reset()
            while True:
                action, _state = model.predict(obs, deterministic=True)
                obs, _reward, _done, _info = env.step(action)
                frames.append(env.render())
                # media.show_video(frames, fps=30, width=600)
        else:
            testEnv = make_env(render_mode='human')
            model = PPO.load(load_path, testEnv)
            obs = testEnv.reset()
            while True:
                action, _state = model.predict(obs, deterministic=True)
                # print(obs.shape, action)
                obs, _reward, _done, _, _info = testEnv.step(action)
                if _done:
                    testEnv.reset()


# add funtionality to to make save_file name in function
run(timestep=5000000, method='train', policy='CnnPolicy', learning_rate=0.00005, max_enemy_num=5, random_enemy_num=True, enemy_speed=0.01, save_file='learning_rate=0.00005,max_enemy_num=5,random_enemy_num=True,enemy_speed=0.01')
# run(timestep=2000000, method='train', policy='CnnPolicy', save_file='atari_params,FrameStack=4')
# run(timestep=100000000, method='train', save_file='n_steps=500000,learning_rate=0.000005,enemy_num=5', enemy_num=5)
# run(method='test', policy='CnnPolicy', vec_env_num=16, load_file='vec_env_num=64,normalize=True,batch_size=1024')
# run(method='test', policy='CnnPolicy', vec_env_num=16, enemy_num=5, load_file='vec_env_num=64,learning_rate=0.00005,enemy_num=5')
# run(method='test', policy='CnnPolicy', vec_env_num=16,
#     enemy_num=5, enemy_speed=0.01, load_file='vec_env_num=64,learning_rate=0.00005,enemy_num=5,enemy_speed=0.01')
# play(max_enemy_num=5, random_enemy_num=True)
