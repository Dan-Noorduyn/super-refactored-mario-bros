from copy import copy
from enum import Enum

import pygame

from core.traits import *
from core.input import *
from utils.physics import Vector2D
from resources.display import SCREEN, Animation, SPRITE_COLLECTION
from resources.dashboard import DASHBOARD

class Entity():

    ## @brief Intitializes an entity with a position.
    # @param x Initial x position of the entity.
    # @param y Initial y position of the entity.
    # @exception TypeError Arguments are not of type float.
    def __init__(self, x: float, y: float):
        try:
            assert(isinstance(x, float))
            assert(isinstance(y, float))
        except AssertionError as e:
            raise(TypeError("Arguments are not of type float."))
    
        self.__pos: Vector2D = Vector2D(x, y)
        self.__vel: Vector2D = Vector2D(0, 0)
        self.__acc: Vector2D = Vector2D(0, 0)

    ## @brief Gets the position of the entity.
    # @returns The position of the entity.
    def get_pos(self) -> Vector2D:
        return Vector2D(self.__pos.get_x(), self.__pos.get_y())

    ## @brief 
    def update_pos(self, v: Vector2D) -> None:
        self.__pos += v

    def set_pos(self, x: float, y: float) -> None:
        self.__pos = Vector2D(x, y)

    def get_vel(self) -> Vector2D:
        return Vector2D(self.__vel.get_x(), self.__vel.get_y())

    def update_vel(self, v: Vector2D) -> None:
        self.__vel += v

    def set_vel(self, vx: float, vy: float) -> None:
        self.__vel = Vector2D(vx, vy)

    def get_acc(self) -> Vector2D:
        return Vector2D(self.__vel.get_x(), self.__vel.get_y())

    def update_acc(self, v: Vector2D) -> None:
        self.__acc += v

    def set_acc(self, ax: float, ay: float) -> None:
        self.__acc = Vector2D(ax, ay)

    def update(self) -> None:
        self.__vel += Vector2D(self.__acc.get_x(), self.__acc.get_y())
        self.__pos += Vector2D(self.__vel.get_y(), self.__vel.get_y())

class EntityBase(pygame.sprite.Sprite):
    def __init__(self, x, y, gravity):
        pygame.sprite.Sprite.__init__(self)
        self.vel = Vector2D(0, 0)
        ##self.image = pygame.Surface([x, y])
        ##print(self.image)
        ##self.rect = pygame.Rect(self.image.get_rect())
        ##print(self.rect)
        self.rect = pygame.Rect(x * 32, y * 32, 32, 32)
        self.gravity = gravity
        self.traits = None
        self.alive = True
        self.timeAfterDeath = 5
        self.timer = 0
        self.type = ""
        self.onGround = False
        self.obeygravity = True

    def applyGravity(self):
        if self.obeygravity:
            if not self.onGround:
                self.vel += Vector2D(0, self.gravity)
            else:
                self.vel = Vector2D(self.vel.get_x(), 0)

    def updateTraits(self):
        for trait in self.traits.values():
            try:
                trait.update()
            except AttributeError:
                pass

    def getPosIndex(self):
        return Vector2D(int(self.rect.x / 32), int(self.rect.y / 32))

    def getPosIndexAsFloat(self):
        return Vector2D(self.rect.x / 32.0, self.rect.y / 32.0)



class Coin(EntityBase):
    def __init__(self, spriteCollection, x, y, gravity=0):
        super(Coin, self).__init__(x, y, gravity)
        self.animation = copy(SPRITE_COLLECTION.get("coin"))
        self.type = "Item"

    def update(self, cam):
        if self.alive:
            self.animation.update()
            SCREEN.blit(self.animation.get_image(), (self.rect.x + cam.x, self.rect.y))

