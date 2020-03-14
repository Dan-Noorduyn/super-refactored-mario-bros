import pygame

class Spritesheet():
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename)
            if self.sheet.get_alpha():
                self.sheet = self.sheet.convert_alpha()
            else:
                # ...
                self.sheet = self.sheet.convert()
                self.sheet.set_colorkey((255, 0, 220))
        except pygame.error:
            print("Unable to load spritesheet image:", filename)
            raise SystemExit

    def image_at(self, x, y, scalingfactor, colorkey=None, ignoreTileSize=False,
                 xTileSize=16, yTileSize=16):
        if ignoreTileSize:
            rect = pygame.Rect((x, y, xTileSize, yTileSize))
        else:
            rect = pygame.Rect((x * xTileSize, y * yTileSize, xTileSize, yTileSize))
        image = pygame.Surface(rect.size)
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return pygame.transform.scale(
            image, (xTileSize * scalingfactor, yTileSize * scalingfactor)
        )

def _load_font(font_path: str):
    font_spritesheet: Spritesheet = Spritesheet(font_path)
    font: dict = {}
    row: int = 0
    charAt: int = 0

    for char in _CHARS:
        if charAt == 16:
            charAt = 0
            row += 1
        font.update(
            {
                char: font_spritesheet.image_at(
                    charAt,
                    row,
                    2,
                    colorkey=pygame.color.Color(0, 0, 0),
                    xTileSize = 8,
                    yTileSize = 8
                )
            }
        )
        charAt += 1
    return font

pygame.init()
pygame.display.init()

WINDOW_SIZE: tuple = (640, 480)
SCREEN: pygame.Surface = pygame.display.set_mode(WINDOW_SIZE)

_CHARS: str = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
_FONT_PATH: str = "./resources/img/font.png"
FONT_SPRITES: dict = _load_font(_FONT_PATH)
