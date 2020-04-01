from copy import copy

import pygame

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
        self.time_after_death = 5
        self.timer = 0
        self.type = ""
        self.on_ground = False
        self.obey_gravity = True

    def apply_gravity(self):
        if self.obey_gravity:
            if not self.on_ground:
                self.vel += Vector2D(0, self.gravity)
            else:
                self.vel.set_y(0)

    def update_traits(self):
        for trait in self.traits.values():
            try:
                trait.update()
            except AttributeError:
                pass

    def get_pos_index(self):
        return Vector2D(int(self.rect.x / 32), int(self.rect.y / 32))

    def get_pos_index_as_float(self):
        return Vector2D(self.rect.x / 32.0, self.rect.y / 32.0)


class Coin(EntityBase):
    def __init__(self, x, y, gravity=0):
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
    def __init__(self, x, y, level):
        super(Goomba, self).__init__(x, y - 1, 1.25)
        self.animation = Animation(
            [
                SPRITE_COLLECTION.get("goomba-1"),
                SPRITE_COLLECTION.get("goomba-2"),
            ]
        )
        self.left_right_trait = LeftRightWalkTrait(self, level)
        self.type = "Mob"
        self.traits = {
            "bounceTrait": bounceTrait(self),
        }
        self.in_air = False
        self.text_pos = Vector2D(x, y)
        self.hit_once = False

    def update(self, camera):
        self.update_traits()
        self.apply_gravity()
        if self.alive:
            self.draw_goomba(camera)
            self.left_right_trait.update()
        else:
            self.on_dead(camera)

    def draw_goomba(self, camera):
        self.animation.update()
        SCREEN.blit(self.animation.get_image(), (self.rect.x + camera.x,
                                                 self.rect.y))

    def on_dead(self, camera):
        if self.timer == 0:
            self.set_points_text_start_position(self.rect.x + 3, self.rect.y)
        if self.timer < self.time_after_death and not self.in_air:
            self.move_points_text_up_and_draw(camera)
            self.draw_flat_goomba(camera)
        elif self.in_air:
            self.draw_goomba(camera)
            self.move_points_text_up_and_draw(camera)
            self.vel -= Vector2D(0, 0.5)
            self.rect.y += self.vel.get_y()

        if self.timer >= self.time_after_death:
            self.alive = None
        self.timer += 0.1

    def bounce(self):
        self.traits["bounceTrait"].jump = True

    def draw_flat_goomba(self, camera):
        SCREEN.blit(
            SPRITE_COLLECTION.get("goomba-flat"),
            (self.rect.x + camera.x, self.rect.y),
        )

    def set_points_text_start_position(self, x, y):
        self.text_pos = Vector2D(x, y)

    def move_points_text_up_and_draw(self, camera):
        self.text_pos += Vector2D(-0.5, 0)
        DASHBOARD.draw_text("100", self.text_pos.get_x() + camera.x,
                           self.text_pos.get_y(), 8)


