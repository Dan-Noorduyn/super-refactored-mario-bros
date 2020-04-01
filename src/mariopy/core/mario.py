import pygame

from core.entity_base import Camera, EntityBase
from core.input import Input
from core.traits import (Collider, EntityCollider, bounceTrait, goTrait,
                         jumpTrait)
from resources.dashboard import DASHBOARD
from resources.display import SCREEN, SPRITE_COLLECTION, Animation
from resources.level import LEVEL
from resources.Menus import PauseMenu
from resources.sound import (BUMP_SOUND, COIN_SOUND, DEATH_SOUND, GAME_OVER,
                             MUSHROOM_SOUND, SOUND_CONTROLLER, SOUNDTRACK,
                             STOMP_SOUND, POWER_DOWN, KICK_SOUND)
from utils.physics import Vector2D


class Mario(EntityBase):
    def __init__(self, x, y, gravity=0.75):
        super(Mario, self).__init__(x, y, gravity)
        self.camera = Camera(self.rect, self, LEVEL.level_length)
        self.input = Input(self)
        self.in_air = False
        self.in_jump = False
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
        self.entity_collider = EntityCollider(self)
        self.restart = False
        self.pause = False
        self.pause_obj = PauseMenu(self)
        self.lives = 3
        self.big_size = False
        self.timer = 120
        self.next = False

    def update(self):
        self.timer += 1
        self.update_traits()
        self.move_mario()
        self.apply_gravity()
        self.camera.move()
        self.draw_mario()
        self.check_entity_collision()
        self.input.check_for_input()
        if DASHBOARD.time == 0:
            self.game_over()

    def draw_mario(self):
        if (self.timer >= 120) or (self.timer < 120 and 10 <= self.timer % 20 < 20):
            if self.traits["goTrait"].heading == 1:
                SCREEN.blit(self.animation.get_image(), self.get_pos())
            elif self.traits["goTrait"].heading == -1:
                SCREEN.blit(
                    pygame.transform.flip(self.animation.get_image(), True, False), self.get_pos()
                )

    def move_mario(self):
        if(-(self.rect.x + self.vel.get_x()) < self.camera.x):
            self.rect.x += self.vel.get_x()
            self.collision.check_x()
        self.rect.y += self.vel.get_y()
        self.collision.check_y()

    def check_entity_collision(self):
        for ent in LEVEL.entity_list:
            is_colliding, is_top = self.entity_collider.check(ent)
            if is_colliding:
                if ent.type == "Item":
                    self._on_collision_with_item(ent)
                elif ent.type == "powerup":
                    self._on_collision_with_mushroom(ent)
                elif ent.type == "Block":
                    self._on_collision_with_block(ent)
                elif ent.type == "PowerBlock":
                    self._on_collision_with_power_block(ent)
                elif ent.type == "Mob":
                    self._on_collision_with_mob(ent, is_colliding, is_top)

    def _on_collision_with_power_block(self, box):
        if not box.triggered:
            LEVEL.add_mushroom(box.x, box.y)
            box.item = (LEVEL.entity_list[-1])
            SOUND_CONTROLLER.play_sfx(BUMP_SOUND)
        box.triggered = True

    def _on_collision_with_mushroom(self, item):
        DASHBOARD.points += 100
        DASHBOARD.earned_points += 100
        if not self.big_size:
            self._big_mario()
            SOUND_CONTROLLER.play_sfx(MUSHROOM_SOUND)
        item.dead = True

    def _on_collision_with_item(self, item):
        LEVEL.entity_list.remove(item)
        DASHBOARD.points += 100
        DASHBOARD.earned_points += 100
        DASHBOARD.coins += 1
        SOUND_CONTROLLER.play_sfx(COIN_SOUND)

    def _on_collision_with_block(self, block):
        if not block.triggered:
            DASHBOARD.coins += 1
            DASHBOARD.earned_points += 100
            SOUND_CONTROLLER.play_sfx(BUMP_SOUND)
        block.triggered = True

    def _on_collision_with_mob(self, mob, is_colliding, is_top):
        if is_top and mob.alive == True:
            SOUND_CONTROLLER.play_sfx(STOMP_SOUND)
            self.rect.bottom = mob.rect.top
            self.bounce()
            self.kill_entity(mob)
            mob.hit_once = True
        elif is_top and mob.alive == "shell_bouncing":
            SOUND_CONTROLLER.play_sfx(KICK_SOUND)
            self.rect.bottom = mob.rect.top
            self.bounce()
            mob.alive = "sleeping"
            mob.hit_once = True
        elif is_top and mob.alive == "sleeping":
            SOUND_CONTROLLER.play_sfx(KICK_SOUND)
            self.rect.bottom = mob.rect.top
            self.bounce()
            if mob.rect.x < self.rect.x:
                mob.left_right_trait.direction = -1
                mob.rect.x += -3
            else:
                mob.rect.x += 3
                mob.left_right_trait.direction = 1
            mob.alive = "shell_bouncing"
            mob.hit_once = True
        elif is_colliding and mob.alive == "sleeping":
            if mob.rect.x < self.rect.x:
                mob.left_right_trait.direction = -1
                mob.rect.x += -3
            else:
                mob.left_right_trait.direction = 1
                mob.rect.x += 3
            SOUND_CONTROLLER.play_sfx(KICK_SOUND)
            mob.alive = "shell_bouncing"
        elif is_colliding and mob.alive and self.timer > 120:
            if self.big_size is True:
                self._small_mario()
                SOUND_CONTROLLER.play_sfx(POWER_DOWN)
            else:
                self.game_over()

    def bounce(self):
        self.traits["bounceTrait"].jump = True

    def _small_mario(self):
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
        self.rect.y += 32

    def _big_mario(self):
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
        self.rect.y -= 32

    def kill_entity(self, ent):
        if ent.__class__.__name__ != "Koopa":
            ent.alive = False
        else:
            ent.timer = 0
            ent.alive = "sleeping"
        DASHBOARD.points += 100
        DASHBOARD.earned_points += 100

    def next_level(self):
        self.rect.x = 0
        self.rect.y = 0
        self.camera.pos = Vector2D(self.rect.x, self.rect.y)
        self.camera.level_length = LEVEL.level_length

    def game_over(self):
        self.lives -= 1
        DASHBOARD.coins = 0
        DASHBOARD.points -= DASHBOARD.earned_points
        DASHBOARD.earned_points = 0
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
            self.input.check_for_input()
        while SOUND_CONTROLLER.playing_music():
            pygame.display.update()
            self.input.check_for_input()
        if self.lives == 0:
            SOUND_CONTROLLER.play_music(GAME_OVER)
            while SOUND_CONTROLLER.playing_music():
                pygame.display.update()
                self.input.check_for_input()
            self.restart = True
            highscore_file = open("resources/highscore.txt", "r")
            if highscore_file.mode == 'r':
                contents = highscore_file.read()
                highscore_file.close()
                if int(contents) < DASHBOARD.points:
                    highscore_file = open("resources/highscore.txt", "w+")
                    highscore_file.write(str(DASHBOARD.points))
                    highscore_file.close()
            DASHBOARD.points = 0
        else:
            DASHBOARD.state = "start"
            DASHBOARD.time = 400
            LEVEL.load_level("Level" + DASHBOARD.level_name)
            self._small_mario()
            self.rect.x = 0
            self.rect.y = 0
            self.timer = 120
            DASHBOARD.lives = self.lives
            SOUND_CONTROLLER.play_music(SOUNDTRACK)
            self.camera.pos = Vector2D(self.rect.x, self.rect.y)

    def get_pos(self):
        return self.camera.x + self.rect.x, self.rect.y

    def set_pos(self, x, y):
        self.rect.x = x
        self.rect.y = y
