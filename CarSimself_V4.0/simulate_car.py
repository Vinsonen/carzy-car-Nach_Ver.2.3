import pygame
from scipy.optimize import minimize
import neat
import time
from multiprocessing import Process
import os

from simulation import run_simulation
print(os.getpid())

def iter_for_optimize(k1=1.1,k2=1,k3=1,kp1=1,kp2=1):
    with open('./interface.py',encoding='utf-8',mode = 'r') as f:
        flist=f.readlines()
    i=flist[93].index('=')
    flist[93]=flist[93][:i+1]+' '+str(k1)+'\n'
    print(flist[93])
    i=flist[94].index('=')
    flist[94]=flist[94][:i+1]+' '+str(k2)+'\n'
    print(flist[94])
    i=flist[95].index('=')
    flist[95]=flist[95][:i+1]+' '+str(k3)+'\n'
    print(flist[95])
    i=flist[96].index('=')
    flist[96]=flist[96][:i+1]+' '+str(kp1)+'\n'
    print(flist[96])
    i=flist[81].index('=')
    flist[81]=flist[81][:i+1]+' '+str(kp2)+'\n'
    print(flist[81])
    with open('./interface.py',encoding='utf-8',mode = 'w') as f:
        f.writelines(flist)

def simulation():
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
    # run_simulation(list(iteritems(population.population)), config)
    start_time=time.time()
    population.run(run_simulation, 1000)
    end_time=time.time()
    return end_time-start_time

def simulate_car(k1,k2,k3,kp1,kp2):
    pygame.init()
    iter_for_optimize(k1,k2,k3,kp1,kp2)
    with open('./log.csv', encoding='utf-8', mode='a+') as f:
        f.write(str(list([k1,k2,k3,kp1,kp2])))
        f.write(',')

    # lap_time=simulation()
    print(os.getpid())
    cp = Process(target = simulation, args=())
    start_time = time.time()
    cp.start()
    print(cp.name,cp.pid)
    time.sleep(60)
    find_kill = 'taskkill -f -pid %s' % (cp.pid)
    print(find_kill)
    result = os.popen(find_kill)
    end_time = time.time()
    lap=end_time-start_time
    if lap>=20:
            with open('./log.csv', encoding='utf-8',mode='a+') as f:
                        f.write(str(20))
                        f.write('\n')

    return end_time-start_time

def objective_function(params):
    k1,k2,k3,kp1,kp2=params

    return -simulate_car(k1,k2,k3,kp1,kp2)


if __name__=="__main__":
    with open('./log.csv', encoding='utf-8', mode='w') as f:
        f.write('Parameter'+','+'round_time'+'\n')

    initial_point=[1.1,1.1,1.1,1,1]
    bounds = [(1.1, 10), (1.1, 10), (1.1, 10), (1, 10), (1, 10)]

    result=minimize(objective_function,initial_point,method='Nelder-Mead',bounds=bounds)

    optimal_k1,optimal_k2,optimal_k3,optimal_kp1,optimal_kp2=result.xrange
    optimal_lap_time=-result.fun
    print("Optimized Parameters:")
    print("K1:", optimal_k1)
    print("K2:", optimal_k2)
    print("K3:", optimal_k3)
    print("Kp1:", optimal_kp1)
    print("Kp2:", optimal_kp2)
    print("Optimal Lap Time:", optimal_lap_time)
