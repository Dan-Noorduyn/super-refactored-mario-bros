from copy import copy
from enum import Enum

import pygame

from core.input import Input
from core.traits import LeftRightWalkTrait, bounceTrait, EntityCollider
from resources.dashboard import DASHBOARD
from resources.display import SCREEN, SPRITE_COLLECTION, Animation
from resources.sound import COIN_SOUND, MUSHROOM_APPEARS, SOUND_CONTROLLER
from utils.physics import Vector2D


class EntityBase(pygame.sprite.Sprite):
    def __init__(self, x, y, gravity):
        pygame.sprite.Sprite.__init__(self)
        self.vel = Vector2D(0, 0)
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
        self.animation.update()
        SCREEN.blit(
            self.animation.get_image(),
            (self.rect.x + cam.x, self.rect.y)
        )


class Goomba(EntityBase):
    def __init__(self, spriteColl, x, y, level):
        super(Goomba, self).__init__(x, y - 1, 1.25)
        self.animation = Animation(
            [
                SPRITE_COLLECTION.get("goomba-1"),
                SPRITE_COLLECTION.get("goomba-2"),
            ]
        )
        self.leftrightTrait = LeftRightWalkTrait(self, level)
        self.type = "Mob"
        self.traits = {
            "bounceTrait": bounceTrait(self),
        }
        self.inAir = False

    def update(self, camera):
        self.updateTraits()
        self.applyGravity()
        if self.alive:
            self.drawGoomba(camera)
            self.leftrightTrait.update()
        else:
            self.onDead(camera)

    def drawGoomba(self, camera):
        self.animation.update()
        SCREEN.blit(self.animation.get_image(), (self.rect.x + camera.x,
                                                 self.rect.y))

    def onDead(self, camera):
        if self.timer == 0:
            self.setPointsTextStartPosition(self.rect.x + 3, self.rect.y)
        if self.timer < self.timeAfterDeath and not self.inAir:
            self.movePointsTextUpAndDraw(camera)
            self.drawFlatGoomba(camera)
        elif self.inAir:
            self.drawGoomba(camera)
            self.movePointsTextUpAndDraw(camera)
            self.vel -= Vector2D(0, 0.5)
            self.rect.y += self.vel.get_y()

        if self.timer >= self.timeAfterDeath:
            self.alive = None
        self.timer += 0.1

    def bounce(self):
        self.traits["bounceTrait"].jump = True

    def drawFlatGoomba(self, camera):
        SCREEN.blit(
            SPRITE_COLLECTION.get("goomba-flat"),
            (self.rect.x + camera.x, self.rect.y),
        )

    def setPointsTextStartPosition(self, x, y):
        self.textPos = Vector2D(x, y)

    def movePointsTextUpAndDraw(self, camera):
        self.textPos += Vector2D(-0.5, 0)
        DASHBOARD.drawText("100", self.textPos.get_x() + camera.x,
                           self.textPos.get_y(), 8)


class Item():
    def __init__(self, collection, x, y):
        self.ItemPos = Vector2D(x, y)
        self.itemVel = Vector2D(0, 0)
        self.coin_animation = copy(collection.get("coin-item"))
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
                self.coin_animation.get_image(), (self.ItemPos.get_x() + cam.x,
                                                  self.ItemPos.get_y())
            )
        elif self.coin_animation.timer < 80:
            self.itemVel = Vector2D(0, -0.75)
            self.ItemPos += Vector2D(0, self.itemVel.get_y())
            DASHBOARD.drawText("100", self.ItemPos.get_x() + 3 + cam.x,
                               self.ItemPos.get_y(), 8)


