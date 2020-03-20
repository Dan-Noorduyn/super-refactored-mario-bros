import pygame
import sys
import json
import os

from .level import LEVEL
from .display import SCREEN, SPRITE_COLLECTION, Spritesheet
from .dashboard import DASHBOARD
from scipy.ndimage.filters import gaussian_filter
from .sound import SOUNDTRACK, SOUND_CONTROLLER


class GaussianBlur:
    def __init__(self):
        self.kernel_size = 7

    def filter(self, srfc, xpos, ypos, width, height):
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
        self.pause_srfc = GaussianBlur().filter(SCREEN, 0, 0, 640, 480)
        self.dot = self.spritesheet.image_at(
            0, 150, 2, colorkey=[255, 0, 220], ignoreTileSize=True
        )
        self.gray_dot = self.spritesheet.image_at(
            20, 150, 2, colorkey=[255, 0, 220], ignoreTileSize=True
        )

    def run(self):
        while not self.start:
            self.update()

    def update(self):
        SCREEN.blit(self.pause_srfc, (0, 0))
        DASHBOARD.drawText("PAUSED", 120, 160, 68)
        DASHBOARD.drawText("CONTINUE", 150, 280, 32)
        DASHBOARD.drawText("BACK TO MENU", 150, 320, 32)
        self.drawDot()
        pygame.display.update()
        self.checkInput()

    def drawDot(self):
        if self.state == 0:
            SCREEN.blit(self.dot, (100, 275))
            SCREEN.blit(self.gray_dot, (100, 315))
        elif self.state == 1:
            SCREEN.blit(self.dot, (100, 315))
            SCREEN.blit(self.gray_dot, (100, 275))

    def checkInput(self):
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

    def createBackgroundBlur(self):
        self.pause_srfc = GaussianBlur().filter(SCREEN, 0, 0, 640, 480)


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
            colorkey=[255, 0, 220],
            ignoreTileSize=True,
            xTileSize=180,
            yTileSize=88,
        )
        self.menu_dot = self.spritesheet.image_at(
            0, 150, 2, colorkey=[255, 0, 220], ignoreTileSize=True
        )
        self.menu_dot2 = self.spritesheet.image_at(
            20, 150, 2, colorkey=[255, 0, 220], ignoreTileSize=True
        )
        self.loadSettings("./settings.json")

    def run(self):
        DASHBOARD.state = "menu"
        while not self.start:
            self.update()

    def update(self):
        self.checkInput()
        if self.in_choosing_level:
            return

        self.drawMenuBackground()
        DASHBOARD.update()

        if not self.in_settings:
            self.drawMenu()
        else:
            self.drawSettings()

    def drawDot(self):
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

    def loadSettings(self, url):
        try:
            with open(url) as jsonData:
                data = json.load(jsonData)
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
            self.saveSettings("./settings.json")

    def saveSettings(self, url):
        data = {"sound": self.music, "sfx": self.sfx}
        with open(url, "w") as outfile:
            json.dump(data, outfile)

    def drawMenu(self):
        self.drawDot()
        DASHBOARD.drawText("CHOOSE LEVEL", 180, 280, 24)
        DASHBOARD.drawText("SETTINGS", 180, 320, 24)
        DASHBOARD.drawText("EXIT", 180, 360, 24)

    def drawMenuBackground(self, withBanner=True):
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
        if(withBanner):
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

    def drawSettings(self):
        self.drawDot()
        DASHBOARD.drawText("MUSIC", 180, 280, 24)
        if self.music:
            DASHBOARD.drawText("ON", 340, 280, 24)
        else:
            DASHBOARD.drawText("OFF", 340, 280, 24)
        DASHBOARD.drawText("SFX", 180, 320, 24)
        if self.sfx:
            DASHBOARD.drawText("ON", 340, 320, 24)
        else:
            DASHBOARD.drawText("OFF", 340, 320, 24)
        DASHBOARD.drawText("BACK", 180, 360, 24)

    def chooseLevel(self):
        self.drawMenuBackground(False)
        self.in_choosing_level = True
        self.level_names = self.loadlevel_names()
        self.drawLevelChooser()

    def drawBorder(self, x, y, width, height, color, thickness):
        pygame.draw.rect(SCREEN, color, (x, y, width, thickness))
        pygame.draw.rect(SCREEN, color, (x, y+width, width, thickness))
        pygame.draw.rect(SCREEN, color, (x, y, thickness, width))
        pygame.draw.rect(SCREEN, color, (x+width, y, thickness,
                                         width+thickness))

    def drawLevelChooser(self):
        j = 0
        offset = 75
        textOffset = 90
        for i, levelName in enumerate(self.level_names):
            if self.curr_selected_level == i+1:
                color = (255, 255, 255)
            else:
                color = (150, 150, 150)
            if i < 3:
                DASHBOARD.drawText(levelName, 175*i+textOffset, 100, 12)
                self.drawBorder(175*i+offset, 55, 125, 75, color, 5)
            else:
                DASHBOARD.drawText(levelName, 175*j+textOffset, 250, 12)
                self.drawBorder(175*j+offset, 210, 125, 75, color, 5)
                j += 1

    def loadlevel_names(self):
        files = []
        res = []
        for r, d, f in os.walk("./resources/levels"):
            for file in f:
                files.append(os.path.join(r, file))
        for f in files:
            res.append(os.path.split(f)[1].split(".")[0])
        self.level_count = len(res)
        res.sort()
        return res

    def checkInput(self):
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
                        self.__init__(SCREEN, DASHBOARD, LEVEL)
                    else:
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_UP:
                    if self.in_choosing_level:
                        if self.curr_selected_level > 3:
                            self.curr_selected_level -= 3
                            self.drawLevelChooser()
                    if self.state > 0:
                        self.state -= 1
                elif event.key == pygame.K_DOWN:
                    if self.in_choosing_level:
                        if self.curr_selected_level+3 <= self.level_count:
                            self.curr_selected_level += 3
                            self.drawLevelChooser()
                    if self.state < 2:
                        self.state += 1
                elif event.key == pygame.K_LEFT:
                    if self.curr_selected_level > 1:
                        self.curr_selected_level -= 1
                        self.drawLevelChooser()
                elif event.key == pygame.K_RIGHT:
                    if self.curr_selected_level < self.level_count:
                        self.curr_selected_level += 1
                        self.drawLevelChooser()
                elif event.key == pygame.K_RETURN:
                    if self.in_choosing_level:
                        self.in_choosing_level = False
                        DASHBOARD.state = "start"
                        DASHBOARD.time = 420
                        LEVEL.loadLevel(self.level_names[self.curr_selected_level-1])
                        DASHBOARD.level_name = self.level_names[self.curr_selected_level-1].split("Level")[
                            1]
                        self.start = True
                        return
                    if not self.in_settings:
                        if self.state == 0:
                            self.chooseLevel()
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
                            self.saveSettings("./settings.json")
                        elif self.state == 1:
                            if self.sfx:
                                SOUND_CONTROLLER.mute_sfx()
                                self.sfx = False
                            else:
                                SOUND_CONTROLLER.unmute_sfx()
                                self.sfx = True
                            self.saveSettings("./settings.json")
                        elif self.state == 2:
                            self.in_settings = False
        pygame.display.update()
