import pygame
from resources.level import LEVEL
from resources.Menus import MainMenu, PauseMenu
from resources.dashboard import DASHBOARD
from resources.sound import *
from core.mario import *

MAX_FRAME_RATE: int = 60


class _Game_Controller():
    def __init__(self):
        self.__clock = pygame.time.Clock()
        self.menu = MainMenu()

    def _stage_clear(self):
        SOUND_CONTROLLER.stop_sfx()
        SOUND_CONTROLLER.stop_music()
        SOUND_CONTROLLER.play_music(STAGE_CLEAR)

    def run(self):
        try:
            while True:
                pygame.display.set_caption("Super Refactored Mario Python 🍄")
                self.menu.run()

                mario = Mario(0, 0)
                _flag = True
                _time_flag = True
                t = 0
                wait = 0
                while not mario.restart:
                    if mario.pause:
                        mario.pauseObj.update()
                    else:
                        if mario.collision.rightLevelBorderReached():
                            _time_flag = False
                            if _flag:
                                self._stage_clear()
                                DASHBOARD.state = "next"
                                _flag = False

                            if DASHBOARD.time > 0:
                                if t > 60:
                                    SOUND_CONTROLLER.play_sfx(COIN_SOUND)
                                    DASHBOARD.time -= 1
                                    DASHBOARD.points += 50
                                    SOUND_CONTROLLER.play_sfx(COIN_SOUND)
                                LEVEL.drawLevel(mario.camera)
                                DASHBOARD.update()
                                mario.input.checkForInput()
                                mario.drawMario()
                                pygame.display.update()
                                t += 1
                            else:
                                if SOUND_CONTROLLER.playing_sfx():
                                    SOUND_CONTROLLER.stop_sfx()
                                elif not SOUND_CONTROLLER.playing_music():
                                    wait += 1
                                    if not (wait % 120):
                                        if self.menu.curr_selected_level < self.menu.level_count:
                                            next_level = self.menu.level_names[self.menu.curr_selected_level]
                                            self.menu.curr_selected_level += 1
                                            LEVEL.loadLevel(next_level)
                                            DASHBOARD.level_name = next_level[len(next_level)-3:len(next_level)]
                                            DASHBOARD.state = "start"
                                            DASHBOARD.time = 420
                                            mario.next_level()
                                            SOUND_CONTROLLER.play_music(SOUNDTRACK)
                                            wait = 0
                                            t = 0
                                            _time_flag = True
                                            _flag = True
                                        else:
                                            highscore_file = open("resources/highscore.txt","r")
                                            if highscore_file.mode == 'r':
                                                contents = highscore_file.read()
                                                highscore_file.close()
                                                if int(contents) < DASHBOARD.points:
                                                    highscore_file = open("resources/highscore.txt", "w+")
                                                    highscore_file.write(str(DASHBOARD.points))
                                                highscore_file.close()
                                            DASHBOARD.reset()
                                            mario.restart = True
                        elif DASHBOARD.time < 100 and _time_flag:
                            SOUND_CONTROLLER.stop_music()
                            SOUND_CONTROLLER.play_music(HURRY_OVERWORLD)
                            _time_flag = False
                        else:
                            LEVEL.drawLevel(mario.camera)
                            LEVEL.updateEntities(mario.camera)
                            DASHBOARD.update()
                            mario.update()
                    DASHBOARD.update()
                    pygame.display.update()
                    self.__clock.tick(MAX_FRAME_RATE)
                DASHBOARD.reset()
                self.menu.start = False
        except SystemExit:
            return


if __name__ == "__main__":
    GAME_CONTROLLER = _Game_Controller()
    GAME_CONTROLLER.run()
