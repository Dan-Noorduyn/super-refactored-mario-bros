import json

import pygame


class Spritesheet():
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename)
            if self.sheet.get_alpha():
                self.sheet = self.sheet.convert_alpha()
            else:
                self.sheet = self.sheet.convert()
                self.sheet.set_colorkey((255, 0, 220))
        except pygame.error:
            #print("Unable to load spritesheet image:", filename)
            raise SystemExit()

    def image_at(self, x, y, scaling_factor, color_key=None, ignore_tile_size=False,
                 x_tile_size=16, y_tile_size=16):
        if ignore_tile_size:
            rect = pygame.Rect((x, y, x_tile_size, y_tile_size))
        else:
            rect = pygame.Rect(
                (x * x_tile_size, y * y_tile_size, x_tile_size, y_tile_size))
        image = pygame.Surface(rect.size)

        image.blit(self.sheet, (0, 0), rect)
        if color_key is not None:
            if color_key == -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key, pygame.RLEACCEL)
        return pygame.transform.scale(
            image, (x_tile_size * scaling_factor, y_tile_size * scaling_factor)
        )


class Animation:
    def __init__(self, images: list, idle_sprite: pygame.Surface = None,
                 air_sprite: pygame.Surface = None, delta_time: int = 7):
        self.__images: list = images
        self.timer: int = 0
        self.__index: int = 0
        self.__image: pygame.Surface = self.__images[self.__index]
        self.__default_img: pygame.Surface = idle_sprite
        self.__air_sprite: pygame.Surface = air_sprite
        self.__delta_time: pygame.Surface = delta_time

    def update(self):
        self.timer += 1
        if self.timer % self.__delta_time == 0:
            self.__index = (self.__index + 1) % len(self.__images)
        self.__image = self.__images[self.__index]

    def idle(self):
        self.__image = self.__default_img

    def in_air(self):
        self.__image = self.__air_sprite

    def set_image(self, img: pygame.Surface):
        self.__image = img

    def get_image(self):
        return self.__image


def _load_background(sheet: Spritesheet, data: dict, out: dict) -> None:
    for sprite in data["sprites"]:
        color_key = sprite["colorKey"] if "colorKey" in sprite else None

        out[sprite["name"]] = sheet.image_at(
            sprite["x"],
            sprite["y"],
            sprite["scalefactor"],
            color_key,
        )


def _load_animation(sheet: Spritesheet, data: dict, out: dict) -> None:
    for sprite in data["sprites"]:
        images = []
        for image in sprite["images"]:
            images.append(
                sheet.image_at(
                    image["x"],
                    image["y"],
                    image["scale"],
                    sprite["colorKey"],
                )
            )
        out[sprite["name"]] = Animation(images, delta_time=sprite["deltaTime"])


def _load_main(sheet: Spritesheet, data: dict, out: dict) -> None:
    for sprite in data["sprites"]:
        color_key = sprite["colorKey"] if "colorKey" in sprite else None
        out[sprite["name"]] = sheet.image_at(
            sprite["x"],
            sprite["y"],
            sprite["scalefactor"],
            color_key=color_key,
            ignore_tile_size=True,
            x_tile_size=data["size"][0],
            y_tile_size=data["size"][1],
        )


def _load_sprites(file_list: list) -> dict:
    out: dict = {}
    for url in file_list:
        with open(url) as data:
            data: dict = json.load(data)
            sheet = Spritesheet(data["spriteSheetURL"])
            sw: dict = {
                "background": _load_background,
                "animation": _load_animation,
                "character": _load_main,
                "item": _load_main
            }
            sw[data["type"]](sheet, data, out)
    return out

def _load_font(font_path: str):
    sheet: Spritesheet = Spritesheet(font_path)
    font: dict = {}
    row: int = 0
    char_at: int = 0

    for char in _CHARS:
        if char_at == 16:
            char_at = 0
            row += 1
        font[char] = sheet.image_at(
            char_at,
            row,
            2,
            color_key=pygame.color.Color(0, 0, 0),
            x_tile_size=8,
            y_tile_size=8
        )
        char_at += 1
    return font


pygame.init()

WINDOW_SIZE: tuple = (640, 480)
SCREEN: pygame.Surface = pygame.display.set_mode(WINDOW_SIZE)

_CHARS: str = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
_FONT_PATH: str = "./resources/img/font.png"
FONT_SPRITES: dict = _load_font(_FONT_PATH)
FONT_SIZE: int = 8

_FILE_LIST = [
    "./resources/sprites/Mario.json",
    "./resources/sprites/Goomba.json",
    "./resources/sprites/Koopa.json",
    "./resources/sprites/Animations.json",
    "./resources/sprites/BackgroundSprites.json",
    "./resources/sprites/ItemAnimations.json",
    "./resources/sprites/big_mario.json",
]
SPRITE_COLLECTION: dict = _load_sprites(_FILE_LIST)
