from random import randint

import pygame

from utils.physics import Vector2D
from resources.display import SCREEN
from resources.sound import *


class Collider:
    def __init__(self, entity, level):
        self.entity = entity
        self.levelObj = level
        self.level = level.level
        self.result = []

    def checkX(self):
        if self.leftLevelBorderReached() or self.rightLevelBorderReached():
            return
        # try:
        rows = [
            self.level[self.entity.getPosIndex().get_y() - 1],
            self.level[self.entity.getPosIndex().get_y()],
            self.level[self.entity.getPosIndex().get_y() + 1]
        ]
        # except Exception:
        #     return
        for row in rows:
            tiles = row[self.entity.getPosIndex().get_x(): self.entity.getPosIndex().get_x() + 2]
            for tile in tiles:
                if tile.rect is not None:
                    if self.entity.rect.colliderect(tile.rect):
                        if self.entity.rect.x < tile.rect.x and self.entity.vel.get_x() > 0:
                            self.entity.rect.right = tile.rect.left
                            self.entity.vel.set_x(0)
                        elif self.entity.rect.x > tile.rect.x and self.entity.vel.get_x() < 0:
                            self.entity.rect.left = tile.rect.right
                            self.entity.vel.set_x(0)

    def checkY(self):
        self.entity.onGround = False
        try:
            rows = [
                self.level[self.entity.getPosIndex().get_y() - 1],
                self.level[self.entity.getPosIndex().get_y()],
                self.level[self.entity.getPosIndex().get_y() + 1]
            ]
        except Exception:
            try:
                self.entity.gameOver()
            except Exception:
                self.entity.alive = None
            return
        for row in rows:
            tiles = row[self.entity.getPosIndex().get_x(): self.entity.getPosIndex().get_x() + 2]
            for tile in tiles:
                if tile.rect is not None:
                    if self.entity.rect.colliderect(tile.rect):
                        if self.entity.rect.y < tile.rect.y and self.entity.vel.get_y() > 0:
                            self.entity.onGround = True
                            self.entity.rect.bottom = tile.rect.top
                            self.entity.vel = Vector2D(self.entity.vel.get_x(), 0)
                            # reset jump on bottom
                            if self.entity.traits is not None:
                                if "jumpTrait" in self.entity.traits:
                                    self.entity.traits["jumpTrait"].reset()
                                if "bounceTrait" in self.entity.traits:
                                    self.entity.traits["bounceTrait"].reset()
                        if self.entity.rect.y > tile.rect.y and self.entity.vel.get_y() < 0:
                            self.entity.rect.top = tile.rect.bottom
                            self.entity.vel.set_y(0)

    def rightLevelBorderReached(self):
        if self.entity.getPosIndexAsFloat().get_x() > self.levelObj.levelLength - 1:
            return True

    def leftLevelBorderReached(self):
        if self.entity.rect.x < 0:
            self.entity.rect.x = 0
            self.entity.vel.set_x(0)
            return True


class bounceTrait:
    def __init__(self, entity):
        self.vel = 5
        self.jump = False
        self.entity = entity

    def update(self):
        if self.jump:
            self.entity.vel.set_y(0)
            self.entity.vel -= Vector2D(0, self.vel)
            self.jump = False
            self.entity.inAir = True

    def reset(self):
        self.entity.inAir = False


class goTrait:
    def __init__(self, animation, camera, ent):
        self.animation = animation
        self.direction = 0
        self.heading = 1
        self.accelVel = 0.4
        self.decelVel = 0.25
        self.maxVel = 3.0
        self.boost = False
        self.camera = camera
        self.entity = ent

    def update(self):
        if self.boost:
            self.maxVel = 5.0
            self.animation.deltaTime = 4
        else:
            self.animation.deltaTime = 7
            if abs(self.entity.vel.get_x()) > 3.2:
                self.entity.vel.set_x(3.2 * self.heading)
            self.maxVel = 3.2

        if self.direction != 0:
            self.heading = self.direction
            if self.heading == 1:
                if self.entity.vel.get_x() < self.maxVel:
                    self.entity.vel += Vector2D(self.accelVel * self.heading, 0)
            else:
                if self.entity.vel.get_x() > -self.maxVel:
                    self.entity.vel += Vector2D(self.accelVel * self.heading, 0)

            if not self.entity.inAir:
                self.animation.update()
            else:
                self.animation.in_air()
        else:
            self.animation.update()
            if self.entity.vel.get_x() >= 0:
                self.entity.vel -= Vector2D(self.decelVel, 0)
            else:
                self.entity.vel += Vector2D(self.decelVel, 0)
            if int(self.entity.vel.get_x()) == 0:
                self.entity.vel = Vector2D(0, self.entity.vel.get_y())
                if self.entity.inAir:
                    self.animation.in_air()
                else:
                    self.animation.idle()