class Koopa(EntityBase):
    def __init__(self, x, y, level):
        super(Koopa, self).__init__(x, y - 1, 1.25)
        self.animation = Animation(
            [
                SPRITE_COLLECTION.get("koopa-1"),
                SPRITE_COLLECTION.get("koopa-2"),
            ]
        )
        self.traits = {
            "bounceTrait": bounceTrait(self),
        }
        self.leftrightTrait = LeftRightWalkTrait(self, level)
        self.timer = 0
        self.timeAfterDeath = 35
        self.type = "Mob"
        self.levelObj = level
        self.EntityCollider = EntityCollider(self)
        self.inAir = False
        self.hit_once = False

    # If shell sleeping. kill it. If alive == true, kill it.

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
                self.animation.get_image(), (self.rect.x + camera.x,
                                             self.rect.y - 32)
            )
        else:
            SCREEN.blit(
                pygame.transform.flip(self.animation.get_image(), True, False),
                (self.rect.x + camera.x, self.rect.y - 32),
            )

    def shellBouncing(self, camera):
        self.leftrightTrait.speed = 4
        self.applyGravity()
        self.animation.set_image(SPRITE_COLLECTION.get("koopa-hiding"))
        self.drawKoopa(camera)
        self.leftrightTrait.update()
        self.checkEntityCollision()

    def checkEntityCollision(self):
        for ent in self.levelObj.entityList:
            if ent.type == "Mob" and ent != self:
                is_colliding, _ = self.EntityCollider.check(ent)
                if is_colliding:
                    self._onCollisionWithMob(ent, is_colliding)

    def _onCollisionWithMob(self, ent, is_colliding):
        if is_colliding and ent.alive:
            ent.bounce()
            ent.setPointsTextStartPosition(ent.rect.x + 3, ent.rect.y)
            ent.alive = False
            DASHBOARD.points += 100
            DASHBOARD.earnedPoints += 100
            ent.leftrightTrait.update()
        elif is_colliding and ent.alive == "sleeping":
            ent.bounce()
            ent.setPointsTextStartPosition(ent.rect.x + 3, ent.rect.y)
            ent.alive = False
            DASHBOARD.points += 100
            DASHBOARD.earnedPoints += 100
            ent.leftrightTrait.update()
        elif is_colliding and ent.alive == "shellBouncing":
            ent.bounce()
            self.bounce()
            ent.setPointsTextStartPosition(ent.rect.x + 3, ent.rect.y)
            self.setPointsTextStartPosition(self.rect.x + 3, self.rect.y)
            ent.alive = False
            self.alive = False
            DASHBOARD.points += 100
            DASHBOARD.earnedPoints += 100
            ent.leftrightTrait.update()
            self.leftrightTrait.update()

    def die(self, camera):
        if self.timer == 0:
            self.setPointsTextStartPosition(self.rect.x + 3, self.rect.y)
        if self.timer < self.timeAfterDeath:
            self.textPos -= Vector2D(0, -0.5)
            DASHBOARD.drawText("100", self.textPos.get_x() + camera.x, self.textPos.get_y(), 8)
            self.vel += Vector2D(0, 0.5)
            self.rect.y -= self.vel.get_y()
            SCREEN.blit(
                SPRITE_COLLECTION.get("koopa-hiding"),
                (self.rect.x + camera.x, self.rect.y - 32),
            )
        else:
            self.vel += Vector2D(0, 0.5)
            self.rect.y += self.vel.get_y()
            self.movePointsTextUpAndDraw(camera)
            self.textPos += Vector2D(0, -0.5)
            DASHBOARD.drawText("100", self.textPos.get_x() + camera.x,
                               self.textPos.get_y(), 8)
            SCREEN.blit(
                SPRITE_COLLECTION.get("koopa-hiding"),
                (self.rect.x + camera.x, self.rect.y - 32),
            )
            if self.timer > 500:
                # delete entity
                self.alive = None
        self.timer += 6

    def bounce(self):
        self.traits["bounceTrait"].jump = True

    def sleepingInShell(self, camera):
        if self.timer < self.timeAfterDeath:
            SCREEN.blit(
                SPRITE_COLLECTION.get("koopa-hiding"),
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

    def setPointsTextStartPosition(self, x, y):
        self.textPos = Vector2D(x, y)

    def movePointsTextUpAndDraw(self, camera):
        self.textPos += Vector2D(-0.5, 0)
        DASHBOARD.drawText("100", self.textPos.get_x() + camera.x, self.textPos.get_y(), 8)


class RandomBox(EntityBase):
    def __init__(self, spriteCollection, x, y, dashboard, gravity=0):
        super(RandomBox, self).__init__(x, y, gravity)
        self.animation = copy(SPRITE_COLLECTION.get("randomBox"))
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
            self.animation.set_image(SPRITE_COLLECTION.get("empty"))
            self.item.spawnCoin(cam, DASHBOARD)
            if self.time < self.maxTime:
                self.time += 1
                self.rect.y -= self.vel
            else:
                if self.time < self.maxTime * 2:
                    self.time += 1
                    self.rect.y += self.vel
        SCREEN.blit(
            SPRITE_COLLECTION.get("sky"),
            (self.rect.x + cam.x, self.rect.y + 2),
        )
        SCREEN.blit(self.animation.get_image(), (self.rect.x + cam.x,
                                                 self.rect.y - 1))


class MushroomItem(EntityBase):
    def __init__(self, x, y, level):
        super(MushroomItem, self).__init__(x, y-1, 1.25)
        self.type = "powerup"
        self.animation = copy(SPRITE_COLLECTION.get("mushroom"))
        self.sound_played = False
        self.alive = False
        self.timer = 0
        self.level = level
        self.leftrightTrait = None
        self.dead = False

    def spawnMushroom(self, cam):
        if not self.sound_played:
            self.sound_played = True
            SOUND_CONTROLLER.play_sfx(MUSHROOM_APPEARS)
        self.drawMushroom(cam)
        self.alive = True
        self.leftrightTrait = LeftRightWalkTrait(self, self.level)

    def update(self, cam):
        if self.alive:
            self.applyGravity()
            self.drawMushroom(cam)
            self.leftrightTrait.update()
        if self.dead:
            self.alive = None

    def drawMushroom(self, cam):
        SCREEN.blit(
            self.animation.get_image(), (self.rect.x +
                                         cam.x,
                                         self.rect.y)
        )


class PowerUpBox(EntityBase):
    def __init__(self, spriteCollection, x, y, gravity=0):
        super(PowerUpBox, self).__init__(x, y, gravity)

        self.animation = copy(SPRITE_COLLECTION.get("PowerUpBox"))
        self.type = "PowerBlock"
        self.triggered = False
        self.time = 0
        self.maxTime = 10
        self.x = x
        self.y = y
        self.vel = 1
        self.item = None
        self.spawn = False

    def update(self, cam):
        if self.alive and not self.triggered:
            self.animation.update()
        elif self.triggered and not self.spawn:
            self.item.spawnMushroom(cam)
            self.spawn = True
        else:
            self.animation.set_image(SPRITE_COLLECTION.get("empty"))

            if self.time < self.maxTime:
                self.time += 1
                self.rect.y -= self.vel
            else:
                if self.time < self.maxTime * 2:
                    self.time += 1
                    self.rect.y += self.vel
        SCREEN.blit(
            SPRITE_COLLECTION.get("sky"),
            (self.rect.x + cam.x, self.rect.y + 2),
        )
        SCREEN.blit(self.animation.get_image(), (self.rect.x + cam.x,
                                                 self.rect.y - 1))


class Camera:
    def __init__(self, pos, entity, level_length):
        self.pos = Vector2D(pos.x, pos.y)
        self.entity = entity
        self.x = self.pos.get_x() * 32
        self.y = self.pos.get_y() * 32
        self.lastPos = self.pos.get_x()
        self.level_length = level_length

    def move(self):
        self.lastPos = self.pos.get_x()
        xPosFloat = self.entity.getPosIndexAsFloat().get_x()
        if 10 < xPosFloat < (self.level_length - 10) and (-xPosFloat + 10) < self.lastPos:
            self.pos = Vector2D(-xPosFloat + 10, self.pos.get_y())
        self.x = self.pos.get_x() * 32
        self.y = self.pos.get_y() * 32