class Goomba(EntityBase):
    def __init__(self, spriteColl, x, y, level):
        super(Goomba, self).__init__(y, x - 1, 1.25)
        self.animation = Animation(
            [
                SPRITE_COLLECTION.get("goomba-1"),
                SPRITE_COLLECTION.get("goomba-2"),
            ]
        )   
        self.leftrightTrait = LeftRightWalkTrait(self, level)
        self.type = "Mob"

    def update(self, camera):
        if self.alive:
            self.applyGravity()
            self.drawGoomba(camera)
            self.leftrightTrait.update()
        else:
            self.onDead(camera)

    def drawGoomba(self, camera):
        self.animation.update()
        SCREEN.blit(self.animation.get_image(), (self.rect.x + camera.x, self.rect.y))

    def onDead(self, camera):
        if self.timer == 0:
            self.setPointsTextStartPosition(self.rect.x + 3, self.rect.y)
        if self.timer < self.timeAfterDeath:
            self.movePointsTextUpAndDraw(camera)
            self.drawFlatGoomba(camera)
        else:
            self.alive = None
        self.timer += 0.1

    def drawFlatGoomba(self, camera):
        SCREEN.blit(
            SPRITE_COLLECTION.get("goomba-flat").image,
            (self.rect.x + camera.x, self.rect.y),
        )

    def setPointsTextStartPosition(self, x, y):
        self.textPos = Vector2D(x, y)

    def movePointsTextUpAndDraw(self, camera):
        self.textPos += Vector2D(-0.5, 0)
        DASHBOARD.drawText("100", self.textPos.get_x() + camera.x, self.textPos.get_y(), 8)

class Item():
    def __init__(self, collection, x, y):
        super(Item, self).__init__(8, SCREEN)
        self.ItemPos = Vector2D(x, y)
        self.itemVel = Vector2D(0, 0)
        self.coin_animation = copy(collection.get("coin-item").animation)
        self.sound_played = False

    def spawnCoin(self, cam, dashboard):
        if not self.sound_played:
            self.sound_played = True
            dashboard.points += 100
            SOUND_CONTROLLER.play_sfx(COIN_SOUND)
        self.coin_animation.update()
        if self.coin_animation.timer < 45:
            if self.coin_animation.timer < 15:
                self.itemVel -= Vector2D(0, 0.5)
                self.ItemPos += Vector2D(0, self.itemVel.get_y())
            elif self.coin_animation.timer < 45:
                self.itemVel += Vector2D(0, 0.5)
                self.ItemPos += Vector2D(0, self.itemVel.get_y())
            SCREEN.blit(
                self.coin_animation.image, (self.ItemPos.get_x() + cam.x, self.ItemPos.get_y())
            )
        elif self.coin_animation.timer < 80:
            self.itemVel = Vector2D(0, -0.75)
            self.ItemPos += Vector2D(0, self.itemVel.get_y())
            DASHBOARD.drawText("100", self.ItemPos.get_x() + 3 + cam.x, self.ItemPos.get_y(), 8)


class _Koopa_State(Enum):
    ALIVE = 1
    SLEEPING = 2
    BOUNCING = 3
    DEAD = 4

