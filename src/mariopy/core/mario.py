import pygame


from core.input import *
from resources.level import LEVEL
from core.entity_base import *


from core.traits import *
from utils.physics import Vector2D
from resources.display import SCREEN, Animation, SPRITE_COLLECTION
from resources.dashboard import DASHBOARD
from resources.Menus import PauseMenu

class Mario(EntityBase):
    def __init__(self, x, y, gravity = 0.75):
        super(Mario, self).__init__(x, y, gravity)
        self.camera = Camera(self.rect, self)
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
        self.levelObj = LEVEL
        self.collision = Collider(self, self.levelObj)
        self.EntityCollider = EntityCollider(self)
        self.restart = False
        self.pause = False
        self.pauseObj = PauseMenu(self)
        self.lives = 3
    def update(self) :
        self.updateTraits()
        self.moveMario()
        self.camera.move()
        self.applyGravity()
        self.checkEntityCollision()
        self.input.checkForInput()
        if DASHBOARD.time == 0:
            self.gameOver()


    def moveMario(self):
        self.rect.x += self.vel.get_x()
        self.collision.checkX()
        self.rect.y += self.vel.get_y()
        self.collision.checkY()

    def checkEntityCollision(self):
        for ent in self.levelObj.entityList:
            isColliding, isTop = self.EntityCollider.check(ent)
            if isColliding:
                if ent.type == "Item":
                    self._onCollisionWithItem(ent)
                elif ent.type == "Block":
                    self._onCollisionWithBlock(ent)
                elif ent.type == "Mob":
                    self._onCollisionWithMob(ent, isColliding, isTop)

    def _onCollisionWithItem(self, item):
        self.levelObj.entityList.remove(item)
        DASHBOARD.points += 100
        DASHBOARD.coins += 1
        SOUND_CONTROLLER.play_sfx(COIN_SOUND)

    def _onCollisionWithBlock(self, block):
        if not block.triggered:
            DASHBOARD.coins += 1
            SOUND_CONTROLLER.play_sfx(BUMP_SOUND)
        block.triggered = True

    def _onCollisionWithMob(self, mob, isColliding, isTop):
        if isTop and (mob.alive or mob.alive == "shellBouncing"):
            SOUND_CONTROLLER.play_sfx(STOMP_SOUND)
            self.rect.bottom = mob.rect.top
            self.bounce()
            self.killEntity(mob)
        elif isTop and mob.alive == "sleeping":
            SOUND_CONTROLLER.play_sfx(STOMP_SOUND)
            self.rect.bottom = mob.rect.top
            mob.timer = 0
            self.bounce()
            mob.alive = False
        elif isColliding and mob.alive == "sleeping":
            if mob.rect.x < self.rect.x:
                mob.leftrightTrait.direction = -1
                mob.rect.x += -5
            else:
                mob.rect.x += 5
                mob.leftrightTrait.direction = 1
            mob.alive = "shellBouncing"
        elif isColliding and mob.alive:
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

    def gameOver(self):
        self.lives -= 1
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
            self.restart = True
        else:
            DASHBOARD.state = "start"
            DASHBOARD.time = 420
            LEVEL.loadLevel("Level"+DASHBOARD.level_name)


    def getPos(self):
        return self.camera.x + self.rect.x, self.rect.y

    def setPos(self,x,y):
        self.rect.x = x
        self.rect.y = y
