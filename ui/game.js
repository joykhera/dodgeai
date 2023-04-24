"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var player_1 = require("./player");
var enemy_1 = require("./enemy");
// import math
var DodgeGameEnv = /** @class */ (function () {
    function DodgeGameEnv(_a) {
        var _b = _a.render_mode, render_mode = _b === void 0 ? null : _b, _c = _a.window_size, window_size = _c === void 0 ? 64 : _c, _d = _a.model_window_size, model_window_size = _d === void 0 ? 64 : _d, _e = _a.enemy_movement, enemy_movement = _e === void 0 ? 'aimed' : _e, _f = _a.hp, hp = _f === void 0 ? 10 : _f, _g = _a.death_penalty, death_penalty = _g === void 0 ? 20 : _g, _h = _a.enemy_num, enemy_num = _h === void 0 ? 1 : _h, _j = _a.player_speed, player_speed = _j === void 0 ? 0.03 : _j, _k = _a.enemy_speed, enemy_speed = _k === void 0 ? 0.02 : _k, _l = _a.player_radius, player_radius = _l === void 0 ? 0.05 : _l, _m = _a.enemy_radius, enemy_radius = _m === void 0 ? 0.05 : _m, _o = _a.action_space, action_space = _o === void 0 ? 4 : _o, _p = _a.normalize, normalize = _p === void 0 ? true : _p, _q = _a.randomize_player_speed, randomize_player_speed = _q === void 0 ? false : _q, _r = _a.randomize_enemy_speed, randomize_enemy_speed = _r === void 0 ? false : _r, _s = _a.randomize_player_radius, randomize_player_radius = _s === void 0 ? false : _s, _t = _a.randomize_enemy_radius, randomize_enemy_radius = _t === void 0 ? false : _t, _u = _a.randomize_enemy_num, randomize_enemy_num = _u === void 0 ? false : _u;
        this.metadata = {
            render_modes: ['human', 'rgb_array'],
            render_fps: 30,
        };
        this.enemies = [];
        this.score = 0;
        this.game_over = false;
        this.clock = null;
        this.window = null;
        this.canvas = null;
        this.font = "30px sans-serif";
        // Define colors
        this.BLACK = '#000000';
        this.WHITE = '#FFFFFF';
        this.RED = '#FF0000';
        this.model_window_size = model_window_size;
        this.window_size = window_size;
        this.player = new player_1.default(this.window_size, this.window_size, this.WHITE, player_radius, player_speed, action_space, randomize_player_radius, randomize_player_speed, normalize);
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
        this.canvas = document.getElementById('canvas');
        this.canvas.width = this.window_size;
        this.canvas.height = this.window_size;
        this.window = this.canvas.getContext("2d");
        for (var i = 0; i < this.enemy_num; i++) {
            this.enemies.push(new enemy_1.default(this.window_size, this.window_size, this.RED, enemy_speed, enemy_radius, enemy_movement, randomize_enemy_radius, randomize_enemy_speed, normalize));
        }
    }
    DodgeGameEnv.prototype.getObservation = function () {
        return this.window.getImageData(0, 0, this.canvas.width, this.canvas.height).data;
    };
    DodgeGameEnv.prototype.reset = function () {
        this.game_over = false;
        this.player.reset();
        this.enemies.forEach(function (enemy) { return enemy.reset(); });
        this.score = 0;
        this.hp = this.max_hp;
        // this.window_size = randint(64, 128);
        if (this.randomize_enemy_num) {
            this.enemy_num = Math.random() * (this.max_enemy_num - 1) + 1;
            this.enemies = [];
            // console.log(this.enemy_num);
            for (var i = 0; i < this.enemy_num; i++) {
                this.enemies.push(new enemy_1.default(this.window_size, this.window_size, this.RED, this.enemy_speed, this.enemy_radius, this.enemy_movement, this.randomize_enemy_radius, this.randomize_enemy_speed, this.normalize));
            }
        }
        var observation = this.getObservation();
        return observation;
    };
    DodgeGameEnv.prototype.isGameOver = function () {
        var _this = this;
        return this.enemies.some(function (enemy) {
            var distance = Math.sqrt(Math.pow((_this.player.pos.x - enemy.pos.x), 2) + Math.pow((_this.player.pos.y - enemy.pos.y), 2));
            return distance < _this.player.radius + enemy.radius;
        }) || this.player.pos.x < 0 || this.player.pos.x > 1 || this.player.pos.y < 0 || this.player.pos.y > 1;
    };
    DodgeGameEnv.prototype.step = function (action) {
        if (this.game_over) {
            this.game_over = false;
        }
        this.player.aiMove(action);
        this.moveEnemies();
        if (this.player.touchWall()) {
            this.game_over = true;
        }
        var gameOver = this.isGameOver();
        this.hp -= gameOver ? 1 : 0;
        var reward = 1 + (this.game_over ? -1 * this.death_penalty : 0);
        this.score += reward;
        var observation = this.getObservation();
        var done = this.hp <= 0;
        var info = {};
        return [observation, reward, done, info];
    };
    DodgeGameEnv.prototype.render = function () {
        var _this = this;
        this.window.clearRect(0, 0, this.window_size, this.window_size);
        this.player.draw(this.window);
        this.enemies.forEach(function (enemy) { return enemy.draw(_this.window); });
        this.window.font = this.font;
        this.window.fillStyle = this.BLACK;
        this.window.fillText("Score: ".concat(this.score), 10, 50);
        this.window.fillText("HP: ".concat(this.hp), 10, 80);
    };
    DodgeGameEnv.prototype.moveEnemies = function () {
        for (var _i = 0, _a = this.enemies; _i < _a.length; _i++) {
            var enemy = _a[_i];
            enemy.move(this.player.pos);
            // Check for collisions with the player
            if (this.player.isCollidingWith(enemy)) {
                this.game_over = true;
            }
        }
    };
    DodgeGameEnv.prototype.run = function () {
        this.reset();
        this.render();
        this.game_over = false;
        while (true) {
            var action = Math.floor(Math.random() * 4);
            this.step(action);
            this.render();
        }
    };
    return DodgeGameEnv;
}());
exports.default = DodgeGameEnv;
