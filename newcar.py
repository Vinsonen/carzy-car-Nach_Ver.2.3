# This Code is Heavily Inspired By The YouTuber: Cheesy AI
# Code Changed, Optimized And Commented By: NeuralNine (Florian Dedov)

import math
import random
import sys
import os
# import cv2
# from google.colab.patches import cv2_imshow
# from google.colab import output
import time
import neat
import pygame

# Constants
# WIDTH = 1600
# HEIGHT = 880

f =1
WIDTH = 960*f
HEIGHT = 540*f
# WIDTH = 960*f
# HEIGHT = 540*f

time_step = 0.01  # 10ms
CAR_SIZE_X = 23.75 * f  # 60/f
CAR_SIZE_Y = 10 * f  # 30/f
CAR_Radstand = 13 # 前后轮距
CAR_Spurweite = 10 # 左右轮距

BORDER_COLOR = (255, 255, 255, 255)  # Color To Crash on Hit

current_generation = 0  # Generation counter

class Car:

    def __init__(self):
        # Load Car Sprite and Rotate
        self.sprite = pygame.image.load('car.png').convert()  # Convert Speeds Up A Lot
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite 

        # self.position = [690, 740]  # Starting Position
        self.position = [400*f, 415*f] # Starting Position
        # self.position = [415*f, 460*f]  # Starting Position
        self.angle = 0
        self.speed = 0
        # self.gewicht= 0  # 质量
        # self.reibung=0  # 摩擦力
        # self.luftwiderstand=0  # 空气阻力
        # self.beschleunigung=0  # 加速度
        self.power=0  #  发动机功率 fahr()
        self.carangle = 0 # 整辆车转过的角度

        self.speed_set = False  # Flag For Default Speed Later on稍后标记默认速度

        self.center = [self.position[0] + CAR_SIZE_X / 2, self.position[1] + CAR_SIZE_Y / 2] # Calculate Center

        self.radars = [] # List For Sensors / Radars
        self.drawing_radars = []  # Radars To Be Drawn待绘制的雷达

        self.alive = True  # Boolean To Check If Car is Crashed检查汽车是否坠毁

        self.distance = 0  # Distance Driven
        self.time = 0  # Time Passed



    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position)  # Draw Sprite如飞机的分数显示和game over
        self.draw_radar(screen)  # OPTIONAL FOR SENSORS 画雷达？

    def draw_radar(self, screen):
        # Optionally Draw All Sensors / Radars
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (0, 255, 0), position, 5)  # 5是半径

    def check_collision(self, game_map):
        self.alive = True
        for point in self.corners:
            # If Any Corner Touches Border Color -> Crash 如果任何角接触到边框颜色 -> 崩溃
            # Assumes Rectangle
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                self.alive = False
                break

    def check_radar(self, degree, game_map):
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # While We Don't Hit BORDER_COLOR AND length < 300 (just a max) -> go further and further
        # 没有被crash或者长度小于300就可以一直移动
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 100*f:
            length = length + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # Calculate Distance To Border And Append To Radars List 计算到边界的距离并附加到雷达列表
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])


    def Lenkeinschlagsänderung(self,angle):
        '''maxmaleangle = 10  # 最大转向角
        if self.angle > maxmaleangle:
            self.angle = maxmaleangle'''
        angle_rad = math.radians(angle)  # 前内轮转过的角度转换后的弧度值
        CAR_Radius = CAR_Radstand/math.tan(angle_rad) + CAR_Spurweite/2  #半径
        self.carangle=math.degrees(self.distance/CAR_Radius) # distance改为speed？
        # self.carangle= 2*math.atan(math.tan(angle_rad)*CAR_Radstand)
        self.Drehgeschwindigkeit(CAR_Radius)
        return self.carangle


    def Drehgeschwindigkeit(self,radius,power):
        winkelgeschwindigkeit= 0.0507 -0.0062*math.cos(power*0.2730) -0.0049*math.sin(power*0.2730) \
                             - 0.0010*math.cos(power*0.546) + 0.0120*math.sin(power*0.546) \
                             + 0.0020*math.cos(power*0.819) + 0.0002*math.sin(power*0.819)
        drehgeschwindigkeit= winkelgeschwindigkeit*radius  #转角最大时 fahr的范围为18到35
        return  drehgeschwindigkeit

    def Geschwindigkeit(self,power):
        # self.power =   # 等于motorleisung的函数 百分比？
        # reibungsköffizient=0  # 摩擦力系数
        # luftwiderstandsköffizient=0  # 空气阻力系数
        # g=9.8 rho = 0 querschnittsfläche= 0  # 横截面积
        # self.reibung = reibungsköffizient * self.gewicht * g  # 摩擦力
        # self.luftwiderstand=luftwiderstandsköffizient * 0.5 * rho * querschnittsfläche * (self.speed ** 2)  # 空气阻力
        '''maxmalepower= 100  # 最大fahr(100) 最大发动机功率..
        minimalpower = 18
        if self.power > maxmalepower:
            self.power= maxmalepower
        elif self.power < minimalpower:
            self.power = minimalpower'''
        # self.beschleunigung= (self.power - self.reibung - self.luftwiderstand)/self.gewicht  # 加速度
        # beschleunigungänderung = self.beschleunigung * time_step
        maxspeed = -0.0496 * (power**2) + 9.008 * power + 31.8089  # max(0 , self.speed + beschleunigungänderung)
        beschleunigung = 1.3734 + 0.6223*math.cos(0.1448*power) + 0.3615*math.sin(power*0.1448) \
                -0.1298*math.cos(0.2896*power*0.1448) + 0.0673*math.sin(0.2896*power) \
                + 0.0691*math.cos(power*0.4344) -0.0485*math.sin(power*0.4344) # fahr的范围为18到50
        self.speed +=beschleunigung
        if self.speed > maxspeed:
            self.speed = maxspeed
        # self.distance += self.speed * time_step
        return self.speed



    def update(self, game_map):
        # Set The Speed To 20 For The First Time
        # Only When Having 4 Output Nodes With Speed Up and Down
        if not self.speed_set:  # 如果不是默认速度的话
            self.speed = 4*f
            self.speed_set = True

        # Get Rotated Sprite And Move Into The Right X-Direction
        # Don't Let The Car Go Closer Than 20px To The Edge  不要让汽车靠近边缘20px
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)  # 关于旋转
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 20*f)  # 不让汽车靠近窗口左边缘超过20/f像素
        self.position[0] = min(self.position[0], WIDTH - 120*f)  # 不让汽车靠近窗口右边缘超过120/f像素 （120/f是车图片的整体长度

        # Increase Distance and Time
        self.distance += self.speed
        self.time += 1
        
        # Same For Y-Position
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20*f)
        self.position[1] = min(self.position[1], WIDTH - 120*f)

        # Calculate New Center
        self.center = [int(self.position[0]) + CAR_SIZE_X / 2, int(self.position[1]) + CAR_SIZE_Y / 2]

        # Calculate Four Corners
        # Length Is Half The Side
        length = 0.5 * CAR_SIZE_X  # 下方的角度是通过实体车测量出来的
        weith = 0.5 * CAR_SIZE_Y
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.carangle + 23))) * length,
                    self.center[1] + math.sin(math.radians(360 - (self.carangle + 23))) * weith]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.carangle + 157))) * length,
                     self.center[1] + math.sin(math.radians(360 - (self.carangle + 157))) * weith]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.carangle + 203))) * length,
                       self.center[1] + math.sin(math.radians(360 - (self.carangle + 203))) * weith]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.carangle + 337))) * length,
                        self.center[1] + math.sin(math.radians(360 - (self.carangle + 337))) * weith]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        # Check Collisions And Clear Radars  检查碰撞并清除雷达
        self.check_collision(game_map)
        self.radars.clear()

        # From -90 To 120 With Step-Size 45 Check Radar
        for d in range(-60, 120, 60):
            self.check_radar(d, game_map)

    def get_data(self):
        # Get Distances To Border
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)  # 为什么是radar[1] ？除30？？？

        return return_values

    def is_alive(self):
        # Basic Alive Function
        return self.alive

    def get_reward(self):
        # Calculate Reward (Maybe Change?)
        # return self.distance / 50.0 为什么除50？？？
        return self.distance / (CAR_SIZE_X / 2)

    def rotate_center(self, image, angle):
        # Rotate The Rectangle
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        # rotated_rectangle = rectangle.copy()
        # rotated_rectangle.center = rotated_image.get_rect().center
        # rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image






