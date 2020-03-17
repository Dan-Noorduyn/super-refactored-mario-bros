import pygame
from core.old_code import DASHBOARD, LEVEL, MENU
# from core.old_code import Mario

MAX_FRAME_RATE: int = 60

class Mario(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image: pygame.Surface = pygame.Surface()

    def update(self):
        ...
    
    def update_image(self):
        ...


class _Game_Controller():
    def __init__(self):
        self.__mario = Mario()
        self.__clock = pygame.time.Clock()

    def run(self):
        while True:
            MENU.run()

            pygame.display.set_caption("Super Refactored Mario Python 🍄")
            while not self.__mario.restart:
                # pygame.display.set_caption("Super Mario running with {:d} FPS".format(int(clock.get_fps())))
                if self.__mario.pause:
                    self.__mario.pauseObj.update()
                else:
                    LEVEL.drawLevel(self.__mario.camera)
                    DASHBOARD.update()
                    self.__mario.update()
                pygame.display.update()
                self.__clock.tick(MAX_FRAME_RATE)

# def main():
    # # mario = Mario(0, 0)
    # mario: Mario = Mario()
    # clock: pygame.time.Clock = pygame.time.Clock()

    # while not mario.restart:
    #     pygame.display.set_caption("Super Mario running with {:d} FPS".format(int(clock.get_fps())))
    #     if mario.pause:
    #         mario.pauseObj.update()
    #     else:
    #         LEVEL.drawLevel(mario.camera)
    #         DASHBOARD.update()
    #         mario.update()
    #     pygame.display.update()
    #     clock.tick(MAX_FRAME_RATE)
    # main()

if __name__ == "__main__":
    # main()
    GAME_CONTROLLER = _Game_Controller()
