import json
from sys import stdout

import pygame

from core.entity_base import Goomba, Koopa, Coin, RandomBox
from resources.dashboard import DASHBOARD
from resources.display import SCREEN, SPRITE_COLLECTION, Animation


class Tile:
    def __init__(self, sprite, rect):
        self.sprite = sprite
        self.rect: pygame.Rect = rect

    def __repr__(self):
        return f"Rect({self.rect.x}, {self.rect.y})"

class _Level():
    def __init__(self):
        self.levelLength: int = 0
        self.entityList: list = []
        self.level = None

    def loadLevel(self, levelname):
        self.entityList: list = []
        self.level = None
        with open("./resources/levels/{}.json".format(levelname)) as jsonData:
            data: dict = json.load(jsonData)
            self.loadLayers(data)
            self.loadObjects(data)
            self.loadEntities(data)
            self.levelLength = data["length"]

    def loadEntities(self, data):
        if "entities" not in data["level"]:
            return

        for x, y in data["level"]["entities"]["randomBox"]:
            self.addRandomBox(x, y)
        for x, y in data["level"]["entities"]["Goomba"]:
            self.addGoomba(x, y)
        for x, y in data["level"]["entities"]["Koopa"]:
            self.addKoopa(x, y)
        for x, y in data["level"]["entities"]["coin"]:
            self.addCoin(x, y)

    def loadLayers(self, data):
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
        self.level = list(map(list, zip(*layers)))

    def loadObjects(self, data):
        for x, y in data["level"]["objects"]["bush"]:
            self.addBushSprite(x, y)
        for x, y in data["level"]["objects"]["cloud"]:
            self.addCloudSprite(x, y)
        for x, y, z in data["level"]["objects"]["pipe"]:
            self.addPipeSprite(x, y, z)
        for x, y in data["level"]["objects"]["sky"]:
            self.level[y][x] = Tile(SPRITE_COLLECTION.get("sky"), None)
        for x, y in data["level"]["objects"]["ground"]:
            self.level[y][x] = Tile(
                SPRITE_COLLECTION.get("ground"),
                pygame.Rect(x * 32, y * 32, 32, 32),
            )

    def updateEntities(self, cam):
        for entity in self.entityList:
            entity.update(cam)
            if entity.alive is None:
                self.entityList.remove(entity)

    def _draw_sprite(self, sprite, x, y):
        dimensions = (x * 32, y * 32)
        if isinstance(sprite.sprite, pygame.Surface):
            SCREEN.blit(sprite.sprite, dimensions)
        elif isinstance(sprite.sprite, Animation):
            sprite.sprite.update()
            SCREEN.blit(sprite.sprite.get_image(), dimensions)

    def drawLevel(self, camera):
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
            self.updateEntities(camera)
        except IndexError:
            return

    def addCloudSprite(self, x, y):
        try:
            for yOff in range(0, 2):
                for xOff in range(0, 3):
                    self.level[y + yOff][x + xOff] = Tile(
                        SPRITE_COLLECTION.get(
                            "cloud{}_{}".format(yOff + 1, xOff + 1)
                        ),
                        None,
                    )
        except IndexError:
            return

    def addPipeSprite(self, x, y, length=2):
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

    def addBushSprite(self, x, y):
        try:
            self.level[y][x] = Tile(SPRITE_COLLECTION.get("bush_1"), None)
            self.level[y][x + 1] = Tile(
                SPRITE_COLLECTION.get("bush_2"), None
            )
            self.level[y][x + 2] = Tile(
                SPRITE_COLLECTION.get("bush_3"), None
            )
        except IndexError:
            return

    def addRandomBox(self, x, y):
        self.level[y][x] = Tile(SPRITE_COLLECTION.get("randomBox"), pygame.Rect(x * 32, y * 32 - 1, 32, 32))
        self.entityList.append(
            RandomBox(
                SPRITE_COLLECTION,
                x,
                y,
                DASHBOARD,
            )
        )

    def addCoin(self, x, y):
        self.entityList.append(Coin(SPRITE_COLLECTION, x, y))

    def addGoomba(self, x, y):
        self.entityList.append(
            Goomba(SPRITE_COLLECTION, x, y, self)
        )

    def addKoopa(self, x, y):
        self.entityList.append(
            Koopa(x, y, self)
        )

LEVEL: _Level = _Level()
