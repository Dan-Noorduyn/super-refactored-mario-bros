import pygame
from core.heap_of_shit import Dashboard, Level, Menu, Mario
from resources.display import SCREEN

def main():
    max_frame_rate = 60
    dashboard = Dashboard(SCREEN, 8)
    level = Level(SCREEN, dashboard)
    menu = Menu(SCREEN, dashboard, level)

    while not menu.start:
        menu.update()

    mario = Mario(0, 0, level, SCREEN, dashboard)
    clock = pygame.time.Clock()

    while not mario.restart:
        pygame.display.set_caption("Super Mario running with {:d} FPS".format(int(clock.get_fps())))
        if mario.pause:
            mario.pauseObj.update()
        else:
            level.drawLevel(mario.camera)
            dashboard.update()
            mario.update()
        pygame.display.update()
        clock.tick(max_frame_rate)
    main()

if __name__ == "__main__":
    main()