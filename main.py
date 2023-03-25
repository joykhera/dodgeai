import gym
# import gym_examples
from gym_examples import DodgeGameEnv
import os
from stable_baselines3 import PPO, A2C
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnRewardThreshold
from mathModel import mathModel
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize, VecTransposeImage
from stable_baselines3.common.monitor import Monitor
from gymnasium.wrappers.frame_stack import FrameStack
from gymnasium.wrappers.resize_observation import ResizeObservation
import tensorboard

stop_callback = StopTrainingOnRewardThreshold(reward_threshold=100000, verbose=1)
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize, VecTransposeImage


def play(enemy_num=1, random_player_speed=False, random_enemy_speed=False, random_player_radius=False, random_enemy_radius=False, enemy_movement='aimed'):
    game = DodgeGameEnv(render_mode='human', enemy_num=enemy_num, enemy_movement=enemy_movement, random_player_speed=random_player_speed,
                        random_enemy_speed=random_enemy_speed, random_player_radius=random_player_radius, random_enemy_radius=random_enemy_radius)
    game.run()
    # game.reset()
    # while True:
    #     game.step()
    

def testMathModel(n_eval_episodes=20):
    env = DodgeGameEnv(render_mode='human', policy='MathPolicy', enemy_movement='random', enemy_num=1)
    action = mathModel(env.reset())
    terminated = False
    for i in range(n_eval_episodes):
        while not terminated:
            observation, reward, terminated, info = env.step(action)
            action = mathModel(observation)
        

def run(timestep=100000, model_type='PPO', method='both', load_file=None, save_file=None, policy='MultiInputPolicy', n_eval_episodes=20, enemy_movement='aimed', stop_callback=stop_callback, vec_env_num=None, enemy_num=1, random_player_speed=False, random_enemy_speed=False, random_player_radius=False, random_enemy_radius=False):
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

        
    if method == 'train' or method == 'both':
        def make_env():
            env = DodgeGameEnv(render_mode='rgb_array', policy=policy, enemy_movement=enemy_movement, enemy_num=enemy_num, random_player_speed=random_player_speed,
                               random_enemy_speed=random_enemy_speed, random_player_radius=random_player_radius, random_enemy_radius=random_enemy_radius)

            # env = TimeLimit(env, 300)
            # env = Monitor(env)
            # env = ResizeObservation(env, (50, 50))
            # print(env)
            # env = FrameStack(env, 4)
            return env
        
        def make_vec_env(n):
            env = VecNormalize(DummyVecEnv([make_env] * n), norm_obs=policy != 'CnnPolicy')
            return VecTransposeImage(env) if policy == 'CnnPolicy' else env
        
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
                    learning_rate=lambda x: x * 2.5e-4,
                    n_steps=128, batch_size=256,
                    n_epochs=4,
                    gamma=0.95,
                    clip_range=0.1,
                    ent_coef=0.01,
                    verbose=1
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
        testEnv = DodgeGameEnv(render_mode='human', policy=policy, enemy_movement=enemy_movement, enemy_num=enemy_num, random_player_speed=random_player_speed,
                               random_enemy_speed=random_enemy_speed, random_player_radius=random_player_radius, random_enemy_radius=random_enemy_radius)
        model.set_env(testEnv)
        print(evaluate_policy(model, testEnv, n_eval_episodes=n_eval_episodes))
        

run(timestep=2000000, method='train', policy='CnnPolicy', vec_env_num=64, save_file='atari_params,eval_cb,hp=10')
# run(timestep=2000000, method='train', policy='CnnPolicy', save_file='atari_params,FrameStack=4')
# run(timestep=5000000, model_type='A2C', method='train', policy='CnnPolicy', save_file='default_params')
# run(timestep=100000000, method='train', save_file='n_steps=500000,learning_rate=0.000005,enemy_num=5', enemy_num=5)
# run(timestep=100000000, method='test', load_file='n_steps=500000,learning_rate=0.000005')
# run(timestep=100000000, policy='CnnPolicy', method='test', load_file='atari_params', n_eval_episodes=5)
# testMathModel()
# play()
