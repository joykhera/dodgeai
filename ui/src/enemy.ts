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

export default class Enemy {
    x: number;
    y: number;
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
    enemy_movement: string; // 'aimed' | 'aimed_bounce' | 'random';
    reached: boolean;
    pos: Position;

    private readonly window_width: number;
    private readonly window_height: number;
    private readonly game_width: number;
    private readonly game_height: number;
    private readonly normalize: boolean;

    constructor(
        window_width: number,
        window_height: number,
        color: string = 'rgb(255, 0, 0)',
        max_speed: number = 5,
        max_radius: number = 50,
        enemy_movement: string, //'aimed' | 'aimed_bounce' | 'random' = 'aimed',
        randomize_radius: boolean = false,
        randomize_speed: boolean = false,
        normalize: boolean = true,
    ) {
        this.window_width = window_width;
        this.window_height = window_height;
        this.game_width = normalize ? 1 : window_width;
        this.game_height = normalize ? 1 : window_height;
        this.normalize = normalize;
        this.x = Math.floor(Math.random() * (this.game_width + 1));
        this.y = Math.floor(Math.random() * (this.game_height + 1));
        this.color = color;
        this.max_radius = max_radius;
        this.max_speed = max_speed;
        this.randomize_radius = randomize_radius
        this.randomize_speed = randomize_speed
        this.radius = randomize_radius ? Math.random() * max_radius : max_radius;
        this.speed = randomize_speed ? Math.random() * max_speed : max_speed;
        this.direction = [5, 85, 95, 175, 185, 265, 275, 355][Math.floor(Math.random() * 4)];
        this.enemy_movement = enemy_movement;
        this.reset();
        this.reached = false;
        this.pos = { 'x': this.x, 'y': this.y };
        this.dx = 0;
        this.dy = 0;
    }

    draw(ctx: CanvasRenderingContext2D): void {
        let x = this.normalize ? this.x * this.window_width : this.x;
        let y = this.normalize ? this.y * this.window_height : this.y;
        let r = this.normalize ? this.radius * this.window_width : this.radius;
    
        // ctx.globalAlpha = 1

        // ctx.beginPath();
        // ctx.moveTo(x, y - r);
        // ctx.lineTo(x - r, y);
        // ctx.lineTo(x, y + r);
        // ctx.lineTo(x + r, y);
        // ctx.fillStyle = this.color;
        // ctx.fill();

        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2, true);
        ctx.fillStyle = this.color;
        ctx.fill();
        ctx.closePath()
        // ctx.imageSmoothingEnabled = false;
        // ctx.drawImage((document.getElementById('canvas') as HTMLCanvasElement), 0, 0, 64, 64, 0, 0, 64, 64);

        // for (var y = 0; y < 64; y++) {
        //     for (var x = 0; x < 64; x++) {
        //         var dx = x - cx;
        //         var dy = y - cy;
        //         var distance = Math.sqrt(dx * dx + dy * dy);
        //         // var dx = Math.abs(x - cx);
        //         // var dy = Math.abs(y - cy);
        //         // var distance = dx / (r/3) + dy / (r/3);

        //         if (distance <= r) {
        //             ctx.fillStyle = 'red';
        //             ctx.fillRect(x, y, 1, 1);
        //         }
        //         // else {
        //         //     ctx.fillStyle = 'black';
        //         // }

        //         // ctx.fillRect(x, y, 1, 1);
        //     }
        // }

        // r = Math.floor(r);
        // x = Math.floor(x);
        // y = Math.floor(y);

        // for (let tx = x - r; tx <= x + r; tx++) {
        //     for (let ty = y - r; ty <= y + r; ty++) {
        //         if ((tx - x) ** 2 + (ty - y) ** 2 <= r ** 2) {
        //             ctx.fillStyle = this.color;
        //             ctx.fillRect(tx, ty, 1, 1);
        //         }
        //     }
        // }
    }

    reset(playerCoords: Position | null = null) {
        // this.x = 0
        // this.y = 0
        const side = Math.floor(Math.random() * 4) + 1;

        if (side === 1) {
            // top
            this.x = Math.random() * this.game_width;
            this.y = 0;
        } else if (side === 2) {
            // right
            this.x = this.game_width;
            this.y = Math.random() * this.game_height;
        } else if (side === 3) {
            // bottom
            this.x = Math.random() * this.game_width;
            this.y = this.game_height;
        } else {
            // left
            this.x = 0;
            this.y = Math.random() * this.game_height;
        }

        if ((this.enemy_movement === 'aimed' || this.enemy_movement === 'aimed_bounce') && playerCoords) {
            const dist_to_target = Math.sqrt((this.x - playerCoords.x) ** 2 + (this.y - playerCoords.y) ** 2);
            this.dx = this.speed * (playerCoords.x - this.x) / dist_to_target;
            this.dy = this.speed * (playerCoords.y - this.y) / dist_to_target;
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
            // console.log(this.dx, this.dy)
            const new_x = this.x + this.dx;
            const new_y = this.y + this.dy;

            if (new_x < 0 || new_y < 0 || new_x > this.game_width || new_y > this.game_height) {
                this.reached = true;
                if (this.enemy_movement === 'aimed') {
                    this.reset(playerCoords);
                } else if (this.enemy_movement === 'aimed_bounce') {
                    const dist_to_target = Math.sqrt(Math.pow((this.x - playerCoords!.x), 2) + Math.pow((this.y - playerCoords!.y), 2));
                    const randomness = this.speed * 0.1;
                    this.dx = this.speed * (playerCoords!.x - this.x) / dist_to_target + Math.random() * (randomness * 2) - randomness;
                    this.dy = this.speed * (playerCoords!.y - this.y) / dist_to_target + Math.random() * (randomness * 2) - randomness;
                }
            } else {
                if (this.reached) {
                    this.reached = false;
                }
                this.x = new_x;
                this.y = new_y;
            }
        } else {
            const randomness = this.speed * 0.1;
            const new_x = this.x + this.dx;
            const new_y = this.y + this.dy;

            if (new_x < this.radius || new_x > this.game_width - this.radius) {
                if (new_x < this.radius) {
                    this.x = this.radius;
                } else {
                    this.x = this.game_width - this.radius;
                }
                this.dx *= -1 + Math.random() * (randomness * 2) - randomness;
            } else {
                this.x = new_x;
            }

            if (new_y < this.radius || new_y > this.game_height - this.radius) {
                if (new_y < this.radius) {
                    this.y = this.radius;
                } else {
                    this.y = this.game_height - this.radius;
                }
                this.dy *= -1 + Math.random() * (randomness * 2) - randomness;
            } else {
                this.y = new_y;
            }
        }

        this.pos.x = this.x;
        this.pos.y = this.y;
        // console.log(this.x, this.y, this.pos)
    }

    getEnemyState(player?: EnemyState, direction = true, radius = false, speed = false): EnemyState {
        let Enemystate: EnemyState = player ? { x: player.x - this.x, y: player.y - this.y } : { x: this.x, y: this.y };

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
