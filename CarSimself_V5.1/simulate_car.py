import pygame
from scipy.optimize import minimize
import neat
import time
from multiprocessing import Process
import os
from simulation import run_simulation


def iter_for_optimize(k1=1.1, k2=1, k3=1, kp1=1, kp2=1):
    # Hier geben Sie den Speicherort von interface.py an
    with open('C:/Users/10215/Desktop/CarSimself_V4.0/interface.py',encoding='utf-8', mode='r') as f:
        flist = f.readlines()
    i = flist[86].index('=')
    flist[86] = flist[86][:i + 1] + ' ' + str(k1) + '\n'
    print(flist[86])
    i = flist[87].index('=')
    flist[87] = flist[87][:i + 1] + ' ' + str(k2) + '\n'
    print(flist[87])
    i = flist[88].index('=')
    flist[88] = flist[88][:i + 1] + ' ' + str(k3) + '\n'
    print(flist[88])
    i = flist[89].index('=')
    flist[89] = flist[89][:i + 1] + ' ' + str(kp1) + '\n'
    print(flist[89])
    i = flist[79].index('=')
    flist[79] = flist[79][:i + 1] + ' ' + str(kp2) + '\n'
    print(flist[79])
    with open('C:/Users/10215/Desktop/CarSimself_V4.0/interface.py',encoding='utf-8', mode='w') as f:
        f.writelines(flist)


def simulation(k1, k2, k3, kp1, kp2):
    # Load Config
    config_path = "./config.txt"
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    # Set Population Size to 2
    config.pop_size = 2
    # Geben Sie hier den Speicherort für log.csv ein
    with open('C:/Users/10215/Desktop/CarSimself_V4.0/log.csv', encoding='utf-8',
              mode='a+') as f:
        f.write(str(list([k1, k2, k3, kp1, kp2])))
        f.write(',')
    # Create Population And Add Reporters
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Run Simulation For A Maximum of 1000 Generations
    # run_simulation(list(iteritems(population.population)), config)
    start_time = time.time()
    population.run(run_simulation, 1000)
    end_time = time.time()

    return end_time - start_time


def simulate_car(k1, k2, k3, kp1, kp2):
    pygame.init()
    iter_for_optimize(k1, k2, k3, kp1, kp2)

    # lap_time=simulation()
    cp = Process(target=simulation, args=(k1, k2, k3, kp1, kp2))
    start_time = time.time()
    cp.start()
    time.sleep(60)
    find_kill = 'taskkill -f -pid %s' % (cp.pid)
    result = os.popen(find_kill)
    end_time = time.time()
    lap = end_time - start_time
    if lap >= 20:
        # Geben Sie hier den Speicherort für log.csv ein
        with open('C:/Users/10215/Desktop/CarSimself_V4.0/log.csv',encoding='utf-8', mode='a+') as f:
            f.write(str(20))
            f.write('\n')

    # pygame.quit()
    return end_time - start_time


def objective_function(params):
    k1, k2, k3, kp1, kp2 = params

    return -simulate_car(k1, k2, k3, kp1, kp2)


if __name__ == "__main__":
    # Geben Sie hier den Speicherort für log.csv ein
    with open('C:/Users/10215/Desktop/CarSimself_V4.0/log.csv', encoding='utf-8',mode='w') as f:
        f.write('Parameter' + ',' + 'round_time' + '\n')

    initial_point = [1.1, 1.1, 1.1, 1, 1]
    bounds = [(1.1, 20), (1.1, 20), (1.1, 20), (1, 20), (1, 20)]

    result = minimize(objective_function, initial_point, method='BFGS', bounds=bounds)

    optimal_k1, optimal_k2, optimal_k3, optimal_kp1, optimal_kp2 = result.xrange
    optimal_lap_time = -result.fun
    print("Optimized Parameters:")
    print("K1:", optimal_k1)
    print("K2:", optimal_k2)
    print("K3:", optimal_k3)
    print("Kp1:", optimal_kp1)
    print("Kp2:", optimal_kp2)
    print("Optimal Lap Time:", optimal_lap_time)
