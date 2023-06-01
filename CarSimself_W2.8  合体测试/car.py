import math
import pygame
import cffi


import simulation
import numpy as np

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

BORDER_COLOR: tuple[int, int, int, int] = (255, 255, 255, 255)  # Color To Crash on Hit
OutBORDER_COLOR: tuple[int, int, int, int] = (0, 0, 0, 255)


def set_position(self, position):
    self.position = position


class Car:

    def __init__(self, position, carangle, power, speed_set, radars, bit_volt_wert_list, distance, time):
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
        self.left_rad = []
        self.right_rad = []
        self.fwert = 0
        self.swert = 0
        self.speed = self.Geschwindigkeit(power)
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
        self.speed_slowed = False
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

    def draw_track(self, screen):
        pygame.draw.circle(screen, (180, 180, 0), self.left_rad, 1)
        pygame.draw.circle(screen, (180, 0, 180), self.right_rad, 1)

        pygame.draw.circle(screen, (0, 180, 180), self.corners[2], 1)
        pygame.draw.circle(screen, (180, 180, 180), self.corners[3], 1)

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

    def rebound_action(self, game_map, point0, nr):
        # sfa反射角度的计算
        # self.speed = 1
        # pygame.draw.circle(game_map, (100, 0, 255), point0, 1)
        x0 = point0[0]
        y0 = point0[1]
        #point1 = [0, y0]

        radius = 15
        # 找到碰撞点point的墙壁的向量 通过颜色的差别找出所碰撞的墙壁的另一个点，来判断现在的墙壁的向量
        for vi in range(5, 370, 10):
            angle = math.radians(vi)
            x1 = x0 + radius * math.cos(angle)
            y1 = y0 + radius * math.sin(angle)
            x2 = x0 + radius * math.cos(angle + math.radians(15))
            y2 = y0 + radius * math.sin(angle + math.radians(15))

            point1 = [int(x1), int(y1)]

            if game_map.get_at([int(x1), int(y1)]) == BORDER_COLOR and \
                    game_map.get_at([int(x2), int(y2)]) != BORDER_COLOR:
                point1 = [int(x1), int(y1)]

                # 计算两点之间的斜率即为碰撞的斜面
                m = (point1[1] - point0[1]) / (point1[0] - point0[0])

                #pygame.draw.line(game_map, (100, 180, 180), (0, point1[1] - m * point1[0]),
                #                  (WIDTH, point0[1] + m * (WIDTH - point0[0])), 3)

                break

           # pygame.draw.circle(game_map, (100, 100, 100), (x1, y1), 1)

        # 计算两个反射面和入射角向量
        theta = np.radians(self.carangle)
        vi = np.array([np.cos(theta), np.sin(theta)])
        vw = np.array([point1[0] - point0[0], point1[1] - point0[1]])  # np.array(point1) - np.array(point)
        angle_theta = np.degrees(np.dot(vw, vi) / (np.linalg.norm(vw)*np.linalg.norm(vi)))
        if angle_theta > 90:
            angle_theta = 180-angle_theta

        # slower speed
        if angle_theta < 30:
            self.speed = self.speed * 0.1
        elif angle_theta < 60:
            self.speed = self.speed * 0.2
        else:
            self.speed = self.speed * 0.3
        self.speed_slowed = True

        if nr == 1 or 2:
            k0 = -1
        else:
            k0 = 1
        self.position[0] += k0 * math.cos(math.radians(360 - self.carangle)) * 8 * np.sin(
          np.radians(angle_theta)) * self.speed
        self.position[1] += k0 * math.sin(math.radians(360 - self.carangle)) * 8 * np.sin(
          np.radians(angle_theta)) * self.speed

        # change angle
        if nr == 1:  # left top
            kt = -1
        elif nr == 2:  # right top
            kt = 1
        else:    # bottom rad
            kt = 0

        turn_angle = 10 * np.cos(np.radians(angle_theta))
        self.carangle += kt * turn_angle
        self.carangle = (self.carangle % 360 + 360) % 360   # limit carangle 0~360

        # vn = np.array(point0[1] - point1[1], [point1[0] - point0[0]])
        # theta = np.radians(self.carangle)
        # vi = np.array([np.cos(theta), np.sin(theta)])
        #
        # # 计算反射向量   计算反射向量与参考坐标轴正方向的夹角，并转化为角度制的角度值
        # reflection = vi - 2 * (np.dot(vi, vn) / np.dot(vn, vn)) * vn
        # angle_reflection = np.degrees(np.arctan2(reflection[1], reflection[0]))

    def check_collision(self, game_map):
        # 检查碰撞
        # self.alive = True
        nr = 0
        for point in self.corners:
            # If Any Corner Touches Border Color -> Crash
            # Assumes Rectangle
            nr = nr+1
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                # 通过检查按钮目前的state来判断哪个

                status = simulation.switch_3button.get_status()
                if status == 0:
                    self.alive = False
                elif status == 1:
                    self.speed = 0

                elif status == 2:
                    self.rebound_action(game_map, point, nr)
                break

    def update(self, game_map):
        # Set The Speed To 20 For The First Time
        # Only When Having 4 Output Nodes With Speed Up and Down
        if not self.speed_set:
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

        set_position(self, position_tmp)

        # Calculate Four Corners
        # Length Is Half The Side
        aus_pixel = 0 * f
        length = 0.5 * CAR_SIZE_X + aus_pixel
        width = 0.5 * CAR_SIZE_Y + aus_pixel
        d = math.sqrt(length ** 2 + width ** 2)
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.carangle + 23))) * d,
                    self.center[1] + math.sin(math.radians(360 - (self.carangle + 23))) * d]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.carangle - 23))) * d,
                     self.center[1] + math.sin(math.radians(360 - (self.carangle - 23))) * d]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.carangle + 157))) * d,
                       self.center[1] + math.sin(math.radians(360 - (self.carangle + 157))) * d]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.carangle + 203))) * d,
                        self.center[1] + math.sin(math.radians(360 - (self.carangle + 203))) * d]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        self.left_rad = [self.center[0] + math.cos(math.radians(360 - (self.carangle + 23))) * (d - 6),
                         self.center[1] + math.sin(math.radians(360 - (self.carangle + 23))) * (d - 6)]
        self.right_rad = [self.center[0] + math.cos(math.radians(360 - (self.carangle - 23))) * (d - 6),
                          self.center[1] + math.sin(math.radians(360 - (self.carangle - 23))) * (d - 6)]

        # Check Collisions And Clear Radars  检查碰撞
        self.check_collision(game_map)
        self.radars.clear()
        # Draw tracks
        if simulation.drawtracks:
            self.draw_track(game_map)
        # From -90 To 120 With Step-Size 45 Check Radar
        self.check_radars_enable()
        if self.radars_enable:
            for d in range(-self.radar_angle, self.radar_angle + 1, self.radar_angle):
                self.check_radar(d, game_map)

            self.radar_dist = self.get_radars_dist()
            self.bit_volt_wert_list = self.linearisierungDA()

    def Lenkeinschlagsänderung(self):
        # 15°  直径125cm

        angle_rad = math.radians(self.radangle)  # 前轮转过的角度转换后的弧度值
        car_radius = int(CAR_Radstand / math.tan(angle_rad))  # 轮距CAR_Radstand
        theta = math.degrees(self.speed / car_radius)

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
            self.radars_enable = self.angle_enable = self.drawradar_enable = True
        else:
            self.radars_enable = False
            self.angle_enable, self.drawradar_enable = False, False

    # 传出旋转圆的半径 将小车的carangle 改到self.carangle

    def Geschwindigkeit(self, power):
        # self.power =   # 等于motorleisung的函数 百分比？
        # reibungsköffizient=0  # 摩擦力系数
        # luftwiderstandsköffizient=0  # 空气阻力系数
        # g=9.8 rho = 0 querschnittsfläche= 0  # 横截面积
        # self.reibung = reibungsköffizient * self.gewicht * g  # 摩擦力
        # self.luftwiderstand=luftwiderstandsköffizient * 0.5 * rho * querschnittsfläche * (self.speed ** 2)  # 空气阻力
        if power == 0:
            speed = 0
        else:
            speed = -0.0496 * (
                    power ** 2) + 9.008 * power + 31.8089
            speed = real_to_sim(speed / 100)

        # self.beschleunigung= (self.power - self.reibung - self.luftwiderstand)/self.gewicht  # 加速度
        # beschleunigungänderung = self.beschleunigung * time_step

        # max(0 , self.speed + beschleunigungänderung)
        # self.distance += self.speed * time_step
        return speed

    def getmotorleistung(self,fwert):
        if (fwert < 18 and fwert > -18):
            return 0
        elif (fwert >= 18 and fwert <= 100):
            return fwert / 100 * 100
        elif (fwert <= -18 and fwert >= -100):
            return (fwert / 100) * (-1) * 100

    def getwinkel(self,swert):
        if (swert == 0):
            return 0
        elif (swert >= 10):
            return 10
        elif (swert <= -10):
            return -10
        else:
            return swert