from game import DodgeGameEnv

def play(env_params, policy='CnnPolicy'):
    game = DodgeGameEnv(
        policy=policy,
        render_mode='human',
        window_size=env_params['window_size'],
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
    # game.run()
    game.reset()
    while True:
        observation, reward, terminated, _, info = game.step(game.action_space.sample())
        if terminated:
            game.reset()
