import Enemy from './enemy.js'

interface Position {
    x: number;
    y: number;
}

interface PlayerState {
    position: {
        x: number;
        y: number;
    };
    radius?: number;
    speed?: number;
}

export default class Player {
    windowWidth: number;
    windowHeight: number;
    gameWidth: number;
    gameHeight: number;
    normalize: boolean;
    initPos: Position;
    pos: Position;
    color: string;
    randomizeSpeed: boolean;
    randomizeRadius: boolean;
    maxRadius: number;
    maxSpeed: number;
    radius: number;
    speed: number;
    lastPositions: Position[];
    actionSpace: number;

    constructor(
        windowWidth: number,
        windowHeight: number,
        color: string,
        maxRadius: number = 10,
        maxSpeed: number = 10,
        actionSpace: number = 4,
        randomizeRadius: boolean = false,
        randomizeSpeed: boolean = false,
        normalize: boolean = true,
    ) {
        this.windowWidth = windowWidth;
        this.windowHeight = windowHeight;
        this.gameWidth = normalize ? 1 : windowWidth;
        this.gameHeight = normalize ? 1 : windowHeight;
        this.normalize = normalize;
        this.initPos = {
            x: this.gameWidth / 2,
            y: this.gameHeight / 2,
        };
        this.pos = { ...this.initPos };
        this.color = color;
        this.randomizeSpeed = randomizeSpeed;
        this.randomizeRadius = randomizeRadius;
        this.maxRadius = maxRadius;
        this.maxSpeed = maxSpeed;
        this.radius = randomizeRadius ? Math.random() * maxRadius + 1 : maxRadius;
        this.speed = randomizeSpeed ? Math.random() * maxSpeed + 1 : maxSpeed;
        this.lastPositions = [];
        this.actionSpace = actionSpace;
    }


    public draw(canvas: HTMLCanvasElement, ctx: CanvasRenderingContext2D) {
        let x = this.normalize ? this.pos.x * canvas.width : this.pos.x;
        let y = this.normalize ? this.pos.y * canvas.height : this.pos.y;
        let r = this.normalize ? this.radius * Math.min(canvas.width, canvas.height) : this.radius;
        
        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.fillStyle = this.color;
        ctx.fill();
        ctx.closePath()
    }

    public aiMove(move: number | [number, number]) {
        if (typeof move === 'number') {
            if (this.actionSpace === 4) {
                if (move === 0) {
                    this.pos.x -= this.speed;
                } else if (move === 1) {
                    this.pos.x += this.speed;
                } else if (move === 2) {
                    this.pos.y -= this.speed;
                } else if (move === 3) {
                    this.pos.y += this.speed;
                }
            } else if (this.actionSpace === 5) {
                if (move === 0) {
                    return;
                } else if (move === 1) {
                    this.pos.x -= this.speed;
                } else if (move === 2) {
                    this.pos.x += this.speed;
                } else if (move === 3) {
                    this.pos.y -= this.speed;
                } else if (move === 4) {
                    this.pos.y += this.speed;
                }
            }
        } else {
            const [x, y] = move;
            this.pos.x += x * this.speed;
            this.pos.y += y * this.speed;
        }
    }

    public isCollidingWith(other: Enemy) {
        const dx = this.pos.x - other.pos.x;
        const dy = this.pos.y - other.pos.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        return distance < this.radius + other.radius;
    }

    public touchWall() {
        return (
            this.pos.x - this.radius < 0 ||
            this.pos.x + this.radius > this.gameWidth ||
            this.pos.y - this.radius < 0 ||
            this.pos.y + this.radius > this.gameHeight
        );
    }

    public reset() {
        this.pos = { ...this.initPos };
        this.lastPositions = [];
        if (this.randomizeSpeed) {
            this.speed = Math.random() * this.maxSpeed + 1;
        }
        if (this.randomizeRadius) {
            this.radius = Math.random() * this.maxRadius + 1;
        }
    }

    public getState(radius?: boolean, speed?: boolean): PlayerState {
        const state: PlayerState = {
            position: { x: this.pos.x, y: this.pos.y },
        };

        if (radius) {
            state.radius = this.radius;
        }

        if (speed) {
            state.speed = this.speed;
        }

        return state;
    }

    public getWalls(): [number, number, number, number] {
        return [this.pos.x - this.radius, this.gameWidth - this.radius - this.pos.x, this.pos.y - this.radius, this.gameHeight - this.radius - this.pos.y];
    }
}