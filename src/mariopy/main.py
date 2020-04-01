import pygame

from core.mario import Mario
from resources.dashboard import DASHBOARD
from resources.level import LEVEL
from resources.Menus import MainMenu
from resources.sound import (COIN_SOUND, HURRY_OVERWORLD, SOUND_CONTROLLER,
                             SOUNDTRACK, STAGE_CLEAR)

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
                    mario.pause_obj.update()
                else:
                    if mario.collision.right_level_border_reached():
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
                            LEVEL.draw_level(mario.camera)
                            DASHBOARD.update()
                            mario.input.check_for_input()
                            mario.draw_mario()
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
                                        LEVEL.load_level(next_level)
                                        DASHBOARD.level_name = next_level[len(next_level)-3:len(next_level)]
                                        DASHBOARD.state = "start"
                                        DASHBOARD.time = 400
                                        DASHBOARD.earned_points = 0
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
                        LEVEL.draw_level(mario.camera)
                        LEVEL.update_entities(mario.camera)
                        DASHBOARD.update()
                        mario.update()
                pygame.display.update()
                self.__clock.tick(MAX_FRAME_RATE)
            DASHBOARD.reset()
            self.menu.start = False


if __name__ == "__main__":
    try:
        _Game_Controller().run()
    except SystemExit:
        ...
    except KeyboardInterrupt:
        ...

