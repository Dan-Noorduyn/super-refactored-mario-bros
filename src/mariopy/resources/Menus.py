import json
import os
import sys

import pygame
from scipy.ndimage.filters import gaussian_filter

from resources.dashboard import DASHBOARD
from resources.display import SCREEN, SPRITE_COLLECTION, Spritesheet
from resources.level import LEVEL
from resources.sound import SOUND_CONTROLLER, SOUNDTRACK


class GaussianBlur:
    def __init__(self):
        self.kernel_size = 7

    def filter(self, srfc, width, height):
        nSrfc = pygame.Surface((width, height))
        pxa = pygame.surfarray.array3d(srfc)
        blurred = gaussian_filter(pxa, sigma=(self.kernel_size,
                                              self.kernel_size, 0))
        pygame.surfarray.blit_array(nSrfc, blurred)
        del pxa
        return nSrfc


class PauseMenu:
    def __init__(self, game_controller):
        self.game_controller = game_controller
        self.state = 0
        self.start = False
        self.spritesheet = Spritesheet("./resources/img/title_screen.png")
        self.pause_srfc = GaussianBlur().filter(SCREEN, SCREEN.get_width(), SCREEN.get_height())
        self.dot = self.spritesheet.image_at(
            0, 150, 2, color_key=[0, 0, 0], ignore_tile_size=True
        )
        self.gray_dot = self.spritesheet.image_at(
            20, 150, 2, color_key=[0, 0, 0], ignore_tile_size=True
        )

    def run(self):
        while not self.start:
            self.update()

    def update(self):
        SCREEN.blit(self.pause_srfc, (0, 0))
        DASHBOARD.draw_text("PAUSED", 120, 160, 68)
        DASHBOARD.draw_text("CONTINUE", 150, 280, 32)
        DASHBOARD.draw_text("BACK TO MENU", 150, 320, 32)
        self.draw_dot()
        pygame.display.update()
        self.check_input()

    def draw_dot(self):
        if self.state == 0:
            SCREEN.blit(self.dot, (100, 275))
            SCREEN.blit(self.gray_dot, (100, 315))
        elif self.state == 1:
            SCREEN.blit(self.dot, (100, 315))
            SCREEN.blit(self.gray_dot, (100, 275))

    def check_input(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_controller.pause = False
                    self.start = True
                elif event.key == pygame.K_RETURN:
                    if self.state == 0:
                        self.game_controller.pause = False
                        self.start = True
                    elif self.state == 1:
                        self.game_controller.restart = True
                elif event.key == pygame.K_UP:
                    if self.state > 0:
                        self.state -= 1
                elif event.key == pygame.K_DOWN:
                    if self.state < 1:
                        self.state += 1

    def create_background_blur(self):
        self.pause_srfc = GaussianBlur().filter(SCREEN, 640, 480)


class MainMenu:
    def __init__(self):
        self.start = False
        self.in_settings = False
        self.state = 0
        self.music = True
        self.sfx = True
        self.curr_selected_level = 1
        self.level_names = []
        self.in_choosing_level = False
        self.level_count = 0
        self.spritesheet = Spritesheet("./resources/img/title_screen.png")
        self.menu_banner = self.spritesheet.image_at(
            0,
            60,
            2,
            color_key=[255, 0, 220],
            ignore_tile_size=True,
            x_tile_size=180,
            y_tile_size=88,
        )
        self.menu_dot = self.spritesheet.image_at(
            0, 150, 2, color_key=[0, 0, 0], ignore_tile_size=True
        )
        self.menu_dot2 = self.spritesheet.image_at(
            20, 150, 2, color_key=[0, 0, 0], ignore_tile_size=True
        )
        self.load_settings("./settings.json")

    def run(self):
        DASHBOARD.state = "menu"
        DASHBOARD.lives = 3
        DASHBOARD.update()
        SOUND_CONTROLLER.play_music(SOUNDTRACK)
        while not self.start:
            self.update()

    def update(self):
        self.check_input()
        if self.in_choosing_level:
            return

        self.draw_menu_background()
        DASHBOARD.update()

        if not self.in_settings:
            self.draw_menu()
        else:
            self.draw_settings()

    def draw_dot(self):
        if self.state == 0:
            SCREEN.blit(self.menu_dot, (145, 273))
            SCREEN.blit(self.menu_dot2, (145, 313))
            SCREEN.blit(self.menu_dot2, (145, 353))
        elif self.state == 1:
            SCREEN.blit(self.menu_dot, (145, 313))
            SCREEN.blit(self.menu_dot2, (145, 273))
            SCREEN.blit(self.menu_dot2, (145, 353))
        elif self.state == 2:
            SCREEN.blit(self.menu_dot, (145, 353))
            SCREEN.blit(self.menu_dot2, (145, 273))
            SCREEN.blit(self.menu_dot2, (145, 313))

    def load_settings(self, url):
        try:
            with open(url) as json_data:
                data = json.load(json_data)
                if data["sound"]:
                    self.music = True
                    SOUND_CONTROLLER.unmute_music()
                    SOUND_CONTROLLER.play_music(SOUNDTRACK)
                else:
                    self.music = False
                    SOUND_CONTROLLER.mute_music()
                if data["sfx"]:
                    self.sfx = True
                    SOUND_CONTROLLER.unmute_sfx()
                else:
                    self.sfx = False
                    SOUND_CONTROLLER.mute_sfx()
        except (IOError, OSError):
            self.music = False
            self.sfx = False
            SOUND_CONTROLLER.mute_music()
            SOUND_CONTROLLER.mute_sfx()
            self.save_settings("./settings.json")

    def save_settings(self, url):
        data = {"sound": self.music, "sfx": self.sfx}
        with open(url, "w") as outfile:
            json.dump(data, outfile)

    def draw_menu(self):
        self.draw_dot()
        DASHBOARD.draw_text("CHOOSE LEVEL", 180, 280, 24)
        DASHBOARD.draw_text("SETTINGS", 180, 320, 24)
        DASHBOARD.draw_text("EXIT", 180, 360, 24)

        DASHBOARD.draw_text("HIGH", 20, 140, 15)
        DASHBOARD.draw_text("SCORE:", 20, 160, 15)
        highscore_file = open("resources/highscore.txt","r")
        if highscore_file.mode == 'r':
            contents = highscore_file.read()
            highscore_file.close()
            DASHBOARD.draw_text(contents.strip(), 20, 180, 15)

    def draw_menu_background(self, with_banner=True):
        for y in range(0, 13):
            for x in range(0, 20):
                SCREEN.blit(
                    SPRITE_COLLECTION.get("sky"),
                    (x * 32, y * 32),
                )
        for y in range(13, 15):
            for x in range(0, 20):
                SCREEN.blit(
                    SPRITE_COLLECTION.get("ground"),
                    (x * 32, y * 32),
                )
        if(with_banner):
            SCREEN.blit(self.menu_banner, (150, 80))
        SCREEN.blit(
            SPRITE_COLLECTION.get("mario_idle"),
            (2 * 32, 12 * 32),
        )
        SCREEN.blit(
            SPRITE_COLLECTION.get("bush_1"), (14 * 32, 12 * 32)
        )
        SCREEN.blit(
            SPRITE_COLLECTION.get("bush_2"), (15 * 32, 12 * 32)
        )
        SCREEN.blit(
            SPRITE_COLLECTION.get("bush_2"), (16 * 32, 12 * 32)
        )
        SCREEN.blit(
            SPRITE_COLLECTION.get("bush_2"), (17 * 32, 12 * 32)
        )
        SCREEN.blit(
            SPRITE_COLLECTION.get("bush_3"), (18 * 32, 12 * 32)
        )
        SCREEN.blit(SPRITE_COLLECTION.get("goomba-1"), (18.5*32, 12*32))

    def draw_settings(self):
        self.draw_dot()
        DASHBOARD.draw_text("MUSIC", 180, 280, 24)
        if self.music:
            DASHBOARD.draw_text("ON", 340, 280, 24)
        else:
            DASHBOARD.draw_text("OFF", 340, 280, 24)
        DASHBOARD.draw_text("SFX", 180, 320, 24)
        if self.sfx:
            DASHBOARD.draw_text("ON", 340, 320, 24)
        else:
            DASHBOARD.draw_text("OFF", 340, 320, 24)
        DASHBOARD.draw_text("BACK", 180, 360, 24)

    def choose_level(self):
        self.draw_menu_background(False)
        self.in_choosing_level = True
        self.level_names = self.load_level_names()
        self.draw_level_chooser()

    def draw_border(self, x, y, width, color, thickness):
        pygame.draw.rect(SCREEN, color, (x, y, width, thickness))
        pygame.draw.rect(SCREEN, color, (x, y+width, width, thickness))
        pygame.draw.rect(SCREEN, color, (x, y, thickness, width))
        pygame.draw.rect(SCREEN, color, (x+width, y, thickness,
                                         width+thickness))

    def draw_level_chooser(self):
        j = 0
        offset = 75
        text_offset = 90
        for i, level_name in enumerate(self.level_names):
            if self.curr_selected_level == i + 1:
                color = (255, 255, 255)
            else:
                color = (150, 150, 150)
            if i < 3:
                DASHBOARD.draw_text(level_name, 175*i+text_offset, 100, 12)
                self.draw_border(175*i+offset, 55, 125, color, 5)
            else:
                DASHBOARD.draw_text(level_name, 175*j+text_offset, 250, 12)
                self.draw_border(175*j+offset, 210, 125, color, 5)
                j += 1

    def load_level_names(self):
        files = []
        res = []
        for r, _, f in os.walk("./resources/levels"):
            for file in f:
                files.append(os.path.join(r, file))
        for f in files:
            res.append(os.path.split(f)[1].split(".")[0])
        self.level_count = len(res)
        res.sort()
        return res

    def check_input(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.in_choosing_level or self.in_settings:
                        self.in_choosing_level = False
                        self.in_settings = False
                        self.__init__()
                    else:
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_UP:
                    if self.in_choosing_level:
                        if self.curr_selected_level > 3:
                            self.curr_selected_level -= 3
                            self.draw_level_chooser()
                    if self.state > 0:
                        self.state -= 1
                elif event.key == pygame.K_DOWN:
                    if self.in_choosing_level:
                        if self.curr_selected_level+3 <= self.level_count:
                            self.curr_selected_level += 3
                            self.draw_level_chooser()
                    if self.state < 2:
                        self.state += 1
                elif event.key == pygame.K_LEFT:
                    if self.curr_selected_level > 1:
                        self.curr_selected_level -= 1
                        self.draw_level_chooser()
                elif event.key == pygame.K_RIGHT:
                    if self.curr_selected_level < self.level_count:
                        self.curr_selected_level += 1
                        self.draw_level_chooser()
                elif event.key == pygame.K_RETURN:
                    if self.in_choosing_level:
                        self.in_choosing_level = False
                        DASHBOARD.state = "start"
                        DASHBOARD.time = 400
                        LEVEL.load_level(self.level_names[self.curr_selected_level-1])
                        DASHBOARD.level_name = self.level_names[self.curr_selected_level-1].split("Level")[
                            1]
                        self.start = True
                        return
                    if not self.in_settings:
                        if self.state == 0:
                            self.choose_level()
                        elif self.state == 1:
                            self.in_settings = True
                            self.state = 0
                        elif self.state == 2:
                            pygame.quit()
                            sys.exit()
                    else:
                        if self.state == 0:
                            if self.music:
                                self.music = False
                                SOUND_CONTROLLER.stop_music()
                            else:
                                SOUND_CONTROLLER.play_music(SOUNDTRACK)
                                self.music = True
                            self.save_settings("./settings.json")
                        elif self.state == 1:
                            if self.sfx:
                                SOUND_CONTROLLER.mute_sfx()
                                self.sfx = False
                            else:
                                SOUND_CONTROLLER.unmute_sfx()
                                self.sfx = True
                            self.save_settings("./settings.json")
                        elif self.state == 2:
                            self.in_settings = False
        pygame.display.update()
