import pygame


from core.input import *
from resources.level import LEVEL
from core.entity_base import *
from resources.sound import *


from core.traits import *
from utils.physics import Vector2D
from resources.display import SCREEN, Animation, SPRITE_COLLECTION
from resources.dashboard import DASHBOARD
from resources.Menus import PauseMenu


class Mario(EntityBase):
    def __init__(self, x, y, gravity=0.75):
        super(Mario, self).__init__(x, y, gravity)
        self.camera = Camera(self.rect, self, LEVEL.levelLength)
        self.input = Input(self)
        self.inAir = False
        self.inJump = False
        self.animation = Animation(
            [
                SPRITE_COLLECTION.get("mario_run1"),
                SPRITE_COLLECTION.get("mario_run2"),
                SPRITE_COLLECTION.get("mario_run3"),
            ],
            SPRITE_COLLECTION.get("mario_idle"),
            SPRITE_COLLECTION.get("mario_jump"),
        )
        self.traits = {
            "jumpTrait": jumpTrait(self),
            "goTrait": goTrait(self.animation, self.camera, self),
            "bounceTrait": bounceTrait(self),
        }
        self.collision = Collider(self, LEVEL)
        self.EntityCollider = EntityCollider(self)
        self.restart = False
        self.pause = False
        self.pauseObj = PauseMenu(self)
        self.lives = 3
        self.big_size = False
        self.timer = 0
        self.next = False

    def update(self):
        self.timer += 1
        self.updateTraits()
        self.moveMario()
        self.camera.move()
        self.applyGravity()
        self.drawMario()
        self.checkEntityCollision()
        self.input.checkForInput()
        if DASHBOARD.time == 0:
            self.gameOver()

    def drawMario(self):
        if self.traits["goTrait"].heading == 1:
            SCREEN.blit(self.animation.get_image(), self.getPos())
        elif self.traits["goTrait"].heading == -1:
            SCREEN.blit(
                pygame.transform.flip(self.animation.get_image(), True, False), self.getPos()
            )

    def moveMario(self):
        if(-(self.rect.x + self.vel.get_x()) < self.camera.x):
            self.rect.x += self.vel.get_x()
            self.collision.checkX()
        self.rect.y += self.vel.get_y()
        self.collision.checkY()

    def checkEntityCollision(self):
        for ent in LEVEL.entityList:
            isColliding, isTop = self.EntityCollider.check(ent)
            if isColliding:
                if ent.type == "Item":
                    self._onCollisionWithItem(ent)
                elif ent.type == "powerup":
                    self._onCollisionWithMushroom(ent)
                elif ent.type == "Block":
                    self._onCollisionWithBlock(ent)
                elif ent.type == "PowerBlock":
                    self._onCollisionWithPowerBlock(ent)
                elif ent.type == "Mob" and self.timer > 60:
                    self._onCollisionWithMob(ent, isColliding, isTop)

    def _onCollisionWithPowerBlock(self, box):
        if not box.triggered:
            LEVEL.addMushroom(box.x, box.y)
            box.item = (LEVEL.entityList[-1])
            SOUND_CONTROLLER.play_sfx(BUMP_SOUND)
        box.triggered = True

    def _onCollisionWithMushroom(self, item):
        DASHBOARD.points += 100
        DASHBOARD.earnedPoints += 100
        if not self.big_size:
            self.big_size = True
            self.animation = Animation(
                [
                    SPRITE_COLLECTION.get("big_mario_run1"),
                    SPRITE_COLLECTION.get("big_mario_run2"),
                    SPRITE_COLLECTION.get("big_mario_run3"),
                ],
                SPRITE_COLLECTION.get("big_mario_idle"),
                SPRITE_COLLECTION.get("big_mario_jump"),
            )
            img = self.animation.get_image()
            self.rect.w = img.get_width()
            self.rect.h = img.get_height()
            self.traits["goTrait"].animation = self.animation

            SOUND_CONTROLLER.play_sfx(MUSHROOM_SOUND)
        item.alive = None

    def _onCollisionWithItem(self, item):
        LEVEL.entityList.remove(item)
        DASHBOARD.points += 100
        DASHBOARD.earnedPoints += 100
        DASHBOARD.coins += 1
        SOUND_CONTROLLER.play_sfx(COIN_SOUND)

    def _onCollisionWithBlock(self, block):
        if not block.triggered:
            DASHBOARD.coins += 1
            DASHBOARD.earnedPoints += 100
            SOUND_CONTROLLER.play_sfx(BUMP_SOUND)
        block.triggered = True

    def _onCollisionWithMob(self, mob, isColliding, isTop):
        if isTop and mob.alive == True:
            SOUND_CONTROLLER.play_sfx(STOMP_SOUND)
            self.rect.bottom = mob.rect.top
            self.bounce()
            self.killEntity(mob)
            print("bounced on shell")
        if isTop and mob.alive == "shellBouncing":
            SOUND_CONTROLLER.play_sfx(STOMP_SOUND)
            self.rect.bottom = mob.rect.top
            self.bounce()
            self.killEntity(mob)
        elif isTop and mob.alive == "sleeping":
            SOUND_CONTROLLER.play_sfx(STOMP_SOUND)
            self.rect.bottom = mob.rect.top
            self.bounce()
            if mob.rect.x < self.rect.x:
                mob.leftrightTrait.direction = -1
                mob.rect.x += -5
            else:
                mob.rect.x += 5
                mob.leftrightTrait.direction = 1
            mob.alive = "shellBouncing"
            print("Bounced on sleeping shell")
        elif isColliding and mob.alive == "sleeping":
            if mob.rect.x < self.rect.x:
                mob.leftrightTrait.direction = -1
                mob.rect.x += -5
            else:
                mob.rect.x += 5
                mob.leftrightTrait.direction = 1
            mob.alive = "shellBouncing"
        elif isColliding and mob.alive:
            if self.big_size is True:
                self.big_size = False
                self.timer = 0
                self.animation = Animation(
                    [
                        SPRITE_COLLECTION.get("mario_run1"),
                        SPRITE_COLLECTION.get("mario_run2"),
                        SPRITE_COLLECTION.get("mario_run3"),
                    ],
                    SPRITE_COLLECTION.get("mario_idle"),
                    SPRITE_COLLECTION.get("mario_jump"),
                )
                self.traits["goTrait"].animation = self.animation
                img = self.animation.get_image()
                self.rect.w = img.get_width()
                self.rect.h = img.get_height()
                self.update()
                self.drawMario()
            else:
                self.gameOver()

    def bounce(self):
        self.traits["bounceTrait"].jump = True

    def killEntity(self, ent):
        if ent.__class__.__name__ != "Koopa":
            ent.alive = False
        else:
            ent.timer = 0
            ent.alive = "sleeping"
        DASHBOARD.points += 100
        DASHBOARD.earnedPoints += 100

    def next_level(self):
        self.rect.x = 0
        self.rect.y = 0
        self.camera.pos = Vector2D(self.rect.x, self.rect.y)

    def gameOver(self):
        self.lives -= 1
        DASHBOARD.coins = 0
        DASHBOARD.points -= DASHBOARD.earnedPoints
        DASHBOARD.earnedPoints = 0
        srf = pygame.Surface((640, 480))
        srf.set_colorkey((255, 255, 255), pygame.RLEACCEL)
        srf.set_alpha(128)
        SOUND_CONTROLLER.stop_music()
        SOUND_CONTROLLER.stop_sfx()
        SOUND_CONTROLLER.play_music(DEATH_SOUND)

        for i in range(500, 20, -2):
            srf.fill((0, 0, 0))
            pygame.draw.circle(
                srf,
                (255, 255, 255),
                (int(self.camera.x + self.rect.x) + 16, self.rect.y + 16),
                i,
            )
            SCREEN.blit(srf, (0, 0))
            pygame.display.update()
            self.input.checkForInput()
        while SOUND_CONTROLLER.playing_music():
            pygame.display.update()
            self.input.checkForInput()
        if self.lives == 0:
            SOUND_CONTROLLER.play_music(GAME_OVER)
            while SOUND_CONTROLLER.playing_music():
                pygame.display.update()
                self.input.checkForInput()
            self.restart = True
            highscore_file = open("resources/highscore.txt", "r")
            if highscore_file.mode == 'r':
                contents = highscore_file.read()
                highscore_file.close()
                if int(contents) < DASHBOARD.points:
                    highscore_file = open("resources/highscore.txt", "w+")
                    highscore_file.write(str(DASHBOARD.points))
            DASHBOARD.points = 0
        else:
            DASHBOARD.state = "start"
            DASHBOARD.time = 420
            LEVEL.loadLevel("Level" + DASHBOARD.level_name)
            self.rect.x = 0
            self.rect.y = 0
            DASHBOARD.lives = self.lives
            SOUND_CONTROLLER.play_music(SOUNDTRACK)
            self.camera.pos = Vector2D(self.rect.x, self.rect.y)

    def getPos(self):
        return self.camera.x + self.rect.x, self.rect.y

    def setPos(self, x, y):
        self.rect.x = x
        self.rect.y = y
