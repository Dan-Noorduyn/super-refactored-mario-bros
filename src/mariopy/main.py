import pygame
from resources.level import LEVEL
from core.old_code import DASHBOARD, MENU
from core.mario import *

MAX_FRAME_RATE: int = 60


class _Game_Controller():
    def __init__(self):
        self.__clock = pygame.time.Clock()

    def run(self):
        while True:
            pygame.display.set_caption("Super Refactored Mario Python 🍄")
            MENU.run()

            mario = Mario(0, 0)
            while not mario.restart:
                if mario.pause:
                    mario.pauseObj.update()
                else:
                    LEVEL.drawLevel(mario.camera)
                    DASHBOARD.update()
                    mario.update()
                pygame.display.update()
                self.__clock.tick(MAX_FRAME_RATE)
                



if __name__ == "__main__":
    GAME_CONTROLLER = _Game_Controller()
    GAME_CONTROLLER.run()
