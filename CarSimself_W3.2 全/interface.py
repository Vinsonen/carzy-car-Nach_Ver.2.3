import pygame
import math
import cffi
import car
from car import Car
f = 1

WIDTH = 1920 * f  #
HEIGHT = 1080 * f
ffi = cffi.FFI()
import car
# 定义C函数的接口
ffi.cdef("""
void fahr(int f);
  int getfwert();
 void servo(int s);
 int getservo();
  void getfahr(float leistung);
  void regelungtechnik();
  void getabstandvorne(uint16_t anlagwort);
   void getabstandrechts(uint16_t anlagwort,uint8_t cosAlpha);
  void getabstandlinks(uint16_t anlagwort, uint8_t cosAlpha);

""")


# 加载库文件
lib = ffi.dlopen("./IF/x64/Debug/IF.dll")
class Interface:
    @staticmethod
    def reglungtechnik_c(cars):
        for i, car in enumerate(cars):
            if car.radars_enable and car.regelung_enable:
                #jia = 1.5 * f  # 注意：是像素加速度 不是实际的 加速度大小
                lib.getfahr(car.power)
                anlagewertrechts = car.bit_volt_wert_list[0][0]
                anlagewertvorne = car.bit_volt_wert_list[1][0]
                anlagewertlinks = car.bit_volt_wert_list[2][0]
                radians = math.radians(car.radar_angle)
                cosAlpha = int(math.cos(radians) * 100)
                lib.getabstandvorne(anlagewertvorne)
                lib.getabstandrechts(anlagewertrechts, cosAlpha)
                lib.getabstandlinks(anlagewertlinks, cosAlpha)
                lib.regelungtechnik()
                car.fwert = lib.getfwert()
                car.swert = lib.getservo()
                car.radangle = (-1) * car.servo2IstWinkel(car.getwinkel(car.swert))
                car.power = car.getmotorleistung(car.fwert)
                car.speed = car.Geschwindigkeit(car.power)

    @staticmethod
    def reglungtechnik_python(cars):
        for i, car in enumerate(cars):
            if car.radars_enable and car.regelung_enable:
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



    @staticmethod
    def draw_dialog(screen):
        dialog_width = 500
        dialog_height = 200
        dialog_x = (WIDTH- dialog_width) // 2
        dialog_y = (HEIGHT - dialog_height) // 2
        border_size = 4
        border_color = (0, 0, 0)
        # 创建对话框表面
        dialog_surface = pygame.Surface((dialog_width, dialog_height))
        dialog_surface.fill((255, 255, 255))  # 设置对话框背景颜色为白色
        pygame.draw.rect(dialog_surface, border_color, (0, 0, dialog_width, dialog_height), border_size)
        # 在对话框表面上绘制文本和按钮
        font = pygame.font.Font(None, 24)
        text = font.render("Sind Sie sicher, dass Sie die Reglungstechnik ändern wollen?", True, (0, 0, 0))  # 设置文本内容和颜色
        text_rect = text.get_rect(center=(dialog_width // 2, dialog_height // 2 - 20))
        dialog_surface.blit(text, text_rect)


        screen.blit(dialog_surface, (dialog_x, dialog_y))

        # 更新窗口显示
        pygame.display.flip()

    @staticmethod
    def draw_button(screen,text,text_color,button_color,positionx,positiony,button_width,button_height,button_rect):
        pygame.draw.rect(screen,button_color,(positionx,positiony,button_width,button_height))
        font = pygame.font.Font(None, 24)
        text_surface = font.render(text, True, text_color)  # 创建文本表面
        text_rect = text_surface.get_rect(center=button_rect.center)  # 获取文本矩形位置
        screen.blit(text_surface, text_rect)
        # 绘制文本

def sim_to_real(simpx):
    realcm = (simpx * 1900) / WIDTH  # 19米和图片宽度WIDTH 图片上的960
    return realcm

def real_to_sim(realcm):
    simpx = realcm * WIDTH / 1900
    return simpx

