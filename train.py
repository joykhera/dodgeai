import os
from stable_baselines3 import PPO
from utils import get_different_params, make_vec_env, make_env
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnRewardThreshold
from defaultParams import default_model_hyperparams, default_env_params

stop_callback = StopTrainingOnRewardThreshold(reward_threshold=100000, verbose=1)


def train(
    env_params,
    model_hyperparams,
    load_file=None,
    save_file=None,
    policy='CnnPolicy',
    stop_callback=stop_callback,
    verbose=1,
    save=True
):

    save_dir = os.path.join('training', 'savedModels', policy)
    if save_file:
        log_path = os.path.join('training', 'logs', policy, save_file)
        save_path = os.path.join(save_dir, save_file)
    elif load_file:
        log_path = os.path.join('training', 'logs', policy, load_file)
        save_path = os.path.join(save_dir, load_file)
    elif save:
        different_params = get_different_params(default_model_hyperparams, default_env_params, model_hyperparams, env_params)
        save_file = ','.join(different_params)
        log_path = os.path.join('training', 'logs', policy, save_file)
        save_path = os.path.join(save_dir, save_file)

    if isinstance(model_hyperparams['vec_env_num'], int):
        env = make_vec_env(env_params, vec_env_num=model_hyperparams['vec_env_num'], policy=policy, render_mode='rgb_array')
    else:
        env = make_env(env_params, policy=policy, env_params=env_params)
        
    if load_file:
        load_path = os.path.join(save_dir, load_file)
        print('loading model from', load_path, '...')
        print('(os.path.isfile(load_path)', os.path.isfile(load_path))
        model = PPO.load(load_path, env=env, custom_objects={'observation_space': env.observation_space, 'action_space': env.action_space})

    if not load_file:
        model = PPO(
            env=env,
            tensorboard_log=log_path,
            policy=policy,
            learning_rate=(lambda x: x * model_hyperparams['learning_rate']) if model_hyperparams['learning_rate_lambda'] else model_hyperparams['learning_rate'],
            n_steps=model_hyperparams['n_steps'],
            batch_size=model_hyperparams['batch_size'],
            n_epochs=model_hyperparams['n_epochs'],
            gamma=model_hyperparams['gamma'],
            clip_range=model_hyperparams['clip_range'],
            ent_coef=model_hyperparams['ent_coef'],
            verbose=verbose,
        )

    model.set_env(env)
    if stop_callback:
        # eval_callback = EvalCallback(env, callback_on_new_best=stop_callback, eval_freq=10000, best_model_save_path=save_dir, verbose=1)
        eval_cb = EvalCallback(make_vec_env(env_params, vec_env_num=1, policy=policy, render_mode='rgb_array'), eval_freq=500)
        model.learn(total_timesteps=model_hyperparams['timestep'], callback=eval_cb)
    else:
        model.learn(total_timesteps=model_hyperparams['timestep'])
    model.save(save_path)
