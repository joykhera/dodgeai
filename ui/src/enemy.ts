interface Position {
    x: number;
    y: number;
}

interface EnemyState {
    x: number;
    y: number;
    dx?: number;
    dy?: number;
    radius?: number;
    speed?: number;
}

type enemyMovement = 'aimed' | 'aimed_bounce' | 'random'

export default class Enemy {
    pos: Position
    color: string;
    max_speed: number;
    max_radius: number;
    radius: number;
    speed: number;
    randomize_radius: boolean;
    randomize_speed: boolean;
    dx: number;
    dy: number;
    direction: number;
    enemy_movement: enemyMovement
    reached: boolean;
    window_width: number;
    window_height: number;
    private readonly game_width: number;
    private readonly game_height: number;
    private readonly normalize: boolean;

    constructor(
        window_width: number,
        window_height: number,
        color: string = 'rgb(255, 0, 0)',
        max_speed: number = 5,
        max_radius: number = 50,
        enemy_movement: enemyMovement = 'aimed',
        randomize_radius: boolean = false,
        randomize_speed: boolean = false,
        normalize: boolean = true,
    ) {
        this.window_width = window_width;
        this.window_height = window_height;
        this.game_width = normalize ? 1 : window_width;
        this.game_height = normalize ? 1 : window_height;
        this.normalize = normalize;
        this.color = color;
        this.max_radius = max_radius;
        this.max_speed = max_speed;
        this.randomize_radius = randomize_radius
        this.randomize_speed = randomize_speed
        this.radius = randomize_radius ? Math.random() * max_radius : max_radius;
        this.speed = randomize_speed ? Math.random() * max_speed : max_speed;
        this.direction = [Math.random() * 80 + 5, Math.random() * 80 + 95, Math.random() * 80 + 185, Math.random() * 275 + 5][Math.floor(Math.random() * 4)]
        this.enemy_movement = enemy_movement;
        this.reset();
        this.reached = false;
        this.pos = {
            x: Math.floor(Math.random() * (this.game_width + 1)),
            y: Math.floor(Math.random() * (this.game_height + 1))
        };
        this.dx = 0;
        this.dy = 0;
    }

    draw(canvas: HTMLCanvasElement, ctx: CanvasRenderingContext2D) {
        let x = this.normalize ? this.pos.x * canvas.width : this.pos.x;
        let y = this.normalize ? this.pos.y * canvas.height : this.pos.y;
        let r = this.normalize ? this.radius * Math.min(canvas.width, canvas.height) : this.radius;

        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2, true);
        ctx.fillStyle = this.color;
        ctx.fill();
        ctx.closePath()
    }

    reset(playerCoords: Position | null = null) {
        // this.pos = {
        //             x: 0,
        //             y: 0
        //         };

        const side = Math.floor(Math.random() * 4) + 1;

        switch (side) {
            case 1:
                this.pos = {
                    x: Math.random() * this.game_width,
                    y: 0
                };
                break
            case 2:
                this.pos = {
                    x: this.game_width,
                    y: Math.random() * this.game_height
                };
                break
            case 3:
                this.pos = {
                    x: Math.random() * this.game_width,
                    y: this.game_height
                };
                break
            case 4:
                this.pos = {
                    x: 0,
                    y: Math.random() * this.game_height
                };
                break
        }

        if ((this.enemy_movement === 'aimed' || this.enemy_movement === 'aimed_bounce') && playerCoords) {
            const dist_to_target = Math.sqrt((this.pos.x - playerCoords.x) ** 2 + (this.pos.y - playerCoords.y) ** 2);
            this.dx = this.speed * (playerCoords.x - this.pos.x) / dist_to_target;
            this.dy = this.speed * (playerCoords.y - this.pos.y) / dist_to_target;
        } else {
            this.direction = Math.random() * 360;
            this.dx = this.speed * Math.cos(this.direction * Math.PI / 180); // randomBetween(-this.speed, this.speed)
            this.dy = this.speed * Math.sin(this.direction * Math.PI / 180); // randomBetween(-this.speed, this.speed)
        }

        if (this.randomize_radius) {
            this.radius = Math.random() * (this.max_radius - 0.02) + 0.02;
        }

        if (this.randomize_speed) {
            this.speed = Math.random() * (this.max_speed - 0.005) + 0.005;
        }
    }

    public move(playerCoords?: Position): void {
        if (this.enemy_movement === 'aimed' || this.enemy_movement === 'aimed_bounce') {
            const new_x = this.pos.x + this.dx;
            const new_y = this.pos.y + this.dy;

            if (new_x < 0 || new_y < 0 || new_x > this.game_width || new_y > this.game_height) {
                this.reached = true;
                if (this.enemy_movement === 'aimed') {
                    this.reset(playerCoords);
                } else if (this.enemy_movement === 'aimed_bounce') {
                    const dist_to_target = Math.sqrt(Math.pow((this.pos.x - playerCoords!.x), 2) + Math.pow((this.pos.y - playerCoords!.y), 2));
                    const randomness = this.speed * 0.1;
                    this.dx = this.speed * (playerCoords!.x - this.pos.x) / dist_to_target + Math.random() * (randomness * 2) - randomness;
                    this.dy = this.speed * (playerCoords!.y - this.pos.y) / dist_to_target + Math.random() * (randomness * 2) - randomness;
                }
            } else {
                if (this.reached) {
                    this.reached = false;
                }
                this.pos.x = new_x;
                this.pos.y = new_y;
            }
        } else {
            const randomness = this.speed * 0.1;
            const new_x = this.pos.x + this.dx;
            const new_y = this.pos.y + this.dy;

            if (new_x < this.radius || new_x > this.game_width - this.radius) {
                if (new_x < this.radius) {
                    this.pos.x = this.radius;
                } else {
                    this.pos.x = this.game_width - this.radius;
                }
                this.dx *= -1 + Math.random() * (randomness * 2) - randomness;
            } else {
                this.pos.x = new_x;
            }

            if (new_y < this.radius || new_y > this.game_height - this.radius) {
                if (new_y < this.radius) {
                    this.pos.y = this.radius;
                } else {
                    this.pos.y = this.game_height - this.radius;
                }
                this.dy *= -1 + Math.random() * (randomness * 2) - randomness;
            } else {
                this.pos.y = new_y;
            }
        }

        this.pos.x = this.pos.x;
        this.pos.y = this.pos.y;
        // console.log(this.pos.x, this.pos.y, this.pos)
    }

    getEnemyState(player?: EnemyState, direction = true, radius = false, speed = false): EnemyState {
        let Enemystate: EnemyState = player ? { x: player.x - this.pos.x, y: player.y - this.pos.y } : { x: this.pos.x, y: this.pos.y };

        if (direction) {
            Enemystate.dx = this.dx;
            Enemystate.dy = this.dy;
        }

        if (radius) {
            Enemystate.radius = this.radius;
        }

        if (speed) {
            Enemystate.speed = this.speed;
        }

        return Enemystate;
    }

}
