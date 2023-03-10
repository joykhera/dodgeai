import pygame
from dodgeGame import Game
import os
import neat
import pickle
from plot import plot

WIDTH = 800
HEIGHT = 800
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

numGames = 0
total_score = 0
plot_scores = []
plot_mean_scores = []

class DodgeAI:
    def __init__(self):
        self.game = Game(WINDOW, WIDTH, HEIGHT)
        self.player = self.game.player
        self.enemies = self.game.enemies
        
    def test_ai(self, genome, config):
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        run  = True
        clock = pygame.time.Clock()
        
        while run:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break
                
            output = net.activate(self.game.get_state())
            decision = output.index(max(output))
            # self.game.loop(decision, numGames)
            self.game.loop(output, numGames)

            if self.game.game_over or self.game.game_over_wall:
                self.game.reset()
        
        pygame.quit()
        
    def train_ai(self, genome, config):
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        run = True
        clock = pygame.time.Clock()
        
        while run:
            # clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                    
            output = net.activate(self.game.get_state())
            self.game.loop(output, numGames)
            genome.fitness += ((self.game.enemies[0].x - self.game.player.x) ** 2 + (self.game.enemies[0].y - self.game.player.y) ** 2) * 0.0000001
            
            if self.game.score > 1000 or self.game.game_over or self.game.game_over_wall:
                score = self.game.score
                genome.fitness += score
                if self.game.game_over_wall and score < 0.05:
                    genome.fitness = 0
                elif self.game.game_over_wall:
                    genome.fitness /= 2
                self.game.reset()
                # return genome.fitness
                return score
            
def eval_genomes(genomes, config):
    for (genome_id, genome) in genomes:
        global numGames 
        global plot_scores
        global plot_mean_scores
        global total_score
        
        numGames += 1
        genome.fitness = 0
        game = DodgeAI()
        score = game.train_ai(genome, config)
        
        plot_scores.append(score)
        total_score += score
        mean_score = total_score / numGames
        plot_mean_scores.append(mean_score)
        
        if numGames > 20000:
            plot(plot_scores, plot_mean_scores)
        
def run_neat(config):
    p = neat.Checkpointer.restore_checkpoint('checkpoints/neat-checkpoint-199')
    # p = neat.Population(config)
    # Log info to console
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(10, filename_prefix='checkpoints/neat-checkpoint-'))

    winner = p.run(eval_genomes, 1000)
    with open("best.pickle", "wb") as f:
        pickle.dump(winner, f)
            
            
def test_ai(config):
    with open("best.pickle", "rb") as f:
        winner = pickle.load(f)

    game = DodgeAI()
    game.test_ai(winner, config)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")

    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    
    run_neat(config)
    # test_ai(config)
    # DodgeAI().game.run()