class Item():
    def __init__(self, x, y):
        self.item_pos = Vector2D(x, y)
        self.item_vel = Vector2D(0, 0)
        self.coin_animation = copy(SPRITE_COLLECTION.get("coin-item"))
        self.sound_played = False

    def spawn_coin(self, cam):
        if not self.sound_played:
            self.sound_played = True
            DASHBOARD.points += 100
            SOUND_CONTROLLER.play_sfx(COIN_SOUND)
        self.coin_animation.update()

        if self.coin_animation.timer < 45:
            if self.coin_animation.timer < 15:
                self.item_vel -= Vector2D(0, 0.5)
                self.item_pos += Vector2D(0, self.item_vel.get_y())
            elif self.coin_animation.timer < 45:
                self.item_vel += Vector2D(0, 0.5)
                self.item_pos += Vector2D(0, self.item_vel.get_y())
            SCREEN.blit(
                self.coin_animation.get_image(), (self.item_pos.get_x() + cam.x,
                                                  self.item_pos.get_y())
            )
        elif self.coin_animation.timer < 80:
            self.item_vel = Vector2D(0, -0.75)
            self.item_pos += Vector2D(0, self.item_vel.get_y())
            DASHBOARD.draw_text("100", self.item_pos.get_x() + 3 + cam.x,
                               self.item_pos.get_y(), 8)


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
        self.left_right_trait = LeftRightWalkTrait(self, level)
        self.timer = 0
        self.time_after_death = 35
        self.type = "Mob"
        self.level_obj = level
        self.entity_collider = EntityCollider(self)
        self.in_air = False
        self.hit_once = False
        self.text_pos = Vector2D(x, y)

    # If shell sleeping. kill it. If alive == true, kill it.

    def update(self, camera):
        if self.alive == True:
            self.update_alive(camera)
        elif self.alive == "sleeping":
            self.sleeping_in_shell(camera)
        elif self.alive == "shell_bouncing":
            self.shell_bouncing(camera)
        elif self.alive == False:
            self.die(camera)

    def draw_koopa(self, camera):
        if self.left_right_trait.direction == -1:
            SCREEN.blit(
                self.animation.get_image(), (self.rect.x + camera.x,
                                             self.rect.y - 32)
            )
        else:
            SCREEN.blit(
                pygame.transform.flip(self.animation.get_image(), True, False),
                (self.rect.x + camera.x, self.rect.y - 32),
            )

    def shell_bouncing(self, camera):
        self.left_right_trait.speed = 4
        self.apply_gravity()
        self.animation.set_image(SPRITE_COLLECTION.get("koopa-hiding"))
        self.draw_koopa(camera)
        self.left_right_trait.update()
        self.check_entity_collision()

    def check_entity_collision(self):
        for ent in self.level_obj.entity_list:
            if ent.type == "Mob" and ent != self:
                is_colliding, _ = self.entity_collider.check(ent)
                if is_colliding:
                    self._on_collision_with_mob(ent, is_colliding)

    def _on_collision_with_mob(self, ent, is_colliding):
        if is_colliding and ent.alive:
            ent.bounce()
            ent.set_points_text_start_position(ent.rect.x + 3, ent.rect.y)
            ent.alive = False
            DASHBOARD.points += 100
            DASHBOARD.earned_points += 100
            ent.left_right_trait.update()
        elif is_colliding and ent.alive == "sleeping":
            ent.bounce()
            ent.set_points_text_start_position(ent.rect.x + 3, ent.rect.y)
            ent.alive = False
            DASHBOARD.points += 100
            DASHBOARD.earned_points += 100
            ent.left_right_trait.update()
        elif is_colliding and ent.alive == "shell_bouncing":
            ent.bounce()
            self.bounce()
            ent.set_points_text_start_position(ent.rect.x + 3, ent.rect.y)
            self.set_points_text_start_position(self.rect.x + 3, self.rect.y)
            ent.alive = False
            self.alive = False
            DASHBOARD.points += 100
            DASHBOARD.earned_points += 100
            ent.left_right_trait.update()
            self.left_right_trait.update()

    def die(self, camera):
        if self.timer == 0:
            self.set_points_text_start_position(self.rect.x + 3, self.rect.y)
        if self.timer < self.time_after_death:
            self.text_pos -= Vector2D(0, -0.5)
            DASHBOARD.draw_text("100", self.text_pos.get_x() + camera.x, self.text_pos.get_y(), 8)
            self.vel += Vector2D(0, 0.5)
            self.rect.y -= self.vel.get_y()
            SCREEN.blit(
                SPRITE_COLLECTION.get("koopa-hiding"),
                (self.rect.x + camera.x, self.rect.y - 32),
            )
        else:
            self.vel += Vector2D(0, 0.5)
            self.rect.y += self.vel.get_y()
            self.move_points_text_up_and_draw(camera)
            self.text_pos += Vector2D(0, -0.5)
            DASHBOARD.draw_text("100", self.text_pos.get_x() + camera.x,
                               self.text_pos.get_y(), 8)
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

    def sleeping_in_shell(self, camera):
        if self.timer < self.time_after_death:
            SCREEN.blit(
                SPRITE_COLLECTION.get("koopa-hiding"),
                (self.rect.x + camera.x, self.rect.y - 32),
            )
        else:
            self.alive = True
            self.timer = 0
        self.timer += 0.1

    def update_alive(self, camera):
        self.apply_gravity()
        self.draw_koopa(camera)
        self.animation.update()
        self.left_right_trait.update()

    def set_points_text_start_position(self, x, y):
        self.text_pos = Vector2D(x, y)

    def move_points_text_up_and_draw(self, camera):
        self.text_pos += Vector2D(-0.5, 0)
        DASHBOARD.draw_text("100", self.text_pos.get_x() + camera.x, self.text_pos.get_y(), 8)


