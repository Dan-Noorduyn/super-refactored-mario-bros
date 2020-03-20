import pygame

from .display import FONT_SPRITES, SCREEN, Spritesheet


class Dashboard():
    def __init__(self):
        self.state = "menu"
        self.level_name = ""
        self.points = 0
        self.coins = 0
        self.ticks = 0
        self.time = 420
        self.lives = 3
        self.new_level = False
        self.sprite_sheet = Spritesheet("./resources/img/title_screen.png")
        self.mushroom_life = self.sprite_sheet.image_at(
            0, 150, 2, colorkey=[255, 0, 220], ignoreTileSize=True
        )

    def update(self):
        self.drawText("MARIO", 20, 20, 15)
        self.drawText(self.pointString(), 20, 37, 15)

        self.drawText("LIVES", 160, 20, 15)
        for lives in range(self.lives):
            if lives == 0:
                SCREEN.blit(self.mushroom_life, (160, 37))
            if lives == 1:
                SCREEN.blit(self.mushroom_life, (185, 37))
            if lives == 2:
                SCREEN.blit(self.mushroom_life, (210, 37))

        self.drawText("@x{}".format(self.coinString()), 310, 37, 15)

        self.drawText("WORLD", 420, 20, 15)
        self.drawText(str(self.level_name), 420, 37, 15)

        self.drawText("TIME", 550, 20, 15)
        if self.state != "menu":
            self.drawText(self.timeString(), 552, 37, 15)

        # update Time
        if self.state == "start":
            self.ticks += 1
            if self.ticks == 60:
                self.ticks = 0
                self.time -= 1

    def drawText(self, text, x, y, size):
        for char in text:
            charSprite = pygame.transform.scale(FONT_SPRITES[char], (size, size))
            # print(charSprite)
            SCREEN.blit(charSprite, (x, y))
            if char == " ":
                x += size//2
            else:
                x += size

    def coinString(self):
        return "{:02d}".format(self.coins)

    def pointString(self):
        return "{:06d}".format(self.points)

    def timeString(self):
        return "{:03d}".format(self.time)


DASHBOARD = Dashboard()