class jumpTrait:
    def __init__(self, entity):
        self.vertical_speed = -12  # jump speed
        self.jumpHeight = 120  # jump height in pixels
        self.entity = entity
        self.initalHeight = 384  # stores the position of mario at jump
        self.deaccelerationHeight = self.jumpHeight - \
            ((self.vertical_speed*self.vertical_speed)/(2*self.entity.gravity))

    def jump(self, jumping):
        if jumping:
            if not self.entity.inAir and not self.entity.inJump:  # only jump when mario is on ground and not in a jump. redundant check
                SOUND_CONTROLLER.play_sfx(JUMP_SOUND)
                self.entity.vel = Vector2D(self.entity.vel.get_x(), self.vertical_speed)
                self.entity.inAir = True
                self.initalHeight = self.entity.rect.y
                self.entity.inJump = True
                self.entity.obeygravity = False  # dont obey gravity in jump so as to reach jump height no matter what the speed

        if self.entity.inJump:  # check vertical distance travelled while mario is in a jump
            if (self.initalHeight-self.entity.rect.y) >= self.deaccelerationHeight or self.entity.vel.get_y() == 0:
                self.entity.inJump = False
                self.entity.obeygravity = True  # mario obeys gravity again and continues normal play

    def reset(self):
        self.entity.inAir = False


class LeftRightWalkTrait:
    def __init__(self, entity, level):
        self.direction = -1 if randint(0, 1) == 0 else 1
        self.entity = entity
        self.collDetection = Collider(self.entity, level)
        self.speed = 1
        self.entity.vel = Vector2D(self.speed * self.direction, self.entity.vel.get_y())

    def update(self):
        if self.entity.vel.get_x() == 0:
            self.direction *= -1
        self.entity.vel = Vector2D(self.speed * self.direction, self.entity.vel.get_y())
        self.moveEntity()

    def moveEntity(self):
        self.entity.rect.y += self.entity.vel.get_y()
        self.collDetection.checkY()
        self.entity.rect.x += self.entity.vel.get_x()
        self.collDetection.checkX()


class EntityCollider:
    def __init__(self, entity):
        self.entity = entity
        # initially own class
        self.isColliding = False
        self.isTop = False

    def check(self, target):
        if self.entity.rect.colliderect(target.rect):
            return self.determineSide(target.rect, self.entity.rect)
        self.isColliding, self.isTop = False, False
        return self.isColliding, self.isTop
        # return CollisionState(False, False)

    def determineSide(self, rect1, rect2):
        if (
            rect1.collidepoint(rect2.bottomleft)
            or rect1.collidepoint(rect2.bottomright)
            or rect1.collidepoint(rect2.midbottom)
        ):
            if rect2.collidepoint(
                (rect1.midleft[0] / 2, rect1.midleft[1] / 2)
            ) or rect2.collidepoint((rect1.midright[0] / 2, rect1.midright[1] / 2)):
                self.isColliding, self.isTop = True, False
                return self.isColliding, self.isTop
                # return CollisionState(True, False)
            else:
                if self.entity.vel.get_y() > 0:
                    self.isColliding, self.isTop = True, True
                    return self.isColliding, self.isTop
                    # return CollisionState(True, True)
        self.isColliding, self.isTop = True, False
        return self.isColliding, self.isTop
        # return CollisionState(True, False)
