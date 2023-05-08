from gym_examples import DodgeGameEnv
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize, VecTransposeImage


def get_different_params(default_model_hyperparams, default_env_params, model_hyperparams, env_params):
    different_params = []
    for key in model_hyperparams.keys():
        if default_model_hyperparams[key] != model_hyperparams[key]:
            different_params.append('{}={}'.format(key, model_hyperparams[key]))
    for key in env_params.keys():
        if default_env_params[key] != env_params[key]:
            different_params.append('{}={}'.format(key, env_params[key]))
    # print(default_model_hyperparams, default_env_params, model_hyperparams, env_params, different_params)
    return different_params


def make_env(env_params, policy='CnnPolicy', render_mode='rgb_array', window_size=None):
    env = DodgeGameEnv(
        render_mode=render_mode,
        policy=policy,
        window_size=window_size or env_params['window_size'],
        model_window_size=env_params['model_window_size'],
        hp=env_params['hp'],
        death_penalty=env_params['death_penalty'],
        enemy_movement=env_params['enemy_movement'],
        enemy_num=env_params['enemy_num'],
        normalize=env_params['normalize'],
        player_speed=env_params['player_speed'],
        enemy_speed=env_params['enemy_speed'],
        player_radius=env_params['player_radius'],
        enemy_radius=env_params['enemy_radius'],
        action_space=env_params['action_space'],
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
    window_size=None
):
    # print(env_params, render_mode, policy, vec_env_num)
    env = VecNormalize(
        DummyVecEnv([lambda: make_env(env_params, render_mode=render_mode, policy=policy, window_size=window_size)] * vec_env_num), norm_obs=policy != 'CnnPolicy')
    # return VecTransposeImage(env) if policy == 'CnnPolicy' else env
    return env
