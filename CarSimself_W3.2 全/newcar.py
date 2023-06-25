# This Code is Heavily Inspired By The YouTuber: Cheesy AI
# Code Changed, Optimized And Commented By: NeuralNine (Florian Dedov)


import neat

from simulation import run_simulation

# Constants# WIDTH = 1600 # HEIGHT = 880

# f = 1.6
#
# WIDTH = 1920/2 * f     #
# HEIGHT = 1080/2 * f
# window_size = (WIDTH, HEIGHT)
#
# time_flip = 0.01  # 10ms
#
# CAR_SIZE_X = 23.75 * f
# CAR_SIZE_Y = 10 * f
#
# BORDER_COLOR: tuple[int, int, int, int] = (255, 255, 255, 255)  # Color To Crash on Hit

# current_generation = 0  # Generation counter

if __name__ == "__main__":
    
    # Load Config
    config_path = "./config.txt"
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    # Set Population Size to 2
    config.pop_size = 2

    # Create Population And Add Reporters
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    
    # Run Simulation For A Maximum of 1000 Generations
    population.run(run_simulation, 1000)
