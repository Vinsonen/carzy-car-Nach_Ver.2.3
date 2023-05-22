import math
import pygame

import simulation
import numpy as np
import pygame.freetype
f = 1

WIDTH = 1920 * f  #
HEIGHT = 1080 * f


# window_size = (WIDTH, HEIGHT)


def sim_to_real(simpx):
    realcm = (simpx * 1900) / WIDTH  # realmap: 1900cm(17m+1m+1m)<=> WIDTH(1920 * f)pixel
    return realcm


def real_to_sim(realcm):
    simpx = realcm * WIDTH / 1900
    return simpx


CAR_SIZE_Xcm = 40  # Car real size 40cm *20cm
CAR_SIZE_Ycm = 20

CAR_SIZE_X = real_to_sim(CAR_SIZE_Xcm)  # 23.75*2 * f  32.3px
CAR_SIZE_Y = real_to_sim(CAR_SIZE_Ycm)  # 20cm == 16.17px

CAR_cover_size = max(CAR_SIZE_X, CAR_SIZE_Y)

CAR_SIZE_DiffY = real_to_sim(40 - 20)
CAR_Radstand = real_to_sim(25)  # 轮距

BORDER_COLOR: tuple[int, int, int] = (255, 255, 255)  # Color To Crash on Hit


def set_position(self, position):
    self.position = position


def rechnenMaxMin_position(self, position, screen):
    change = False
    positionMaxX, positionMinX = self.position, self.position
    if position[0] > positionMaxX[0]:
        positionMaxX = position
        change = True
    if position[0] < positionMinX[0]:
        positionMinX = position
        change = True
    font = pygame.freetype.SysFont("Arial", 19)
    # if not change:
    #     font.render_to(screen, (100, 100), f"maxxPosition : ({positionMaxX[0]:0f},{positionMaxX[1]:0f})  "
    #                                    f"minnPosition: ( {positionMinX[0]:0f}{positionMinX[1]:0f} )"
    #                                    f"radius: {positionMaxX[0]-positionMinX[0]:2f}", (255, 0, 100))