class Koopa(EntityBase):
    def __init__(self, x, y, level):
        super(Koopa, self).__init__(y - 1, x, 1.25)
        self.animation = Animation(
            [
                SPRITE_COLLECTION.get("koopa-1"),
                SPRITE_COLLECTION.get("koopa-2"),
            ]
        )
        self.leftrightTrait = LeftRightWalkTrait(self, level)
        self.timer = 0
        self.timeAfterDeath = 35
        self.type = "Mob"

    def update(self, camera):
        if self.alive == True:
            self.updateAlive(camera)
        elif self.alive == "sleeping":
            self.sleepingInShell(camera)
        elif self.alive == "shellBouncing":
            self.shellBouncing(camera)
        elif self.alive == False:
            self.die(camera)

    def drawKoopa(self, camera):
        if self.leftrightTrait.direction == -1:
            SCREEN.blit(
                self.animation.get_image(), (self.rect.x + camera.x, self.rect.y - 32)
            )
        else:
            SCREEN.blit(
                pygame.transform.flip(self.animation.get_image(), True, False),
                (self.rect.x + camera.x, self.rect.y - 32),
            )

    def shellBouncing(self, camera):
        self.leftrightTrait.speed = 4
        self.applyGravity()
        self.animation.image = SPRITE_COLLECTION.get("koopa-hiding").image
        self.drawKoopa(camera)
        self.leftrightTrait.update()

    def die(self, camera):
        if self.timer == 0:
            self.textPos = Vector2D(self.rect.x + 3, self.rect.y - 32)
        if self.timer < self.timeAfterDeath:
            self.textPos += Vector2D(0, -0.5)
            DASHBOARD.drawText("100", self.textPos.get_x() + camera.x, self.textPos.get_y(), 8)
            self.vel -= Vector2D(0, 0.5)
            self.rect.y += self.vel.get_y()
            SCREEN.blit(
                SPRITE_COLLECTION.get("koopa-hiding").image,
                (self.rect.x + camera.x, self.rect.y - 32),
            )
        else:
            self.vel += Vector2D(0, 0.3)
            self.rect.y += self.vel.get_y()
            self.textPos += Vector2D(0, -0.5)
            DASHBOARD.drawText("100", self.textPos.get_x() + camera.x, self.textPos.get_y(), 8)
            SCREEN.blit(
                SPRITE_COLLECTION.get("koopa-hiding").image,
                (self.rect.x + camera.x, self.rect.y - 32),
            )
            if self.timer > 500:
                # delete entity
                self.alive = None
        self.timer += 6

    def sleepingInShell(self, camera):
        if self.timer < self.timeAfterDeath:
            SCREEN.blit(
                SPRITE_COLLECTION.get("koopa-hiding").image,
                (self.rect.x + camera.x, self.rect.y - 32),
            )
        else:
            self.alive = True
            self.timer = 0
        self.timer += 0.1

    def updateAlive(self, camera):
        self.applyGravity()
        self.drawKoopa(camera)
        self.animation.update()
        self.leftrightTrait.update()

class RandomBox(EntityBase):
    def __init__(self, spriteCollection, x, y, dashboard, gravity=0):
        super(RandomBox, self).__init__(x, y, gravity)
        
        self.animation = copy(SPRITE_COLLECTION.get("randomBox").animation)
        self.type = "Block"
        self.triggered = False
        self.time = 0
        self.maxTime = 10
        self.vel = 1
        self.item = Item(spriteCollection, self.rect.x, self.rect.y)

    def update(self, cam):
        if self.alive and not self.triggered:
            self.animation.update()
        else:
            self.animation.image = SPRITE_COLLECTION.get("empty").image
            self.item.spawnCoin(cam, DASHBOARD)
            if self.time < self.maxTime:
                self.time += 1
                self.rect.y -= self.vel
            else:
                if self.time < self.maxTime * 2:
                    self.time += 1
                    self.rect.y += self.vel
        SCREEN.blit(
            SPRITE_COLLECTION.get("sky").image,
            (self.rect.x + cam.x, self.rect.y + 2),
        )
        SCREEN.blit(self.animation.image, (self.rect.x + cam.x, self.rect.y - 1))

class Camera:
    def __init__(self, pos, entity):
        self.pos = Vector2D(pos.x, pos.y)
        self.entity = entity
        self.x = self.pos.get_x() * 32
        self.y = self.pos.get_y() * 32

    def move(self):
        xPosFloat = self.entity.getPosIndexAsFloat().get_x()
        if 10 < xPosFloat < 50:
            self.pos = Vector2D(-xPosFloat + 10, self.pos.get_y())
        self.x = self.pos.get_x() * 32
        self.y = self.pos.get_y() * 32
