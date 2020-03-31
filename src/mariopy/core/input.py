import sys

import pygame
from pygame.locals import K_LEFT, K_RIGHT, K_SPACE, K_UP, K_LSHIFT

class Input:
    def __init__(self, entity):
        self.mouseX = 0
        self.mouseY = 0
        self.entity = entity

    def checkForInput(self):
        self.checkForKeyboardInput()
        self.checkForQuitAndRestartInputEvents()

    def checkForKeyboardInput(self):
        keys = pygame.key.get_pressed()

        if keys[K_LEFT] and not keys[K_RIGHT]:
            self.entity.traits["goTrait"].direction = -1
        elif keys[K_RIGHT] and not keys[K_LEFT]:
            self.entity.traits["goTrait"].direction = 1
        else:
            self.entity.traits['goTrait'].direction = 0

        jumping = keys[K_SPACE] or keys[K_UP]
        self.entity.traits['jumpTrait'].jump(jumping)

        self.entity.traits['goTrait'].boost = keys[K_LSHIFT]

    def checkForQuitAndRestartInputEvents(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and \
                (event.key == pygame.K_ESCAPE or event.key == pygame.K_F5):
                self.entity.pause = True
                self.entity.pauseObj.createBackgroundBlur()
