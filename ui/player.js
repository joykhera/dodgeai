"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
Object.defineProperty(exports, "__esModule", { value: true });
var Player = /** @class */ (function () {
    function Player(windowWidth, windowHeight, color, maxRadius, maxSpeed, actionSpace, randomizeRadius, randomizeSpeed, normalize) {
        if (maxRadius === void 0) { maxRadius = 10; }
        if (maxSpeed === void 0) { maxSpeed = 10; }
        if (actionSpace === void 0) { actionSpace = 4; }
        if (randomizeRadius === void 0) { randomizeRadius = false; }
        if (randomizeSpeed === void 0) { randomizeSpeed = false; }
        if (normalize === void 0) { normalize = true; }
        this.windowWidth = windowWidth;
        this.windowHeight = windowHeight;
        this.gameWidth = normalize ? 1 : windowWidth;
        this.gameHeight = normalize ? 1 : windowHeight;
        this.normalize = normalize;
        this.initPos = {
            x: this.gameWidth / 2,
            y: this.gameHeight / 2,
        };
        this.pos = __assign({}, this.initPos);
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
    Player.prototype.draw = function (ctx) {
        var _a = this, pos = _a.pos, radius = _a.radius, windowWidth = _a.windowWidth, windowHeight = _a.windowHeight;
        if (this.normalize) {
            var cx = pos.x * windowWidth;
            var cy = pos.y * windowHeight;
            var r = radius * windowWidth;
            ctx.beginPath();
            ctx.arc(cx, cy, r, 0, Math.PI * 2);
            ctx.fillStyle = this.color;
            ctx.fill();
        }
        else {
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);
            ctx.fillStyle = this.color;
            ctx.fill();
        }
    };
    Player.prototype.aiMove = function (move) {
        if (typeof move === 'number') {
            if (this.actionSpace === 4) {
                if (move === 0) {
                    this.pos.x -= this.speed;
                }
                else if (move === 1) {
                    this.pos.x += this.speed;
                }
                else if (move === 2) {
                    this.pos.y -= this.speed;
                }
                else if (move === 3) {
                    this.pos.y += this.speed;
                }
            }
            else if (this.actionSpace === 5) {
                if (move === 0) {
                    return;
                }
                else if (move === 1) {
                    this.pos.x -= this.speed;
                }
                else if (move === 2) {
                    this.pos.x += this.speed;
                }
                else if (move === 3) {
                    this.pos.y -= this.speed;
                }
                else if (move === 4) {
                    this.pos.y += this.speed;
                }
            }
        }
        else {
            var x = move[0], y = move[1];
            this.pos.x += x * this.speed;
            this.pos.y += y * this.speed;
        }
    };
    Player.prototype.isCollidingWith = function (other) {
        var dx = this.pos.x - other.pos.x;
        var dy = this.pos.y - other.pos.y;
        var distance = Math.sqrt(dx * dx + dy * dy);
        return distance < this.radius + other.radius;
    };
    Player.prototype.touchWall = function () {
        return (this.pos.x - this.radius < 0 ||
            this.pos.x + this.radius > this.gameWidth ||
            this.pos.y - this.radius < 0 ||
            this.pos.y + this.radius > this.gameHeight);
    };
    Player.prototype.reset = function () {
        this.pos = __assign({}, this.initPos);
        this.lastPositions = [];
        if (this.randomizeSpeed) {
            this.speed = Math.random() * this.maxSpeed + 1;
        }
        if (this.randomizeRadius) {
            this.radius = Math.random() * this.maxRadius + 1;
        }
    };
    Player.prototype.getState = function (radius, speed) {
        var state = {
            position: { x: this.pos.x, y: this.pos.y },
        };
        if (radius) {
            state.radius = this.radius;
        }
        if (speed) {
            state.speed = this.speed;
        }
        return state;
    };
    Player.prototype.getWalls = function () {
        return [this.pos.x - this.radius, this.gameWidth - this.radius - this.pos.x, this.pos.y - this.radius, this.gameHeight - this.radius - this.pos.y];
    };
    return Player;
}());
exports.default = Player;
