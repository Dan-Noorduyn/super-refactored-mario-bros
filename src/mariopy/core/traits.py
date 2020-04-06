from resources.sound import JUMP_SOUND, SOUND_CONTROLLER
from utils.physics import Vector2D


class Collider:
    def __init__(self, entity, level):
        self.entity = entity
        self.level_obj = level
        self.level = level.level
        self.result = []

    def check_x(self):
        if self.left_level_border_reached() or self.right_level_border_reached():
            return

        rows = []

        for i in range(max(0, self.entity.get_pos_index().get_y() - 1), len(self.level)):
            rows.append(self.level[i])

        for row in rows:
            tiles = row[self.entity.get_pos_index().get_x():self.entity.get_pos_index().get_x() + 2]
            for tile in tiles:
                if tile.rect is not None:
                    if self.entity.rect.colliderect(tile.rect):
                        if self.entity.rect.x < tile.rect.x and self.entity.vel.get_x() > 0:
                            self.entity.rect.right = tile.rect.left
                            self.entity.vel.set_x(0)
                        elif self.entity.rect.x > tile.rect.x and self.entity.vel.get_x() < 0:
                            self.entity.rect.left = tile.rect.right
                            self.entity.vel.set_x(0)

    def check_y(self):
        self.entity.on_ground = False

        rows = []
        for i in range(max(0, self.entity.get_pos_index().get_y() - 1), len(self.level)):
            rows.append(self.level[i])

        if not rows: # if there are no rows under you, then entity dies
            if hasattr(self.entity, "game_over"):
                self.entity.game_over()
            else:
                self.entity.alive = None

        for row in rows:
            tiles = row[self.entity.get_pos_index().get_x():self.entity.get_pos_index().get_x() + 2]
            for tile in tiles:
                if tile.rect is not None and self.entity.rect.colliderect(tile.rect):
                    if self.entity.rect.y < tile.rect.y and self.entity.vel.get_y() > 0:
                        self.entity.on_ground = True
                        self.entity.rect.bottom = tile.rect.top
                        self.entity.vel.set_y(0)
                        # reset jump on bottom
                        if self.entity.traits is not None:
                            if "jumpTrait" in self.entity.traits:
                                self.entity.traits["jumpTrait"].reset()
                            if "BounceTrait" in self.entity.traits:
                                self.entity.traits["BounceTrait"].reset()
                    else:
                        self.entity.rect.top = tile.rect.bottom
                        self.entity.vel.set_y(0)

    def right_level_border_reached(self):
        return self.entity.get_pos_index_as_float().get_x() > self.level_obj.level_length - 1

    def left_level_border_reached(self):
        if self.entity.rect.x < 0:
            self.entity.rect.x = 0
            self.entity.vel.set_x(0)
            return True


class BounceTrait:
    def __init__(self, entity):
        self.vel = 5
        self.jump = False
        self.entity = entity

    def update(self):
        if self.jump:
            self.entity.vel.set_y(0)
            self.entity.vel -= Vector2D(0, self.vel)
            self.jump = False
            self.entity.in_air = True

    def reset(self):
        self.entity.in_air = False

    def set(self):
        self.entity.in_air = True