class Car:

    def __init__(self, position, carangle, fahrspeed, speed_set, radars, bit_volt_wert_list, distance, time):
        # Load Car Sprite and Rotate
        self.sprite = pygame.image.load('car.png').convert()  # Convert Speeds Up A Lot
        self.sprite = pygame.transform.scale(self.sprite, (CAR_cover_size, CAR_cover_size))
        self.rotated_sprite = self.sprite

        # self.position = [690, 740] # Starting Position
        # self.position = [800 * f, 825 * f]  # Starting Position
        # self.position = [840 * f, 930 * f]
        self.position = position
        self.center = [self.position[0] + CAR_cover_size / 2, self.position[1] + CAR_cover_size / 2]  # Calculate Center
        self.corners = []

        self.speed = self.Geschwindigkeit(fahrspeed)
        self.speed_set = speed_set  # Flag For Default Speed Later on

        # self.gewicht= 0  # 质量
        # self.reibung=0  # 摩擦力
        # self.luftwiderstand=0  # 空气阻力
        # self.beschleunigung=0  # 加速度
        self.power = 0  # 发动机功率 fahr()
        self.radangle = 0
        self.carangle = carangle  # 整辆车转过的角度

        self.radars = radars  # List For Sensors / Radars
        # self.radarR = self.radars[0:1]
        # self.radarM = self.radars[2:3]
        # self.radarL = self.radars[4:5]
        self.radar_angle = 60
        self.radar_dist = []
        self.bit_volt_wert_list = bit_volt_wert_list  # ADC  [(bit, volt),(,)...]
        self.drawing_radars = []  # Radars To Be Drawn

        self.alive = True  # Boolean To Check If Car is Crashed
        self.angle_enable = True
        self.radars_enable = True
        self.drawradar_enable = True

        self.distance = distance  # Distance Driven
        self.anlog_dist = []
        self.time = time  # Time Passed

    def get_data_to_serialize(self):
        return {
            'position': self.position,
            'carangle': self.carangle,
            'speed': self.speed,
            'speed_set': self.speed_set,
            'radars': self.radars,
            'analog_wert_list': self.bit_volt_wert_list,

            'distance': self.distance,
            'time': self.time,
        }

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position)  # Draw Sprite
        self.draw_radar(screen)  # OPTIONAL FOR SENSORS

    def draw_radar(self, screen):
        # Optionally Draw All Sensors / Radars
        if self.drawradar_enable:
            for radar in self.radars:  # 拿到目的坐标画曲线
                position = radar[0]
                pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
                pygame.draw.circle(screen, (0, 255, 0), position, 5)
        else:
            return

    def check_radar(self, degree, game_map):  # , midlength):   # degree 分别代表三个方向的雷达  检查到边缘的距离
        # midradar = False
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.carangle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.carangle + degree))) * length)

        # While We Don't Hit BORDER_COLOR AND length < 300 (just a max) -> go further and further
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 150 * WIDTH / 1900:
            length = length + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.carangle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.carangle + degree))) * length)

        # Calculate Distance To Border And Append To Radars List
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])

    def get_radars_dist(self):
        # Get Distances To Border
        # 返回三个雷达的距离值 R M L
        radars = self.radars
        self.radar_dist = []
        for i, radar in enumerate(radars):
            self.radar_dist.append(int(radar[1]))

        return self.radar_dist

    def linearisierungDA(self):
        dist_list = self.get_radars_dist()
        A = 23962  # pro 2.5v == 1024bit <-->1v == 409.6bit
        B = -20
        AV = 58.5  # Wert in Volt
        BV = -0.05
        bit_volt_wert_list = []
        for dist in dist_list:
            # 对dist进行等比例缩放   dist to real_dist(cm)
            real_dist = sim_to_real(dist)
            if real_dist == 0:
                digital_bit, analog_volt = 0, 0
            else:
                digital_bit = int((A / real_dist) + B)
                analog_volt = (AV / real_dist) + BV
            bit_volt_wert_list.append((digital_bit, analog_volt))
        return bit_volt_wert_list

    def rebound_action(self, game_map, point):
        # sfa反射角度的计算
        # self.speed = 1

        point1 = [0, 0]
        radius = 15
        # 找到碰撞点point的墙壁的向量 通过颜色的差别找出所碰撞的墙壁的另一个点，来判断现在的墙壁的向量
        for i in range(0, 360, 3):
            angle = math.radians(i)
            x = point[0] + radius * math.cos(math.radians(angle))
            y = point[1] + radius * math.sin(math.radians(angle))
            if game_map.get_at([int(x), int(y)]) == BORDER_COLOR and game_map.get_at(
                    [int(point[0] + radius * math.cos(math.radians(angle + 5))),
                     int(point[1] + radius * math.sin(math.radians(angle + 5)))]) == (0, 0, 0):
                point1 = [int(x), int(y)]
                break

        # 计算两个反射面和入射角向量
        v1 = np.array([point1[0] - point[0], point1[1] - point[1]])  # np.array(point1) - np.array(point)
        theta = np.radians(self.carangle)
        v2 = np.array([np.cos(theta), np.sin(theta)])

        # 计算反射向量   计算反射向量与参考坐标轴正方向的夹角，并转化为角度制的角度值
        reflection = v1 - 2 * (np.dot(v1, v2) / np.dot(v2, v2)) * v2
        angle_reflection = np.degrees(np.arctan2(reflection[1], reflection[0]))
        while angle_reflection < 0:
            angle_reflection += 360
        while angle_reflection >= 360:
            angle_reflection -= 360
        return angle_reflection

    def check_collision(self, game_map):
        # 检查碰撞
        # self.alive = True
        for point in self.corners:
            # If Any Corner Touches Border Color -> Crash
            # Assumes Rectangle

            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                # 通过检查按钮目前的state来判断哪个
                status = simulation.switch_3button.get_status()
                if status == 0:
                    self.alive = False
                elif status == 1:
                    self.speed = 0
                    self.angle_enable, self.drawradar_enable = False, False
                elif status == 2:
                    self.carangle = self.rebound_action(game_map, point)

            break





    def update(self, game_map):
        # Set The Speed To 20 For The First Time
        # Only When Having 4 Output Nodes With Speed Up and Down
        if not self.speed_set and self.speed == 0:
            self.speed = 2 * f
            self.speed_set = True

        # Increase Distance and Time
        self.distance += self.speed
        self.time += 0.01

        position_tmp = self.position

        self.rotated_sprite = self.rotate_center(self.sprite, self.carangle)
        # Get Rotated Sprite And Move Into The Right X-Direction   Same For Y-Position
        # Don't Let The Car Go Closer Than 20px To The Edge
        # 直线形式or 转弯

        if self.radangle != 0:
            self.carangle = self.Lenkeinschlagsänderung()

        position_tmp[0] += math.cos(math.radians(360 - self.carangle)) * self.speed
        position_tmp[1] += math.sin(math.radians(360 - self.carangle)) * self.speed

        position_tmp[0] = max(position_tmp[0], 20 * f)
        position_tmp[0] = min(position_tmp[0], WIDTH - 120 * f)
        # Calculate New Center
        position_tmp[1] = max(position_tmp[1], 20 * f)
        position_tmp[1] = min(position_tmp[1], WIDTH - 120 * f)

        self.center = [int(position_tmp[0]) + CAR_cover_size / 2, int(position_tmp[1]) + CAR_cover_size / 2]

        rechnenMaxMin_position(self, position_tmp, game_map)
        set_position(self, position_tmp)
        pygame.draw.circle(game_map, (0, 255, 0), self.center, 2)
        # Calculate Four Corners
        # Length Is Half The Side
        aus_pixel = 2 * f
        length = 0.5 * CAR_SIZE_X + aus_pixel
        width = 0.5 * CAR_SIZE_Y + aus_pixel
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.carangle + 23))) * length,
                    self.center[1] + math.sin(math.radians(360 - (self.carangle + 23))) * width]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.carangle + 157))) * length,
                     self.center[1] + math.sin(math.radians(360 - (self.carangle + 157))) * width]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.carangle + 203))) * length,
                       self.center[1] + math.sin(math.radians(360 - (self.carangle + 203))) * width]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.carangle + 337))) * length,
                        self.center[1] + math.sin(math.radians(360 - (self.carangle + 337))) * width]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        # Check Collisions And Clear Radars  检查碰撞
        self.check_collision(game_map)
        self.radars.clear()

        # From -90 To 120 With Step-Size 45 Check Radar
        self.check_radars_enable()
        if self.radars_enable:
            for d in range(-self.radar_angle, self.radar_angle + 1, self.radar_angle):
                self.check_radar(d, game_map)

            self.radar_dist = self.get_radars_dist()
            self.bit_volt_wert_list = self.linearisierungDA()

    def Lenkeinschlagsänderung(self):
    # 15°  直径125cm
        maxmaleangle = 16
        minmaleangle = -16  # 最大转向角
        if self.radangle > maxmaleangle:
            self.radangle = maxmaleangle
        if self.radangle < minmaleangle:
            self.radangle = minmaleangle

        angle_rad = math.radians(self.radangle)  # 前轮转过的角度转换后的弧度值
        car_radius = int(CAR_Radstand / math.tan(angle_rad))  # 轮距CAR_Radstand
        theta = math.degrees(self.speed / car_radius)

        # kennzeichen = self.radangle / math.fabs(self.radangle)
        # # position[1] += CAR_Radius * (math.sin(math.radians(self.carangle + theta)) - math.sin(math.radians(self.carangle)))
        # # position[0] += CAR_Radius * (math.cos(math.radians(self.carangle)) - math.cos(math.radians(self.carangle + theta)))
        #
        # dx = kennzeichen * self.speed * car_radius * (
        #             math.sin(math.radians(self.carangle + theta)) - math.sin(math.radians(self.carangle)))
        # dy = kennzeichen * self.speed * car_radius * (
        #             math.cos(math.radians(self.carangle)) - math.cos(math.radians(self.carangle + theta)))
        # position[0] += dx
        # position[1] += dy

        self.carangle += theta

        while self.carangle < 0:
            self.carangle += 360
        while self.carangle >= 360:
            self.carangle -= 360
        # self.carangle= 2*math.atan(math.tan(angle_rad)*CAR_Radstand)
        return self.carangle

    def is_alive(self):
        # Basic Alive Function
        return self.alive

    def get_reward(self):
        # Calculate Reward (Maybe Change?)
        # return self.distance / 50.0
        return self.distance / (CAR_SIZE_X / 2)

    def rotate_center(self, image, angle):
        # Rotate The Rectangle
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_image = rotated_image.convert_alpha()  # 将表面对象转换为带 alpha 通道的表面对象
        rotated_image.set_colorkey((255, 255, 255, 255))  # 设置透明背景色
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image

    def check_radars_enable(self):
        if simulation.switch_2button.get_status() == 0:
            self.radars_enable = True
        else:
            self.radars_enable = False

    # 传出旋转圆的半径 将小车的carangle 改到self.carangle

    def Geschwindigkeit(self, power):
        # self.power =   # 等于motorleisung的函数 百分比？
        # reibungsköffizient=0  # 摩擦力系数
        # luftwiderstandsköffizient=0  # 空气阻力系数
        # g=9.8 rho = 0 querschnittsfläche= 0  # 横截面积
        # self.reibung = reibungsköffizient * self.gewicht * g  # 摩擦力
        # self.luftwiderstand=luftwiderstandsköffizient * 0.5 * rho * querschnittsfläche * (self.speed ** 2)  # 空气阻力
        maxmalepower = 100  # 最大fahr(100) 最大发动机功率..
        minimalpower = 18
        if power > maxmalepower:
            power = maxmalepower
        if power < minimalpower:
            power = minimalpower
        # self.beschleunigung= (self.power - self.reibung - self.luftwiderstand)/self.gewicht  # 加速度
        # beschleunigungänderung = self.beschleunigung * time_step
        speed = -0.0496 * (
                power ** 2) + 9.008 * power + 31.8089
        speed = real_to_sim(speed / 100)
        # max(0 , self.speed + beschleunigungänderung)
        # self.distance += self.speed * time_step
        return speed
