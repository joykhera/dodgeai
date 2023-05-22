import Player from './player.js'
import Enemy from './enemy.js'

type enemyMovement = 'aimed' | 'aimed_bounce' | 'random'


export default class DodgeGameEnv {
    // render_fps: number;
    model_window_size: number;
    window_size: number;
    player: Player;
    enemies: Enemy[] = [];
    score: number = 0;
    game_over: boolean = false;
    enemy_movement: enemyMovement;
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
    clock: any = null;
    modelCanvas: HTMLCanvasElement;
    canvas: HTMLCanvasElement;
    modelCtx: any = null;
    ctx: any = null;
    font: string = "30px sans-serif";

    // Define colors
    BLACK: string = '#000000';
    WHITE: string = '#FFFFFF';
    RED: string = '#FF0000';

    constructor(
        model_window_size: number = 50,
        window_size: number = model_window_size * 10,
        enemy_movement: enemyMovement = 'aimed',
        hp: number = 10,
        death_penalty: number = 20,
        enemy_num: number = 1,
        player_speed: number = 0.03,
        enemy_speed: number = 0.02,
        player_radius: number = 0.02,
        enemy_radius: number = 0.02,
        action_space: number = 5,
        randomize_player_speed: boolean = false,
        randomize_enemy_speed: boolean = false,
        randomize_player_radius: boolean = false,
        randomize_enemy_radius: boolean = false,
        randomize_enemy_num: boolean = false,
    ) {
        this.model_window_size = model_window_size;
        this.window_size = window_size;
        this.player = new Player(
            this.model_window_size,
            this.model_window_size,
            this.WHITE,
            player_radius,
            player_speed,
            action_space,
            randomize_player_radius,
            randomize_player_speed,
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
        this.modelCanvas = document.getElementById('modelCanvas') as HTMLCanvasElement;
        this.modelCanvas.width = this.model_window_size;
        this.modelCanvas.height = this.model_window_size;
        this.modelCtx = this.modelCanvas.getContext("2d");
        this.canvas = document.getElementById('canvas') as HTMLCanvasElement;
        this.canvas.width = this.window_size
        this.canvas.height = this.window_size
        this.ctx = this.canvas.getContext("2d");

        this.addEnemies()
        this.reset();

        document.getElementById('enemyNumSlider')?.addEventListener('input', (e) => {
            this.enemy_num = (e.target as HTMLInputElement).valueAsNumber
            this.addEnemies()
        })
        document.getElementById('enemySpeedSlider')?.addEventListener('input', (e) => {
            this.enemy_speed = (e.target as HTMLInputElement).valueAsNumber / 100
            this.addEnemies()
        })
        document.getElementById('enemySizeSlider')?.addEventListener('input', (e) => {
            this.enemy_radius = (e.target as HTMLInputElement).valueAsNumber / 100
            this.addEnemies()
        })
    }

    getObservation() {
        const rgbaData = Array.from<number>(this.modelCtx.getImageData(0, 0, this.modelCanvas.width, this.modelCanvas.height).data)
        const rgbData: number[] = [];
        for (let i = 0; i < rgbaData.length; i += 4) {
            rgbData.push(rgbaData[i], rgbaData[i + 1], rgbaData[i + 2]);
        }

        const rearrangedArray = [];
        for (var rgb = 0; rgb < 3; rgb++) {
            for (var row = 0; row < this.model_window_size; row++) {
                for (var col = 0; col < this.model_window_size; col++) {
                    var index = row * this.model_window_size + col;
                    var rgbIndex = index * 3 + rgb;
                    rearrangedArray.push(rgbData[rgbIndex]);
                }
            }
        }

        return rearrangedArray
    }

    reset(): any {
        this.game_over = false;
        this.player.reset();
        this.enemies.forEach(enemy => enemy.reset());
        this.score = 0;
        this.hp = this.max_hp;

        if (this.randomize_enemy_num) {
            this.enemy_num = Math.random() * (this.max_enemy_num - 1) + 1;
            this.enemies = [];

            for (let i = 0; i < this.enemy_num; i++) {
                this.enemies.push(
                    new Enemy(
                        this.model_window_size,
                        this.model_window_size,
                        this.RED,
                        this.enemy_speed,
                        this.enemy_radius,
                        this.enemy_movement,
                        this.randomize_enemy_radius,
                        this.randomize_enemy_speed,
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
        this.modelCtx.fillStyle = "black";
        this.modelCtx.fillRect(0, 0, this.modelCanvas.width, this.modelCanvas.height);
        this.player.draw(this.modelCanvas, this.modelCtx);
        this.enemies.forEach(enemy => enemy.draw(this.modelCanvas, this.modelCtx));
        this.modelCtx.font = this.font;
        this.modelCtx.fillStyle = this.BLACK;

        this.ctx.fillStyle = "black";
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        this.player.draw(this.canvas, this.ctx);
        this.enemies.forEach(enemy => enemy.draw(this.canvas, this.ctx));
        this.ctx.font = this.font;
        this.ctx.fillStyle = this.BLACK;


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

    addEnemies(): void {
        this.enemies = [];
        for (let i = 0; i < this.enemy_num; i++) {
            this.enemies.push(
                new Enemy(
                    this.model_window_size,
                    this.model_window_size,
                    this.RED,
                    this.enemy_speed,
                    this.enemy_radius,
                    this.enemy_movement,
                    this.randomize_enemy_radius,
                    this.randomize_enemy_speed
                )
            );
        }
        this.reset()
    }

    run(): void {
        const loop = () => {
            const action = Math.floor(Math.random() * 4);
            const [_obs, _reward, done, _info] = this.step(action)
            this.render()
            if (done) this.reset()
            window.requestAnimationFrame(loop);
        };
        window.requestAnimationFrame(loop);
    }
}