class goTrait:
    def __init__(self, animation, camera, ent):
        self.animation = animation
        self.direction = 0
        self.heading = 1
        self.accel_vel = 0.4
        self.decel_vel = 0.25
        self.max_vel = 3.0
        self.boost = False
        self.camera = camera
        self.entity = ent

    def update(self):
        if self.boost:
            self.max_vel = 5.0
            self.animation.delta_time = 4
        else:
            self.animation.delta_time = 7
            if abs(self.entity.vel.get_x()) > 3.2:
                self.entity.vel.set_x(3.2 * self.heading)
            self.max_vel = 3.2

        if self.direction != 0:
            self.heading = self.direction
            if self.heading == 1:
                if self.entity.vel.get_x() < self.max_vel:
                    self.entity.vel += Vector2D(self.accel_vel * self.heading, 0)
            else:
                if self.entity.vel.get_x() > -self.max_vel:
                    self.entity.vel += Vector2D(self.accel_vel * self.heading, 0)

            if not self.entity.in_air:
                self.animation.update()
            else:
                self.animation.in_air()
        else:
            self.animation.update()
            if self.entity.vel.get_x() >= 0:
                self.entity.vel -= Vector2D(self.decel_vel, 0)
            else:
                self.entity.vel += Vector2D(self.decel_vel, 0)
            if int(self.entity.vel.get_x()) == 0:
                self.entity.vel = Vector2D(0, self.entity.vel.get_y())
                if self.entity.in_air:
                    self.animation.in_air()
                else:
                    self.animation.idle()


class jumpTrait:
    def __init__(self, entity):
        self.vertical_speed = -12  # jump speed
        self.jump_height = 120  # jump height in pixels
        self.entity = entity
        self.inital_height = 384  # stores the position of mario at jump
        self.deacceleration_height = self.jump_height - \
            ((self.vertical_speed*self.vertical_speed)/(2*self.entity.gravity))

    def jump(self, jumping):
        if jumping and not self.entity.in_air and self.entity.vel.get_y() == 0: # only jump when mario is on ground and not in a jump. redundant check
            SOUND_CONTROLLER.play_sfx(JUMP_SOUND)
            self.entity.vel.set_y(self.vertical_speed)
            self.entity.in_air = True
            self.inital_height = self.entity.rect.y
            self.entity.in_jump = True
            self.entity.obey_gravity = False  # dont obey gravity in jump so as to reach jump height no matter what the speed

        if self.entity.in_jump:  # check vertical distance travelled while mario is in a jump
            if (self.inital_height-self.entity.rect.y) >= self.deacceleration_height or self.entity.vel.get_y() == 0:
                self.entity.in_jump = False
                self.entity.obey_gravity = True  # mario obeys gravity again and continues normal play

    def reset(self):
        self.entity.in_air = False

    def set(self):
        self.entity.in_air = True


class LeftRightWalkTrait:
    def __init__(self, entity, level):
        self.direction = -1
        self.entity = entity
        self.coll_detection = Collider(self.entity, level)
        self.speed = 1
        self.entity.vel = Vector2D(self.speed * self.direction, self.entity.vel.get_y())

    def update(self):
        if self.entity.vel.get_x() == 0:
            self.direction *= -1
        self.entity.vel = Vector2D(self.speed * self.direction, self.entity.vel.get_y())
        self.move_entity()

    def move_entity(self):
        self.entity.rect.y += self.entity.vel.get_y()
        self.coll_detection.check_y()
        self.entity.rect.x += self.entity.vel.get_x()
        self.coll_detection.check_x()


class EntityCollider:
    def __init__(self, entity):
        self.entity = entity
        # initially own class
        self.is_colliding = False
        self.is_top = False

    def check(self, target):
        if self.entity.rect.colliderect(target.rect):
            return self.determine_side(target.rect, self.entity.rect)
        self.is_colliding, self.is_top = False, False
        return self.is_colliding, self.is_top

    def determine_side(self, rect1, rect2):
        if (
            rect1.collidepoint(rect2.bottomleft)
            or rect1.collidepoint(rect2.bottomright)
            or rect1.collidepoint(rect2.midbottom)
        ):
            if rect2.collidepoint(
                (rect1.midleft[0] / 2, rect1.midleft[1] / 2)
            ) or rect2.collidepoint((rect1.midright[0] / 2, rect1.midright[1] / 2)):
                self.is_colliding, self.is_top = True, False
                return self.is_colliding, self.is_top
            else:
                if self.entity.vel.get_y() > 0:
                    self.is_colliding, self.is_top = True, True
                    return self.is_colliding, self.is_top
        self.is_colliding, self.is_top = True, False
        return self.is_colliding, self.is_top