def run_simulation(genomes, config):
    
    # Empty Collections For Nets and Cars
    nets = []
    cars = []

    # Initialize PyGame And The Display 初始化 PyGame 和显示
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)     # pygame.FULLSCREEN)

    # For All Genomes Passed Create A New Neural Network 为所有通过的基因组创建一个新的神经网络？？？？
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        cars.append(Car())

    # Clock Settings
    # Font Settings & Loading Map
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 15)
    alive_font = pygame.font.SysFont("Arial", 10)
    game_map = pygame.image.load('Rmap.png').convert() # Convert Speeds Up A Lot

    global current_generation
    current_generation += 1

    # Simple Counter To Roughly Limit Time (Not Good Practice) # 粗略限制时间的简单计数器（不是好的做法）
    counter = 0

    while True:
        # Exit On Quit Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # For Each Car Get The Acton It Takes ???
        for i, car in enumerate(cars):
            output = nets[i].activate(car.get_data())
            choice = output.index(max(output))
            if choice == 0:
                # car.Lenkeinschlagsänderung() += 10
                car.angle += 10# Left
            elif choice == 1:
                # car.Lenkeinschlagsänderung() -= 10
                car.angle -= 10 # Right
            elif choice == 2:
                if(car.speed - 2 >= 12):
                    car.speed -= 2 # Slow Down
            else:
                car.speed += 2 # Speed Up
        
        # Check If Car Is Still Alive
        # Increase Fitness If Yes And Break Loop If Not
        still_alive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                still_alive += 1
                car.update(game_map)
                genomes[i][1].fitness += car.get_reward()  #??????

        if still_alive == 0:
            break

        counter += 1
        if counter == 30 * 40: # Stop After About 20 Seconds ??????
            break

        # Draw Map And All Cars That Are Alive
        screen.blit(game_map, (0, 0))
        for car in cars:
            if car.is_alive():
                car.draw(screen)
        
        # Display Info
        text = generation_font.render("Generation: " + str(current_generation), True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (900/2*f, 450/2*f)
        screen.blit(text, text_rect)

        text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (900/2*f, 490/2*f)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(1/time_step) # 100 FPS

if __name__ == "__main__":
    
    # Load Config
    config_path = "./config.txt"
    config = neat.config.Config(neat.DefaultGenome,  #默认的基因组类
                                neat.DefaultReproduction,  #默认的繁殖类
                                neat.DefaultSpeciesSet,  #默认的物种集合类
                                neat.DefaultStagnation,  #默认的停滞类
                                config_path)

    # Create Population And Add Reporters ?????????
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    
    # Run Simulation For A Maximum of 1000 Generations
    population.run(run_simulation, 1000)

'''首先，通过指定一个配置文件路径 config_path，创建了一个 neat.config.Config 对象 config，该对象包含了遗传算法中的配置信息，如基因组、繁殖、物种集合和停滞等。
接着，通过使用 neat.Population 类，基于配置文件 config 创建了一个种群 population，该种群将包含进行遗传算法优化的个体（基因组）。
然后，通过 neat.StdOutReporter 类创建了一个标准输出的报告器，将在控制台输出优化过程中的统计信息，例如每一代的最佳基因组、种群的平均适应度等。
True 参数表示将报告器的输出设置为详细模式。
最后，通过 neat.StatisticsReporter 类创建了一个统计信息的报告器 stats，用于记录种群的统计信息，例如每一代的适应度、物种数量、个体数量等。
这些统计信息可以用于生成进化过程中的图表和可视化等用途。将 stats 添加到 population 中，以便在优化过程中记录种群的统计信息。'''
