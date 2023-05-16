import math
import random
import sys
import os
import time
from typing import Tuple
import datetime
import neat
import numpy as np
import pygame
import pickle
import pygame.freetype

from PIL import Image
import car
from car import Car
from toggle_button import ToggleButton

f = car.f

WIDTH = 1920 * f  #
HEIGHT = 1080 * f
window_size = (WIDTH, HEIGHT)

time_flip = 0.01  # 10ms

# CAR_SIZE_X = 23.75 * 2 * f
# CAR_SIZE_Y = 10 * 2 * f

BORDER_COLOR: tuple[int, int, int] = (255, 255, 255)  # Color To Crash on Hit

current_generation = 0  # Generation counter
paused = False
file_text = ""

# Initialize PyGame And The Display
pygame.init()
screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)  # , pygame.FULLSCREEN

# 创建按钮
positionx = WIDTH * 0.7 * f
positiony = HEIGHT - 180 * f
font = pygame.freetype.SysFont("Arial", 19)

text_box_rect = pygame.Rect(positionx * 0.73, positiony + 40, 200, 30)
aufnahmen_button = pygame.Rect(positionx, positiony, 100, 30)
recover_button = pygame.Rect(positionx, positiony + 40, 100, 30)
switch_3button = ToggleButton(positionx * 1.2, positiony,
                              'Collision-Model: Crash', 'Collision-Model: Stop', 'Collision-Model: Rebound')
switch_2button = ToggleButton(switch_3button.rect.x, positiony + switch_3button.rect.height + 5
                              , "Sensor Enabled", "Sensor Unable", "")
switch_3button.draw(screen)
switch_2button.draw(screen)


def run_simulation(genomes, config):
    # Empty Collections For Nets and Cars
    map_text = "Rmap.png"
    nets = []
    cars = []

    # For All Genomes Passed Create A New Neural Network
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        # _init__(self, position, carangle, speed, speed_set, radars,  bit_volt_wert_list, distance, time)
        # position anfang:[790 * f, 825 * f]  [210 * f, 250 * f], [632 * f, 682 * f]310°
        new_car = Car([790 * f, 825 * f], 0, 18, False, [], [], 0, 0)
        cars.append(new_car)

    # Clock Settings
    # Font Settings & Loading Map
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 15)
    alive_font = pygame.font.SysFont("Arial", 10)
    game_map = pygame.image.load(map_text).convert()  # Convert Speeds Up A Lot
    game_map = pygame.transform.scale(game_map, window_size)

    global current_generation, paused, file_text
    current_generation += 1

    # Simple Counter To Roughly Limit Time (Not Good Practice)
    counter = 0

    while True:
        # im Zeitpunkt pruefen
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # 当再次按下空格键时，恢复游戏
                        paused = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if aufnahmen_button.collidepoint(event.pos):
                        paused = False

        # Exit On Quit Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            # pause == space
            elif event.type == pygame.KEYDOWN:
                # space ==pause
                if event.key == pygame.K_SPACE:
                    paused = True

                # 处理文本输入 Textbox
                elif event.unicode.isalnum():
                    file_text += event.unicode
                elif event.key == pygame.K_BACKSPACE:
                    file_text = file_text[:-1]

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 处理按钮BUTTON_Aufnahmen
                if aufnahmen_button.collidepoint(event.pos):
                    moment_aufnahmen(cars)
                    paused = True
                    # pygame.time.wait(500)  # warten 3 sekunden
                # RECOVER button
                if recover_button.collidepoint(event.pos):
                    print(f"file recovered: {file_text}")
                    cars = moment_recover(file_text)

            switch_3button.handle_event(event, 3)
            switch_2button.handle_event(event, 2)

        # Check If Car Is Still Alive
        # Increase Fitness If Yes And Break Loop If Not
        still_alive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                still_alive += 1
                car.update(game_map)
                #   genomes[i][1].fitness += car.get_reward()

        if still_alive == 0:
            break

        # Draw Map And All Cars That Are Alive
        screen.blit(game_map, (0, 0))
        for car in cars:
            if car.is_alive():
                car.draw(screen)

        # 车的转向操作************************************************************************************
        regelung(cars)

        # Once sumtime
        counter += 1
        if counter == 100 * 30:  # Stop After 100FPS * S
            break

        # Display Info------------------------------------------------------------------------------------
        text = generation_font.render("Generation: " + str(current_generation), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (900 / 4 * f, 450 / 2 * f)
        screen.blit(text, text_rect)
        text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (900 / 4 * f, 490 / 2 * f)
        screen.blit(text, text_rect)

        # Car info_Text
        car_info_lines = data_text(cars)
        for i, line in enumerate(car_info_lines):
            font.render_to(screen, (315*f, 285*f + i * 20), line, (255, 0, 100))

        pygame.draw.rect(screen, pygame.Color('red'), aufnahmen_button)
        pygame.draw.rect(screen, pygame.Color('blue'), recover_button)
        pygame.draw.rect(screen, pygame.Color('gray'), text_box_rect)

        font.render_to(screen, (aufnahmen_button.x + 5, aufnahmen_button.y + 5), "Aufnahmen", pygame.Color('white'))
        font.render_to(screen, (recover_button.x + 5, recover_button.y + 5), "File_Recover", pygame.Color('white'))
        # screen.blit(recover_button_text, (recover_button.x + 5, recover_button.y + 5))
        font.render_to(screen, (text_box_rect.x + 5, text_box_rect.y + 5), file_text, pygame.Color('black'))
        # screen.blit(text_surface, (text_box_rect.x + 5, text_box_rect.y + 5))

        switch_3button.draw(screen)
        switch_2button.draw(screen)

        pygame.display.flip()
        clock.tick(1 / time_flip)  # 100 FPS 10ms


def regelung(cars):
    # For Each Car Get The Acton It Takes
    for i, car in enumerate(cars):
        if car.radars_enable:
            jia = 1.5 * f  # 注意：是像素加速度 不是实际的 加速度大小

            if car.angle_enable:

                distcm = []
                dist = car.radar_dist
                for distpx in dist:
                    distcm.append(sim_to_real(distpx))

                if distcm[0] < 145 or distcm[2] < 145:
                    if distcm[0] < distcm[2]:
                        car.radangle = +15
                    if distcm[0] > distcm[2]:
                        car.radangle = -15

                if distcm[0] > 145 and distcm[2] > 145:
                    if 0 < car.carangle < 90:
                        car.radangle = 15
                    elif 90 < car.carangle < 180:
                        car.radangle = -15
    # # For Each Car Get The Acton It Takes
    # for i, car in enumerate(cars):
    #     if car.radars_enable:
    #         jia = 1.5 * f  # 注意：是像素加速度 不是实际的 加速度大小
    #
    #         if car.angle_enable:
    #
    #             distcm = []
    #             dist = car.radar_dist
    #             for distpx in dist:
    #                 distcm.append(sim_to_real(distpx))
    #
    #             if distcm[0] < 145 or distcm[2] < 145:
    #                 if distcm[0] < distcm[2]:
    #                     car.carangle += 10
    #                 if distcm[0] > distcm[2]:
    #                     car.carangle -= 10
    #
    #             if distcm[0] > 145 and distcm[2] > 145:
    #                 if 0 < car.carangle < 90:
    #                     car.carangle += 10
    #                 elif 90 < car.carangle < 180:
    #                     car.carangle -= 10


def moment_aufnahmen(cars):
    count = 1
    date = str(datetime.datetime.now().strftime("%d%M%S"))
    doc_text = "Momentaufnahme_%d_%s.pkl" % (count, date)
    # 文件地址
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'MomentAufnahme', doc_text)
    # 文件data
    data_to_serialize = []
    for acar in cars:
        data_to_serialize.append(acar.get_data_to_serialize())

    # 将每个Surface对象转换为Image对象并将其添加到列表中
    with open(file_path, 'wb') as auf:
        pickle.dump(data_to_serialize, auf)

    count += 1


