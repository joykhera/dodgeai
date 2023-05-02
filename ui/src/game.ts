import Player from './player.js'
import Enemy from './enemy.js'
// import math

export default class DodgeGameEnv {
    // render_fps: number;
    model_window_size: number;
    window_size: number;
    player: Player;
    enemies: Enemy[] = [];
    score: number = 0;
    game_over: boolean = false;
    enemy_movement: string;
    max_enemy_num: number;
    randomize_enemy_num: boolean;
    enemy_num: number;
    enemy_speed: number;
    enemy_radius: number;
    randomize_enemy_speed: boolean;
    randomize_enemy_radius: boolean;
    max_hp: number;
    hp: number;
    death_penalty: number;
    normalize: boolean;
    clock: any = null;
    window: any = null;
    canvas: HTMLCanvasElement | null = null;
    font: string = "30px sans-serif";

    // Define colors
    BLACK: string = '#000000';
    WHITE: string = '#FFFFFF';
    RED: string = '#FF0000';

    constructor(
        window_size: number = 64,
        model_window_size: number = 64,
        enemy_movement: string = 'aimed',
        hp: number = 10,
        death_penalty: number = 20,
        enemy_num: number = 1,
        player_speed: number = 0.03,
        enemy_speed: number = 0.02,
        player_radius: number = 0.05,
        enemy_radius: number = 0.05,
        action_space: number = 4,
        normalize: boolean = true,
        randomize_player_speed: boolean = false,
        randomize_enemy_speed: boolean = false,
        randomize_player_radius: boolean = false,
        randomize_enemy_radius: boolean = false,
        randomize_enemy_num: boolean = false,
    ) {
        this.model_window_size = model_window_size;
        this.window_size = window_size;
        this.player = new Player(
            this.window_size,
            this.window_size,
            this.WHITE,
            player_radius,
            player_speed,
            action_space,
            randomize_player_radius,
            randomize_player_speed,
            normalize,
        );
        this.score = 0;
        this.game_over = false;
        this.enemy_movement = enemy_movement;
        this.max_enemy_num = enemy_num;
        this.randomize_enemy_num = randomize_enemy_num;
        this.enemy_num = this.randomize_enemy_num
            ? Math.floor(Math.random() * (this.max_enemy_num - 1) + 1)
            : this.max_enemy_num;
        this.enemy_speed = enemy_speed;
        this.enemy_radius = enemy_radius;
        this.randomize_enemy_speed = randomize_enemy_speed;
        this.randomize_enemy_radius = randomize_enemy_radius;
        this.max_hp = hp;
        this.hp = hp;
        this.death_penalty = death_penalty;
        this.normalize = normalize;
        this.canvas = document.getElementById('canvas') as HTMLCanvasElement;
        this.canvas.width = this.window_size;
        this.canvas.height = this.window_size;
        this.window = this.canvas.getContext("2d");

        for (let i = 0; i < this.enemy_num; i++) {
            this.enemies.push(
                new Enemy(
                    this.window_size,
                    this.window_size,
                    this.RED,
                    enemy_speed,
                    enemy_radius,
                    enemy_movement,
                    randomize_enemy_radius,
                    randomize_enemy_speed,
                    normalize,
                )
            );
        }

        this.reset();
    }

    getObservation() {
        return Array.from(this.window.getImageData(0, 0, this.canvas!.width, this.canvas!.height).data);
    }

    reset(): any {
        this.game_over = false;
        this.player.reset();
        this.enemies.forEach(enemy => enemy.reset());
        this.score = 0;
        this.hp = this.max_hp;

        // this.window_size = randint(64, 128);
        if (this.randomize_enemy_num) {
            this.enemy_num = Math.random() * (this.max_enemy_num - 1) + 1;
            this.enemies = [];
            // console.log(this.enemy_num);
            for (let i = 0; i < this.enemy_num; i++) {
                this.enemies.push(
                    new Enemy(
                        this.window_size,
                        this.window_size,
                        this.RED,
                        this.enemy_speed,
                        this.enemy_radius,
                        this.enemy_movement,
                        this.randomize_enemy_radius,
                        this.randomize_enemy_speed,
                        this.normalize,
                    )
                );
            }
        }

        const observation = this.getObservation()
        return observation;
    }

    isGameOver(): boolean {
        return this.enemies.some(enemy => {
            const distance = Math.sqrt(
                (this.player.pos.x - enemy.pos.x) ** 2 + (this.player.pos.y - enemy.pos.y) ** 2
            );
            return distance < this.player.radius + enemy.radius;
        }) || this.player.pos.x < 0 || this.player.pos.x > 1 || this.player.pos.y < 0 || this.player.pos.y > 1;
    }

    step(action: number): [any[], number, boolean, any] {
        if (this.game_over) {
            this.game_over = false;
        }
        this.player.aiMove(action);
        this.moveEnemies();
        if (this.player.touchWall()) {
            this.game_over = true;
        }

        const gameOver = this.isGameOver();
        this.hp -= gameOver ? 1 : 0;
        const reward = 1 + (this.game_over ? -1 * this.death_penalty : 0);
        this.score += reward;

        const observation = this.getObservation();
        const done = this.hp <= 0;
        const info = {};

        return [observation, reward, done, info];
    }

    render() {
        this.window.clearRect(0, 0, this.window_size, this.window_size);
        this.player.draw(this.window);
        this.enemies.forEach(enemy => enemy.draw(this.window));
        this.window.font = this.font;
        this.window.fillStyle = this.BLACK;
        // this.window.fillText(`Score: ${this.score}`, 10, 50);
        // this.window.fillText(`HP: ${this.hp}`, 10, 80);
    }

    moveEnemies(): void {
        for (const enemy of this.enemies) {
            enemy.move(this.player.pos);

            // Check for collisions with the player
            if (this.player.isCollidingWith(enemy)) {
                this.game_over = true;
            }
        }
    }

    run(): void {
        const loop = () => {
            const action = Math.floor(Math.random() * 4);
            const [_obs, _reward, done, _info] = this.step(action)
            // console.log(_obs.filter(e => e != 0))
            this.render()
            if (done) this.reset()
            window.requestAnimationFrame(loop);
            // console.log(this.game_over, this.hp)
        };
        window.requestAnimationFrame(loop);
    }
}