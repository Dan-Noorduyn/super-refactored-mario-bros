import pygame

from resources.display import FONT_SPRITES, SCREEN, Spritesheet


class Dashboard():
    def __init__(self):
        self.state = "menu"
        self.level_name = ""
        self.earned_points = 0
        self.points = 0
        self.coins = 0
        self.ticks = 0
        self.time = 400
        self.lives = 3
        self.new_level = False
        self.sprite_sheet = Spritesheet("./resources/img/title_screen.png")
        self.mushroom_life = self.sprite_sheet.image_at(
            0, 150, 2, color_key=[0, 0, 0], ignore_tile_size=True
        )


    def reset(self):
        self.state = "menu"
        self.level_name = ""
        self.points = 0
        self.earned_points = 0
        self.coins = 0
        self.ticks = 0
        self.time = 400
        self.lives = 3
        self.new_level = False

    def update(self):
        self.draw_text("MARIO", 20, 20, 15)
        self.draw_text(self.point_string(), 20, 37, 15)

        self.draw_text("LIVES", 160, 20, 15)
        for lives in range(self.lives):
            if lives == 0:
                SCREEN.blit(self.mushroom_life, (160, 37))
            if lives == 1:
                SCREEN.blit(self.mushroom_life, (185, 37))
            if lives == 2:
                SCREEN.blit(self.mushroom_life, (210, 37))

        self.draw_text("@x{}".format(self.coin_string()), 310, 37, 15)

        self.draw_text("WORLD", 420, 20, 15)
        if self.state != "menu":
            self.draw_text(str(self.level_name), 420, 37, 15)

        self.draw_text("TIME", 550, 20, 15)
        if self.state != "menu":
            self.draw_text(self.time_string(), 552, 37, 15)
        # update Time
        if self.state == "start":
            self.ticks += 2
            if self.ticks == 60:
                self.ticks = 0
                self.time -= 1

    def draw_text(self, text, x, y, size):
        for char in text:
            char_sprite = pygame.transform.scale(FONT_SPRITES[char], (size, size))
            SCREEN.blit(char_sprite, (x, y))
            if char == " ":
                x += size//2
            else:
                x += size

    def coin_string(self):
        return "{:02d}".format(self.coins)

    def point_string(self):
        return "{:06d}".format(self.points)

    def time_string(self):
        return "{:03d}".format(self.time)


DASHBOARD = Dashboard()