def moment_recover(file_text_date):
    recover_cars = []
    count = 1
    date = "085931"
    if file_text != "":
        date = file_text_date

    file_path = os.path.abspath(f"MomentAufnahme/Momentaufnahme_{count}_{date}.pkl")
    with open(file_path, 'rb') as ein:
        deserialized_data = pickle.load(ein)
        print(deserialized_data)

    for data in deserialized_data:
        recover_cars.append(
            Car(data['position'],
                data['carangle'],
                data['speed'],
                data['speed_set'],
                data['radars'],
                data['analog_wert_list'],
                data['distance'],
                data['time']))

    return recover_cars


def sim_to_real(simpx):
    realcm = (simpx * 1900) / WIDTH  #  19米和图片宽度WIDTH 图片上的960
    return realcm


def real_to_sim(realcm):
    simpx = realcm * WIDTH / 1900
    return simpx


# return text Atrribute
def data_text(cars):
    for car in cars:
        car_info = \
            f"Center Position: " + \
            ", ".join([f"{pos/f:.0f}" for pos in car.center]) \
            + "\n" \
\
            f"Angle: {car.carangle:.2f} \n" \
            f"Speed: {car.speed:.2f}( px/10ms)    {sim_to_real(car.speed):.2f}( cm/10ms) \n" \
            f"Speed Set: {car.speed_set}\n    \n" +\
\
            f"Radars Beruehrungspunkt: \n " + \
            "    "+", ".join([f"{rad[0]}" for i, rad in enumerate(car.radars)]) \
            + "\n" \
 \
              f"Radars dist(px): " + ", " \
                .join([f"{rad[1]}px" for i, rad in enumerate(car.radars)]) \
            + "\n" \
 \
              f"Radars realdist(cm): " + ", " \
                .join([f"{sim_to_real(rad[1]):.2f}cm" for i, rad in enumerate(car.radars)]) \
            + "\n" \
 \
              f"Analog Wert(Volt) List: " + ", ".join(
                [f"{wertV[1]:.2f}V" for i, wertV in enumerate(car.bit_volt_wert_list)]) \
            + "\n" \
\
              f"Digital Wert(bit) List: " + ", ".join(
                [f"{wertbit[0]:.0f}" for i, wertbit in enumerate(car.bit_volt_wert_list)]) \
            + "\n\n" \
              f"Distance: {car.distance:.1f} px   {sim_to_real(car.distance):.1f}cm\n" \
              f"Time: {car.time:.2f} s  \n"
        info_lines = car_info.splitlines()

        return info_lines

