import pygame
import math
import cffi
import time
from abc import ABC, abstractmethod
import car

f = car.f

WIDTH = 1920 * f  #
HEIGHT = 1080 * f

ffi = cffi.FFI()
# Definition der Schnittstelle zu C-Funktionen
ffi.cdef("""
void fahr(int f);
int getfwert();
void servo(int s);
int getswert();
void getfahr(int8_t leistung);
void regelungtechnik();
void getabstandvorne(uint16_t anlagwort);
void getabstandrechts(uint16_t anlagwort,uint8_t cosAlpha);
void getabstandlinks(uint16_t anlagwort, uint8_t cosAlpha);
uint16_t get_abstandvorne();
uint16_t get_abstandrechts();
uint16_t get_abstandlinks();
int8_t getServo();
void getservo(int8_t winkel);
""")

# import file
lib = ffi.dlopen("./IF/x64/Debug/IF.dll")


class MyInterface(ABC):
    @abstractmethod
    def regelungtechnik_c(self):
        pass

    @abstractmethod
    def regelungtechnik_python(self):
        pass


class Interface(MyInterface):

    @staticmethod
    def regelungtechnik_c(cars):
        for i, car in enumerate(cars):
            if car.radars_enable and car.regelung_enable:
                lib.getfahr(int(car.power))
                lib.getservo(int(car.radangle))
                anlagewertrechts = car.bit_volt_wert_list[0][0]
                anlagewertvorne = car.bit_volt_wert_list[1][0]
                anlagewertlinks = car.bit_volt_wert_list[2][0]
                radians = math.radians(car.radar_angle)
                cosAlpha = int(math.cos(radians) * 10)
                lib.getabstandvorne(anlagewertvorne)
                lib.getabstandrechts(anlagewertrechts, cosAlpha)
                lib.getabstandlinks(anlagewertlinks, cosAlpha)
                lib.regelungtechnik()
                car.fwert = lib.getfwert()
                car.swert = lib.getswert()
            car.radangle = (-1)*car.servo2IstWinkel(car.getwinkel(car.swert))
            car.getmotorleistung(car.fwert)
            car.speed = car.Geschwindigkeit(car.power)

    @staticmethod
    def regelungtechnik_python(cars):
        for i, car in enumerate(cars):
            if car.radars_enable and car.regelung_enable:
                start_time = time.time()
                distcm = []
                dist = car.radar_dist
                for distpx in dist:
                    distcm.append(sim_to_real(distpx))

                # Richtung
                kp2 = 1.0
                if distcm[0] < 130 or distcm[2] < 130:
                    sollwert4 = 0
                    diff = distcm[2] - distcm[0]
                    car.swert = (-1)*(diff-sollwert4) * kp2  # gleich mit C

                # Geschwindigkeit
                k1 = 1.1000000149011613
                k2 = 1.1
                k3 = 1.1
                kp1 = 1.0

                sollwert1 = distcm[1] * k1
                sollwert2 = distcm[1] * k2
                sollwert3 = distcm[1] * k3

                if distcm[1] > 100:
                    if car.power < 60:
                        car.fwert += (sollwert1 - distcm[1]) * kp1 + 18
                        if car.fwert > 60:
                            car.fwert = 60

                elif 50 < distcm[1] < 100:
                    if car.power > 18:
                        car.fwert -= (sollwert2 - distcm[1]) * kp1
                        if car.fwert < 18:
                            car.fwert = 18

                elif distcm[1] < 50 :
                    car.fwert = (-1) * (sollwert3 - distcm[1]) * kp1 - 18
                    car.swert = (-1)*( distcm[2]-distcm[0] ) * kp2-10

                else:
                    pass


            car.radangle = (-1) * car.servo2IstWinkel(car.getwinkel(car.swert))
            car.getmotorleistung(car.fwert)
            car.speed = car.Geschwindigkeit(car.power)

    @staticmethod
    def draw_dialog(screen):
        dialog_width = 500
        dialog_height = 200
        dialog_x = (WIDTH - dialog_width) // 2
        dialog_y = (HEIGHT - dialog_height) // 2
        border_size = 4
        border_color = (0, 0, 0)
        # dialog windows
        dialog_surface = pygame.Surface((dialog_width, dialog_height))
        dialog_surface.fill((255, 255, 255))  # backgroudn white
        pygame.draw.rect(dialog_surface, border_color, (0, 0, dialog_width, dialog_height), border_size)
        # Button and text
        font = pygame.font.Font(None, 24)
        text = font.render("Sind Sie sicher, dass Sie die Reglungstechnik ändern wollen?", True, (0, 0, 0))  #
        text_rect = text.get_rect(center=(dialog_width // 2, dialog_height // 2 - 20))
        dialog_surface.blit(text, text_rect)

        screen.blit(dialog_surface, (dialog_x, dialog_y))
        pygame.display.flip()

    @staticmethod
    def draw_button(screen, text, text_color, button_color, positionx, positiony, button_width, button_height,
                    button_rect):
        pygame.draw.rect(screen, button_color, (positionx, positiony, button_width, button_height))
        font = pygame.font.Font(None, 24)
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)

    @staticmethod
    def getabstandvorne1():
        abstand = lib.get_abstandvorne()

        return abstand

    @staticmethod
    def getabstandlinks1():
        abstand = lib.get_abstandlinks()

        return abstand

    @staticmethod
    def getabstandrechts1():
        abstand = lib.get_abstandrechts()

        return abstand


def sim_to_real(simpx):
    realcm = (simpx * 1900) / WIDTH
    return realcm


def real_to_sim(realcm):
    simpx = realcm * WIDTH / 1900
    return simpx
