import json

import pygame

from core.entity_base import (Coin, Goomba, Koopa, MushroomItem, PowerUpBox,
                              RandomBox)
from resources.display import SCREEN, SPRITE_COLLECTION, Animation


class Tile:
    def __init__(self, sprite, rect):
        self.sprite = sprite
        self.rect: pygame.Rect = rect

    def __repr__(self):
        return f"Rect({self.rect.x}, {self.rect.y})"


class _Level():
    def __init__(self):
        self.level_length: int = 0
        self.entity_list: list = []
        self.level: list = []

    def load_level(self, level_name):
        self.entity_list.clear()
        self.level.clear()
        with open("./resources/levels/{}.json".format(level_name)) as json_data:
            data: dict = json.load(json_data)
            self.load_layers(data)
            self.load_objects(data)
            self.load_entities(data)
            self.level_length = data["length"]

    def load_entities(self, data):
        if "entities" not in data["level"]:
            return

        entities = data["level"]["entities"]

        if "randomBox" in entities:
            for x, y in entities["randomBox"]:
                self.add_random_box(x, y)
        if "PowerUpBox" in entities:
            for x, y in entities["PowerUpBox"]:
                self.add_power_box(x, y)
        if "Goomba" in entities:
            for x, y in entities["Goomba"]:
                self.add_goomba(x, y)
        if "Koopa" in entities:
            for x, y in entities["Koopa"]:
                self.add_koopa(x, y)
        if "coin" in entities:
            for x, y in entities["coin"]:
                self.add_coin(x, y)

    def load_layers(self, data):
        layers = []
        for x in range(*data["level"]["layers"]["sky"]["x"]):
            layers.append(
                (
                    [
                        Tile(SPRITE_COLLECTION.get("sky"), None)
                        for y in range(*data["level"]["layers"]["sky"]["y"])
                    ]
                    + [
                        Tile(
                            SPRITE_COLLECTION.get("ground"),
                            pygame.Rect(x * 32, (y - 1) * 32, 32, 32),
                        )
                        for y in range(*data["level"]["layers"]["ground"]["y"])
                    ]
                )
            )
        self.level[:] = map(list, zip(*layers))

    def load_objects(self, data):
        if "objects" not in data["level"]:
            return

        objects = data["level"]["objects"]

        if "bush" in objects:
            for x, y in objects["bush"]:
                self.add_bush_sprite(x, y)
        if "cloud" in objects:
            for x, y in objects["cloud"]:
                self.add_cloud_sprite(x, y)
        if "pipe" in objects:
            for x, y, z in objects["pipe"]:
                self.add_pipe_sprite(x, y, z)
        if "sky" in objects:
            for x, y in objects["sky"]:
                self.level[y][x] = Tile(SPRITE_COLLECTION.get("sky"), None)
        if "ground" in objects:
            for x, y in objects["ground"]:
                self.level[y][x] = Tile(
                    SPRITE_COLLECTION.get("ground"),
                    pygame.Rect(x * 32, y * 32, 32, 32),
                )

    def update_entities(self, cam):
        for entity in self.entity_list:
            entity.update(cam)
            if entity.alive is None:
                self.entity_list.remove(entity)

    def _draw_sprite(self, sprite, x, y):
        dimensions = (x * 32, y * 32)
        if isinstance(sprite.sprite, pygame.Surface):
            SCREEN.blit(sprite.sprite, dimensions)
        elif isinstance(sprite.sprite, Animation):
            sprite.sprite.update()
            SCREEN.blit(sprite.sprite.get_image(), dimensions)

    def draw_level(self, camera):
        try:
            for y in range(0, 15):
                for x in range(0 - int(camera.pos.get_x() + 1), 20 - int(camera.pos.get_x() - 1)):
                    if self.level[y][x].sprite is not None:
                        SCREEN.blit(
                            SPRITE_COLLECTION.get("sky"),
                            ((x + camera.pos.get_x()) * 32, y * 32),
                        )
                        self._draw_sprite(
                            self.level[y][x], x + camera.pos.get_x(), y
                        )
        except IndexError:
            return

    def add_cloud_sprite(self, x, y):
        try:
            for y_off in range(0, 2):
                for x_off in range(0, 3):
                    self.level[y + y_off][x + x_off] = Tile(
                        SPRITE_COLLECTION.get(
                            "cloud{}_{}".format(y_off + 1, x_off + 1)
                        ),
                        None,
                    )
        except IndexError:
            return

    def add_pipe_sprite(self, x, y, length=2):
        try:
            # add Pipe Head
            self.level[y][x] = Tile(
                SPRITE_COLLECTION.get("pipeL"),
                pygame.Rect(x * 32, y * 32, 32, 32),
            )
            self.level[y][x + 1] = Tile(
                SPRITE_COLLECTION.get("pipeR"),
                pygame.Rect((x + 1) * 32, y * 32, 32, 32),
            )
            # add pipe Body
            for i in range(1, length + 20):
                self.level[y + i][x] = Tile(
                    SPRITE_COLLECTION.get("pipe2L"),
                    pygame.Rect(x * 32, (y + i) * 32, 32, 32),
                )
                self.level[y + i][x + 1] = Tile(
                    SPRITE_COLLECTION.get("pipe2R"),
                    pygame.Rect((x + 1) * 32, (y + i) * 32, 32, 32),
                )
        except IndexError:
            return

    def add_bush_sprite(self, x, y):
        for i in range(0, min(3, len(self.level[y][x:]))):
            self.level[y][x + i] = Tile(SPRITE_COLLECTION.get("bush_{}".format(i + 1)), None)

    def add_random_box(self, x, y):
        self.level[y][x] = Tile(SPRITE_COLLECTION.get("randomBox"),
                                pygame.Rect(x * 32, y * 32 - 1, 32, 32))
        self.entity_list.append(RandomBox(x, y))

    def add_power_box(self, x, y):
        self.level[y][x] = Tile(SPRITE_COLLECTION.get("PowerUpBox"),
                                pygame.Rect(x * 32, y * 32 - 1, 32, 32))
        self.entity_list.append(PowerUpBox(x, y))

    def add_mushroom(self, x, y):
        self.entity_list.append(MushroomItem(x, y, self))

    def add_coin(self, x, y):
        self.entity_list.append(Coin(x, y))

    def add_goomba(self, x, y):
        self.entity_list.append(
            Goomba(x, y, self)
        )

    def add_koopa(self, x, y):
        self.entity_list.append(Koopa(x, y, self))


LEVEL: _Level = _Level()