class RandomBox(EntityBase):
    def __init__(self, x, y, gravity=0):
        super(RandomBox, self).__init__(x, y, gravity)
        self.animation = copy(SPRITE_COLLECTION.get("randomBox"))
        self.type = "Block"
        self.triggered = False
        self.time = 0
        self.max_time = 10
        self.vel = 1
        self.item = Item(self.rect.x, self.rect.y)

    def update(self, cam):
        if self.alive and not self.triggered:
            self.animation.update()
        else:
            self.animation.set_image(SPRITE_COLLECTION.get("empty"))
            self.item.spawn_coin(cam)
            if self.time < self.max_time:
                self.time += 1
                self.rect.y -= self.vel
            else:
                if self.time < self.max_time * 2:
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
        super(MushroomItem, self).__init__(x, y - 1, 1.25)
        self.type = "powerup"
        self.animation = copy(SPRITE_COLLECTION.get("mushroom"))
        self.sound_played = False
        self.alive = False
        self.timer = 0
        self.level = level
        self.left_right_trait = None
        self.dead = False

    def spawn_mushroom(self, cam):
        if not self.sound_played:
            self.sound_played = True
            SOUND_CONTROLLER.play_sfx(MUSHROOM_APPEARS)
        self.draw_mushroom(cam)
        self.alive = True
        self.left_right_trait = LeftRightWalkTrait(self, self.level)

    def update(self, cam):
        if self.alive:
            self.apply_gravity()
            self.draw_mushroom(cam)
            self.left_right_trait.update()
        if self.dead:
            self.alive = None

    def draw_mushroom(self, cam):
        SCREEN.blit(
            self.animation.get_image(), (self.rect.x +
                                         cam.x,
                                         self.rect.y)
        )


class PowerUpBox(EntityBase):
    def __init__(self, x, y, gravity=0):
        super(PowerUpBox, self).__init__(x, y, gravity)

        self.animation = copy(SPRITE_COLLECTION.get("PowerUpBox"))
        self.type = "PowerBlock"
        self.triggered = False
        self.time = 0
        self.max_time = 10
        self.x = x
        self.y = y
        self.vel = 1
        self.item = None
        self.spawn = False

    def update(self, cam):
        if self.alive and not self.triggered:
            self.animation.update()
        elif self.triggered and not self.spawn:
            self.item.spawn_mushroom(cam)
            self.spawn = True
        else:
            self.animation.set_image(SPRITE_COLLECTION.get("empty"))

            if self.time < self.max_time:
                self.time += 1
                self.rect.y -= self.vel
            else:
                if self.time < self.max_time * 2:
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
        self.last_pos = self.pos.get_x()
        self.level_length = level_length

    def move(self):
        self.last_pos = self.pos.get_x()
        x_pos_float = self.entity.get_pos_index_as_float().get_x()
        if 10 < x_pos_float < (self.level_length - 10) and (-x_pos_float + 10) < self.last_pos:
            self.pos = Vector2D(-x_pos_float + 10, self.pos.get_y())
        self.x = self.pos.get_x() * 32
        self.y = self.pos.get_y() * 32
