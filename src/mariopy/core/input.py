import sys

import pygame
from pygame.locals import K_LEFT, K_RIGHT, K_SPACE, K_UP, K_LSHIFT

class Input:
    def __init__(self, entity):
        self.entity = entity

    def check_for_input(self):
        self.check_for_keyboard_input()
        self.check_for_quit_and_restart_input_events()

    def check_for_keyboard_input(self):
        keys = pygame.key.get_pressed()

        if keys[K_LEFT] and not keys[K_RIGHT]:
            self.entity.traits["GoTrait"].direction = -1
        elif keys[K_RIGHT] and not keys[K_LEFT]:
            self.entity.traits["GoTrait"].direction = 1
        else:
            self.entity.traits['GoTrait'].direction = 0

        jumping = keys[K_SPACE] or keys[K_UP]
        self.entity.traits['JumpTrait'].jump(jumping)

        self.entity.traits['GoTrait'].boost = keys[K_LSHIFT]

    def check_for_quit_and_restart_input_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and \
                (event.key == pygame.K_ESCAPE or event.key == pygame.K_F5):
                self.entity.pause = True
                self.entity.pause_obj.create_background_blur()
