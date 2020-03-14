import json
import os
import sys
from copy import copy
from random import randint

import pygame
from pygame.locals import *
from pygame.transform import flip
from scipy.ndimage.filters import gaussian_filter

from resources.sound import *
from resources.display import FONT_SPRITES, Spritesheet, SCREEN
from utils.physics import Vector2D

class Animation:
    def __init__(self, images, idleSprite=None, airSprite=None, deltaTime=7):
        self.images = images
        self.timer = 0
        self.index = 0
        self.image = self.images[self.index]
        self.idleSprite = idleSprite
        self.airSprite = airSprite
        self.deltaTime = deltaTime

    def update(self):
        self.timer += 1
        if self.timer % self.deltaTime == 0:
            if self.index < len(self.images) - 1:
                self.index += 1
            else:
                self.index = 0
        self.image = self.images[self.index]

    def idle(self):
        self.image = self.idleSprite

    def inAir(self):
        self.image = self.airSprite

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


class Collider:
    def __init__(self, entity, level):
        self.entity = entity
        self.level = level.level
        self.levelObj = level
        self.result = []

    def checkX(self):
        if self.leftLevelBorderReached() or self.rightLevelBorderReached():
            return
        # try:
        rows = [
            self.level[self.entity.getPosIndex().get_x()],
            self.level[self.entity.getPosIndex().get_y() + 1],
        ]
        # except Exception:
            # return
        for row in rows:
            tiles = row[self.entity.getPosIndex().get_x() : self.entity.getPosIndex().get_x() + 2]
            for tile in tiles:
                if tile.rect is not None:
                    if self.entity.rect.colliderect(tile.rect):
                        if self.entity.vel.get_x() > 0:
                            self.entity.rect.right = tile.rect.left
                            self.entity.vel = Vector2D(0, self.entity.vel.get_y())
                        if self.entity.vel.get_x() < 0:
                            self.entity.rect.left = tile.rect.right
                            self.entity.vel = Vector2D(0, self.entity.vel.get_y())

    def checkY(self):
        self.entity.onGround = False
        # try:
        rows = [
            self.level[self.entity.getPosIndex().get_x()],
            self.level[self.entity.getPosIndex().get_y() + 1],
        ]
        # except Exception:
            # try:
                # self.entity.gameOver()
            # except Exception:
                # self.entity.alive = None
            # return
        for row in rows:
            tiles = row[self.entity.getPosIndex().get_x() : self.entity.getPosIndex().get_x() + 2]
            for tile in tiles:
                if tile.rect is not None:
                    if self.entity.rect.colliderect(tile.rect):
                        if self.entity.vel.get_y() > 0:
                            self.entity.onGround = True
                            self.entity.rect.bottom = tile.rect.top
                            self.entity.vel = Vector2D(self.entity.vel.get_x(), 0)
                            # reset jump on bottom
                            if self.entity.traits is not None:
                                if "jumpTrait" in self.entity.traits:
                                    self.entity.traits["jumpTrait"].reset()
                                if "bounceTrait" in self.entity.traits:
                                    self.entity.traits["bounceTrait"].reset()
                        if self.entity.vel.get_y() < 0:
                            self.entity.rect.top = tile.rect.bottom
                            self.entity.vel = Vector2D(self.entity.vel.get_x(), 0)

    def rightLevelBorderReached(self):
        if self.entity.getPosIndexAsFloat().get_x() > self.levelObj.levelLength - 1:
            self.entity.rect.x = (self.levelObj.levelLength - 1) * 32
            self.entity.vel = Vector2D(0, self.entity.vel.get_y())
            return True

    def leftLevelBorderReached(self):
        if self.entity.rect.x < 0:
            self.entity.rect.x = 0
            self.entity.vel = Vector2D(0, self.entity.vel.get_y())
            return True

class Dashboard():
    def __init__(self, screen, size):
        self.state = "menu"
        self.screen = screen
        self.levelName = ""
        self.points = 0
        self.coins = 0
        self.ticks = 0
        self.time = 0

    def update(self):
        self.drawText("MARIO", 50, 20, 15)
        self.drawText(self.pointString(), 50, 37, 15)

        self.drawText("@x{}".format(self.coinString()), 225, 37, 15)

        self.drawText("WORLD", 380, 20, 15)
        self.drawText(str(self.levelName), 395, 37, 15)

        self.drawText("TIME", 520, 20, 15)
        if self.state != "menu":
            self.drawText(self.timeString(), 535, 37, 15)

        # update Time
        self.ticks += 1
        if self.ticks == 60:
            self.ticks = 0
            self.time += 1

    def drawText(self, text, x, y, size):
        for char in text:
            charSprite = pygame.transform.scale(FONT_SPRITES[char], (size, size))
            self.screen.blit(charSprite, (x, y))
            if char == " ":
                x += size//2
            else:
                x += size

    def coinString(self):
        return "{:02d}".format(self.coins)

    def pointString(self):
        return "{:06d}".format(self.points)

    def timeString(self):
        return "{:03d}".format(self.time)

class EntityCollider:
    def __init__(self, entity):
        self.entity = entity

    def check(self, target):
        if self.entity.rect.colliderect(target.rect):
            return self.determineSide(target.rect, self.entity.rect)
        return CollisionState(False, False)

    def determineSide(self, rect1, rect2):
        if (
            rect1.collidepoint(rect2.bottomleft)
            or rect1.collidepoint(rect2.bottomright)
            or rect1.collidepoint(rect2.midbottom)
        ):
            if rect2.collidepoint(
                (rect1.midleft[0] / 2, rect1.midleft[1] / 2)
            ) or rect2.collidepoint((rect1.midright[0] / 2, rect1.midright[1] / 2)):
                return CollisionState(True, False)
            else:
                if self.entity.vel.get_y() > 0:
                    return CollisionState(True, True)
        return CollisionState(True, False)


class CollisionState:
    def __init__(self, _isColliding, _isTop):
        self.isColliding = _isColliding
        self.isTop = _isTop

class GaussianBlur:
    def __init__(self, kernelsize: int = 7):
        self.kernel_size = kernelsize

    def filter(self, srfc, xpos, ypos, width, height):
        nSrfc = pygame.Surface((width, height))
        pxa = pygame.surfarray.array3d(srfc)
        blurred = gaussian_filter(pxa, sigma=(self.kernel_size, self.kernel_size, 0))
        pygame.surfarray.blit_array(nSrfc, blurred)
        del pxa
        return nSrfc

class Input:
    def __init__(self, entity):
        self.mouseX = 0
        self.mouseY = 0
        self.entity = entity

    def checkForInput(self):
        self.checkForKeyboardInput()
        self.checkForMouseInput()
        self.checkForQuitAndRestartInputEvents()

    def checkForKeyboardInput(self):
        pressedKeys = pygame.key.get_pressed()

        if pressedKeys[K_LEFT] and not pressedKeys[K_RIGHT]:
            self.entity.traits["goTrait"].direction = -1
        elif pressedKeys[K_RIGHT] and not pressedKeys[K_LEFT]:
            self.entity.traits["goTrait"].direction = 1
        else:
            self.entity.traits['goTrait'].direction = 0

        isJumping = pressedKeys[K_SPACE] or pressedKeys[K_UP]
        self.entity.traits['jumpTrait'].jump(isJumping)

        self.entity.traits['goTrait'].boost = pressedKeys[K_LSHIFT]

    def checkForMouseInput(self):
        mouseX, mouseY = pygame.mouse.get_pos()
        if self.isRightMouseButtonPressed():
            self.entity.levelObj.addKoopa(
                mouseY / 32, mouseX / 32 - self.entity.camera.pos.get_x()
            )
            self.entity.levelObj.addGoomba(
                mouseY / 32, mouseX / 32 - self.entity.camera.pos.get_x()
            )
        if self.isLeftMouseButtonPressed():
            self.entity.levelObj.addCoin(
                mouseX / 32 - self.entity.camera.pos.get_x(), mouseY / 32
            )

    def checkForQuitAndRestartInputEvents(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and \
                (event.key == pygame.K_ESCAPE or event.key == pygame.K_F5):
                self.entity.pause = True
                self.entity.pauseObj.createBackgroundBlur()

    def isLeftMouseButtonPressed(self):
        return pygame.mouse.get_pressed()[0]

    def isRightMouseButtonPressed(self):
        return pygame.mouse.get_pressed()[2]

class Level:
    def __init__(self, screen, dashboard):
        self.sprites = Sprites()
        self.dashboard = dashboard
        self.screen = screen
        self.level = None
        self.levelLength = 0
        self.entityList = []

    def loadLevel(self, levelname):
        with open("./resources/levels/{}.json".format(levelname)) as jsonData:
            data = json.load(jsonData)
            self.loadLayers(data)
            self.loadObjects(data)
            self.loadEntities(data)
            self.levelLength = data["length"]

    def loadEntities(self, data):
        try:
            [self.addRandomBox(x, y) for x, y in data["level"]["entities"]["randomBox"]]
            [self.addGoomba(x, y) for x, y in data["level"]["entities"]["Goomba"]]
            [self.addKoopa(x, y) for x, y in data["level"]["entities"]["Koopa"]]
            [self.addCoin(x, y) for x, y in data["level"]["entities"]["coin"]]
        except:
            #if no entities in Level
            pass

    def loadLayers(self, data):
        layers = []
        for x in range(*data["level"]["layers"]["sky"]["x"]):
            layers.append(
                (
                    [
                        Tile(self.sprites.spriteCollection.get("sky"), None)
                        for y in range(*data["level"]["layers"]["sky"]["y"])
                    ]
                    + [
                        Tile(
                            self.sprites.spriteCollection.get("ground"),
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
            self.level[y][x] = Tile(self.sprites.spriteCollection.get("sky"), None)
        for x, y in data["level"]["objects"]["ground"]:
            self.level[y][x] = Tile(
                self.sprites.spriteCollection.get("ground"),
                pygame.Rect(x * 32, y * 32, 32, 32),
            )

    def updateEntities(self, cam):
        for entity in self.entityList:
            entity.update(cam)
            if entity.alive is None:
                self.entityList.remove(entity)

    def drawLevel(self, camera):
        try:
            for y in range(0, 15):
                for x in range(0 - int(camera.pos.get_x() + 1), 20 - int(camera.pos.get_x() - 1)):
                    if self.level[y][x].sprite is not None:
                        if self.level[y][x].sprite.redrawBackground:
                            self.screen.blit(
                                self.sprites.spriteCollection.get("sky").image,
                                ((x + camera.pos.get_x()) * 32, y * 32),
                            )
                        self.level[y][x].sprite.drawSprite(
                            x + camera.pos.get_x(), y, self.screen
                        )
            self.updateEntities(camera)
        except IndexError:
            return

    def addCloudSprite(self, x, y):
        try:
            for yOff in range(0, 2):
                for xOff in range(0, 3):
                    self.level[y + yOff][x + xOff] = Tile(
                        self.sprites.spriteCollection.get(
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
                self.sprites.spriteCollection.get("pipeL"),
                pygame.Rect(x * 32, y * 32, 32, 32),
            )
            self.level[y][x + 1] = Tile(
                self.sprites.spriteCollection.get("pipeR"),
                pygame.Rect((x + 1) * 32, y * 32, 32, 32),
            )
            # add pipe Body
            for i in range(1, length + 20):
                self.level[y + i][x] = Tile(
                    self.sprites.spriteCollection.get("pipe2L"),
                    pygame.Rect(x * 32, (y + i) * 32, 32, 32),
                )
                self.level[y + i][x + 1] = Tile(
                    self.sprites.spriteCollection.get("pipe2R"),
                    pygame.Rect((x + 1) * 32, (y + i) * 32, 32, 32),
                )
        except IndexError:
            return

    def addBushSprite(self, x, y):
        try:
            self.level[y][x] = Tile(self.sprites.spriteCollection.get("bush_1"), None)
            self.level[y][x + 1] = Tile(
                self.sprites.spriteCollection.get("bush_2"), None
            )
            self.level[y][x + 2] = Tile(
                self.sprites.spriteCollection.get("bush_3"), None
            )
        except IndexError:
            return

    def addRandomBox(self, x, y):
        self.level[y][x] = Tile(None, pygame.Rect(x * 32, y * 32 - 1, 32, 32))
        self.entityList.append(
            RandomBox(
                self.screen,
                self.sprites.spriteCollection,
                x,
                y,
                self.dashboard,
            )
        )

    def addCoin(self, x, y):
        self.entityList.append(Coin(self.screen, self.sprites.spriteCollection, x, y))

    def addGoomba(self, x, y):
        self.entityList.append(
            Goomba(self.screen, self.sprites.spriteCollection, x, y, self)
        )

    def addKoopa(self, x, y):
        self.entityList.append(
            Koopa(self.screen, self.sprites.spriteCollection, x, y, self)
        )

class Menu:
    def __init__(self, screen, dashboard, level):
        self.screen = screen
        self.start = False
        self.inSettings = False
        self.state = 0
        self.level = level
        self.music = True
        self.sfx = True
        self.currSelectedLevel = 1
        self.levelNames = []
        self.inChoosingLevel = False
        self.dashboard = dashboard
        self.levelCount = 0
        self.spritesheet = Spritesheet("./resources/img/title_screen.png")
        self.menu_banner = self.spritesheet.image_at(
            0,
            60,
            2,
            colorkey=[255, 0, 220],
            ignoreTileSize=True,
            xTileSize=180,
            yTileSize=88,
        )
        self.menu_dot = self.spritesheet.image_at(
            0, 150, 2, colorkey=[255, 0, 220], ignoreTileSize=True
        )
        self.menu_dot2 = self.spritesheet.image_at(
  	        20, 150, 2, colorkey=[255, 0, 220], ignoreTileSize=True
        )
        self.loadSettings("./settings.json")

    def update(self):
        self.checkInput()
        if self.inChoosingLevel:
            return

        self.drawMenuBackground()
        self.dashboard.update()

        if not self.inSettings:
            self.drawMenu()
        else:
            self.drawSettings()

    def drawDot(self):
        if self.state == 0:
            self.screen.blit(self.menu_dot, (145, 273))
            self.screen.blit(self.menu_dot2, (145, 313))
            self.screen.blit(self.menu_dot2, (145, 353))
        elif self.state == 1:
            self.screen.blit(self.menu_dot, (145, 313))
            self.screen.blit(self.menu_dot2, (145, 273))
            self.screen.blit(self.menu_dot2, (145, 353))
        elif self.state == 2:
            self.screen.blit(self.menu_dot, (145, 353))
            self.screen.blit(self.menu_dot2, (145, 273))
            self.screen.blit(self.menu_dot2, (145, 313))

    def loadSettings(self, url):
        try:
            with open(url) as jsonData:
                data = json.load(jsonData)
                if data["sound"]:
                    self.music = True
                    SOUND_CONTROLLER.unmute_music()
                    SOUND_CONTROLLER.play_music(SOUNDTRACK)
                else:
                    self.music = False
                    SOUND_CONTROLLER.mute_music()
                if data["sfx"]:
                    self.sfx = True
                    SOUND_CONTROLLER.unmute_sfx()
                else:
                    self.sfx = False
                    SOUND_CONTROLLER.mute_sfx()

        except (IOError, OSError):
            self.music = False
            self.sfx = False
            SOUND_CONTROLLER.mute_music()
            SOUND_CONTROLLER.mute_sfx()
            self.saveSettings("./settings.json")

    def saveSettings(self, url):
        data = {"sound": self.music, "sfx": self.sfx}
        with open(url, "w") as outfile:
            json.dump(data, outfile)

    def drawMenu(self):
        self.drawDot()
        self.dashboard.drawText("CHOOSE LEVEL", 180, 280, 24)
        self.dashboard.drawText("SETTINGS", 180, 320, 24)
        self.dashboard.drawText("EXIT", 180, 360, 24)

    def drawMenuBackground(self, withBanner=True):
        for y in range(0, 13):
            for x in range(0, 20):
                self.screen.blit(
                    self.level.sprites.spriteCollection.get("sky").image,
                    (x * 32, y * 32),
                )
        for y in range(13, 15):
            for x in range(0, 20):
                self.screen.blit(
                    self.level.sprites.spriteCollection.get("ground").image,
                    (x * 32, y * 32),
                )
        if(withBanner):
            self.screen.blit(self.menu_banner, (150, 80))
        self.screen.blit(
            self.level.sprites.spriteCollection.get("mario_idle").image,
            (2 * 32, 12 * 32),
        )
        self.screen.blit(
            self.level.sprites.spriteCollection.get("bush_1").image, (14 * 32, 12 * 32)
        )
        self.screen.blit(
            self.level.sprites.spriteCollection.get("bush_2").image, (15 * 32, 12 * 32)
        )
        self.screen.blit(
            self.level.sprites.spriteCollection.get("bush_2").image, (16 * 32, 12 * 32)
        )
        self.screen.blit(
            self.level.sprites.spriteCollection.get("bush_2").image, (17 * 32, 12 * 32)
        )
        self.screen.blit(
            self.level.sprites.spriteCollection.get("bush_3").image, (18 * 32, 12 * 32)
        )
        self.screen.blit(self.level.sprites.spriteCollection.get("goomba-1").image,(18.5*32,12*32))

    def drawSettings(self):
        self.drawDot()
        self.dashboard.drawText("MUSIC", 180, 280, 24)
        if self.music:
            self.dashboard.drawText("ON", 340, 280, 24)
        else:
            self.dashboard.drawText("OFF", 340, 280, 24)
        self.dashboard.drawText("SFX", 180, 320, 24)
        if self.sfx:
            self.dashboard.drawText("ON", 340, 320, 24)
        else:
            self.dashboard.drawText("OFF", 340, 320, 24)
        self.dashboard.drawText("BACK", 180, 360, 24)

    def chooseLevel(self):
        self.drawMenuBackground(False)
        self.inChoosingLevel = True
        self.levelNames = self.loadLevelNames()
        self.drawLevelChooser()

    def drawBorder(self,x,y,width,height,color,thickness):
        pygame.draw.rect(self.screen,color,(x,y,width,thickness))
        pygame.draw.rect(self.screen,color,(x,y+width,width,thickness))
        pygame.draw.rect(self.screen,color,(x,y,thickness,width))
        pygame.draw.rect(self.screen,color,(x+width,y,thickness,width+thickness))

    def drawLevelChooser(self):
        j = 0
        offset = 75
        textOffset = 90
        for i, levelName in enumerate(self.loadLevelNames()):
            if self.currSelectedLevel == i+1:
                color = (255,255,255)
            else:
                color = (150,150,150)
            if i < 3:
                self.dashboard.drawText(levelName,175*i+textOffset,100,12)
                self.drawBorder(175*i+offset,55,125,75,color,5)
            else:
                self.dashboard.drawText(levelName,175*j+textOffset,250,12)
                self.drawBorder(175*j+offset,210,125,75,color,5)
                j+=1

    def loadLevelNames(self):
        files = []
        res = []
        for r, d, f in os.walk("./resources/levels"):
            for file in f:
                files.append(os.path.join(r, file))
        for f in files:
            res.append(os.path.split(f)[1].split(".")[0])
        self.levelCount = len(res)
        return res

    def checkInput(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.inChoosingLevel or self.inSettings:
                        self.inChoosingLevel = False
                        self.inSettings = False
                        self.__init__(self.screen, self.dashboard, self.level)
                    else:
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_UP:
                    if self.inChoosingLevel:
                        if self.currSelectedLevel > 3:
                            self.currSelectedLevel -= 3
                            self.drawLevelChooser()
                    if self.state > 0:
                        self.state -= 1
                elif event.key == pygame.K_DOWN:
                    if self.inChoosingLevel:
                        if self.currSelectedLevel+3 <= self.levelCount:
                            self.currSelectedLevel += 3
                            self.drawLevelChooser()
                    if self.state < 2:
                        self.state += 1
                elif event.key == pygame.K_LEFT:
                    if self.currSelectedLevel > 1:
                        self.currSelectedLevel -= 1
                        self.drawLevelChooser()
                elif event.key == pygame.K_RIGHT:
                    if self.currSelectedLevel < self.levelCount:
                        self.currSelectedLevel += 1
                        self.drawLevelChooser()
                elif event.key == pygame.K_RETURN:
                    if self.inChoosingLevel:
                        self.inChoosingLevel = False
                        self.dashboard.state = "start"
                        self.dashboard.time = 0
                        self.level.loadLevel(self.levelNames[self.currSelectedLevel-1])
                        self.dashboard.levelName = self.levelNames[self.currSelectedLevel-1].split("Level")[1]
                        self.start = True
                        return
                    if not self.inSettings:
                        if self.state == 0:
                            self.chooseLevel()
                        elif self.state == 1:
                            self.inSettings = True
                            self.state = 0
                        elif self.state == 2:
                            pygame.quit()
                            sys.exit()
                    else:
                        if self.state == 0:
                            if self.music:
                                self.music = False
                                SOUND_CONTROLLER.stop_music()
                            else:
                                SOUND_CONTROLLER.play_music(SOUNDTRACK)
                                self.music = True
                            self.saveSettings("./settings.json")
                        elif self.state == 1:
                            if self.sfx:
                                SOUND_CONTROLLER.mute_sfx()
                                self.sfx = False
                            else:
                                SOUND_CONTROLLER.unmute_sfx()
                                self.sfx = True
                            self.saveSettings("./settings.json")
                        elif self.state == 2:
                            self.inSettings = False
        pygame.display.update()

class Pause:
    def __init__(self, screen, entity, dashboard):
        self.screen = screen
        self.entity = entity
        self.dashboard = dashboard
        self.state = 0
        self.spritesheet = Spritesheet("./resources/img/title_screen.png")
        self.pause_srfc = GaussianBlur().filter(self.screen, 0, 0, 640, 480)
        self.dot = self.spritesheet.image_at(
            0, 150, 2, colorkey=[255, 0, 220], ignoreTileSize=True
        )
        self.gray_dot = self.spritesheet.image_at(
  	        20, 150, 2, colorkey=[255, 0, 220], ignoreTileSize=True
        )

    def update(self):
        self.screen.blit(self.pause_srfc,(0,0))
        self.dashboard.drawText("PAUSED", 120, 160, 68)
        self.dashboard.drawText("CONTINUE", 150, 280, 32)
        self.dashboard.drawText("BACK TO MENU", 150, 320, 32)
        self.drawDot()
        pygame.display.update()
        self.checkInput()

    def drawDot(self):
        if self.state == 0:
            self.screen.blit(self.dot, (100, 275))
            self.screen.blit(self.gray_dot, (100, 315))
        elif self.state == 1:
            self.screen.blit(self.dot, (100, 315))
            self.screen.blit(self.gray_dot, (100, 275))

    def checkInput(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.state == 0:
                        self.entity.pause = False
                    elif self.state == 1:
                        self.entity.restart = True
                elif event.key == pygame.K_UP:
                    if self.state > 0:
                        self.state -= 1
                elif event.key == pygame.K_DOWN:
                    if self.state < 1:
                        self.state += 1

    def createBackgroundBlur(self):
        self.pause_srfc = GaussianBlur().filter(self.screen, 0, 0, 640, 480)

class Sprite:
    def __init__(self, image, colliding, animation=None, redrawBackground=False):
        self.image = image
        self.colliding = colliding
        self.animation = animation
        self.redrawBackground = redrawBackground

    def drawSprite(self, x, y, screen):
        dimensions = (x * 32, y * 32)
        if self.animation is None:
            screen.blit(self.image, dimensions)
        else:
            self.animation.update()
            screen.blit(self.animation.image, dimensions)




class Sprites:
    def __init__(self):
        self.spriteCollection = self.loadSprites(
            [
                "./resources/sprites/Mario.json",
                "./resources/sprites/Goomba.json",
                "./resources/sprites/Koopa.json",
                "./resources/sprites/Animations.json",
                "./resources/sprites/BackgroundSprites.json",
                "./resources/sprites/ItemAnimations.json",
            ]
        )

    def loadSprites(self, urlList):
        resDict = {}
        for url in urlList:
            with open(url) as jsonData:
                data = json.load(jsonData)
                mySpritesheet = Spritesheet(data["spriteSheetURL"])
                dic = {}
                if data["type"] == "background":
                    for sprite in data["sprites"]:
                        try:
                            colorkey = sprite["colorKey"]
                        except KeyError:
                            colorkey = None
                        dic[sprite["name"]] = Sprite(
                            mySpritesheet.image_at(
                                sprite["x"],
                                sprite["y"],
                                sprite["scalefactor"],
                                colorkey,
                            ),
                            sprite["collision"],
                            None,
                            sprite["redrawBg"],
                        )
                    resDict.update(dic)
                    continue
                elif data["type"] == "animation":
                    for sprite in data["sprites"]:
                        images = []
                        for image in sprite["images"]:
                            images.append(
                                mySpritesheet.image_at(
                                    image["x"],
                                    image["y"],
                                    image["scale"],
                                    colorkey=sprite["colorKey"],
                                )
                            )
                        dic[sprite["name"]] = Sprite(
                            None,
                            None,
                            animation=Animation(images, deltaTime=sprite["deltaTime"]),
                        )
                    resDict.update(dic)
                    continue
                elif data["type"] == "character" or data["type"] == "item":
                    for sprite in data["sprites"]:
                        try:
                            colorkey = sprite["colorKey"]
                        except KeyError:
                            colorkey = None
                        dic[sprite["name"]] = Sprite(
                            mySpritesheet.image_at(
                                sprite["x"],
                                sprite["y"],
                                sprite["scalefactor"],
                                colorkey,
                                True,
                                xTileSize=data["size"][0],
                                yTileSize=data["size"][1],
                            ),
                            sprite["collision"],
                        )
                    resDict.update(dic)
                    continue
        return resDict


class Tile:
    def __init__(self, sprite, rect):
        self.sprite = sprite
        self.rect = rect

class EntityBase(object):
    def __init__(self, x, y, gravity):
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
    def __init__(self, screen, spriteCollection, x, y, gravity=0):
        super(Coin, self).__init__(x, y, gravity)
        self.screen = screen
        self.spriteCollection = spriteCollection
        self.animation = copy(self.spriteCollection.get("coin").animation)
        self.type = "Item"

    def update(self, cam):
        if self.alive:
            self.animation.update()
            self.screen.blit(self.animation.image, (self.rect.x + cam.x, self.rect.y))

class Goomba(EntityBase):
    def __init__(self, screen, spriteColl, x, y, level):
        super(Goomba, self).__init__(y, x - 1, 1.25)
        self.spriteCollection = spriteColl
        self.animation = Animation(
            [
                self.spriteCollection.get("goomba-1").image,
                self.spriteCollection.get("goomba-2").image,
            ]
        )
        self.screen = screen
        self.leftrightTrait = LeftRightWalkTrait(self, level)
        self.type = "Mob"
        self.dashboard = level.dashboard

    def update(self, camera):
        if self.alive:
            self.applyGravity()
            self.drawGoomba(camera)
            self.leftrightTrait.update()
        else:
            self.onDead(camera)

    def drawGoomba(self, camera):
        self.screen.blit(self.animation.image, (self.rect.x + camera.x, self.rect.y))
        self.animation.update()

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
        self.screen.blit(
            self.spriteCollection.get("goomba-flat").image,
            (self.rect.x + camera.x, self.rect.y),
        )

    def setPointsTextStartPosition(self, x, y):
        self.textPos = Vector2D(x, y)

    def movePointsTextUpAndDraw(self, camera):
        self.textPos += Vector2D(-0.5, 0)
        self.dashboard.drawText("100", self.textPos.get_x() + camera.x, self.textPos.get_y(), 8)




class Item(Dashboard):
    def __init__(self, collection, screen, x, y):
        super(Item, self).__init__(8, screen)
        self.ItemPos = Vector2D(x, y)
        self.itemVel = Vector2D(0, 0)
        self.screen = screen
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
            self.screen.blit(
                self.coin_animation.image, (self.ItemPos.get_x() + cam.x, self.ItemPos.get_y())
            )
        elif self.coin_animation.timer < 80:
            self.itemVel = Vector2D(0, -0.75)
            self.ItemPos += Vector2D(0, self.itemVel.get_y())
            self.drawText("100", self.ItemPos.get_x() + 3 + cam.x, self.ItemPos.get_y(), 8)




class Koopa(EntityBase):
    def __init__(self, screen, spriteColl, x, y, level):
        super(Koopa, self).__init__(y - 1, x, 1.25)
        self.spriteCollection = spriteColl
        self.animation = Animation(
            [
                self.spriteCollection.get("koopa-1").image,
                self.spriteCollection.get("koopa-2").image,
            ]
        )
        self.screen = screen
        self.leftrightTrait = LeftRightWalkTrait(self, level)
        self.timer = 0
        self.timeAfterDeath = 35
        self.type = "Mob"
        self.dashboard = level.dashboard

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
            self.screen.blit(
                self.animation.image, (self.rect.x + camera.x, self.rect.y - 32)
            )
        else:
            self.screen.blit(
                pygame.transform.flip(self.animation.image, True, False),
                (self.rect.x + camera.x, self.rect.y - 32),
            )

    def shellBouncing(self, camera):
        self.leftrightTrait.speed = 4
        self.applyGravity()
        self.animation.image = self.spriteCollection.get("koopa-hiding").image
        self.drawKoopa(camera)
        self.leftrightTrait.update()

    def die(self, camera):
        if self.timer == 0:
            self.textPos = Vector2D(self.rect.x + 3, self.rect.y - 32)
        if self.timer < self.timeAfterDeath:
            self.textPos += Vector2D(0, -0.5)
            self.dashboard.drawText("100", self.textPos.get_x() + camera.x, self.textPos.get_y(), 8)
            self.vel -= Vector2D(0, 0.5)
            self.rect.y += self.vel.get_y()
            self.screen.blit(
                self.spriteCollection.get("koopa-hiding").image,
                (self.rect.x + camera.x, self.rect.y - 32),
            )
        else:
            self.vel += Vector2D(0, 0.3)
            self.rect.y += self.vel.get_y()
            self.textPos += Vector2D(0, -0.5)
            self.dashboard.drawText("100", self.textPos.get_x() + camera.x, self.textPos.get_y(), 8)
            self.screen.blit(
                self.spriteCollection.get("koopa-hiding").image,
                (self.rect.x + camera.x, self.rect.y - 32),
            )
            if self.timer > 500:
                # delete entity
                self.alive = None
        self.timer += 6

    def sleepingInShell(self, camera):
        if self.timer < self.timeAfterDeath:
            self.screen.blit(
                self.spriteCollection.get("koopa-hiding").image,
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




class Mario(EntityBase):
    def __init__(self, x, y, level, screen, dashboard, gravity=0.75):
        super(Mario, self).__init__(x, y, gravity)
        self.spriteCollection = Sprites().spriteCollection
        self.camera = Camera(self.rect, self)
        self.input = Input(self)
        self.inAir = False
        self.inJump = False
        self.animation = Animation(
            [
                self.spriteCollection["mario_run1"].image,
                self.spriteCollection["mario_run2"].image,
                self.spriteCollection["mario_run3"].image,
            ],
            self.spriteCollection["mario_idle"].image,
            self.spriteCollection["mario_jump"].image,
        )

        self.traits = {
            "jumpTrait": jumpTrait(self),
            "goTrait": goTrait(self.animation, screen, self.camera, self),
            "bounceTrait": bounceTrait(self),
        }

        self.levelObj = level
        self.collision = Collider(self, level)
        self.screen = screen
        self.EntityCollider = EntityCollider(self)
        self.dashboard = dashboard
        self.restart = False
        self.pause = False
        self.pauseObj = Pause(screen, self, dashboard)

    def update(self):
        self.updateTraits()
        self.moveMario()
        self.camera.move()
        self.applyGravity()
        self.checkEntityCollision()
        self.input.checkForInput()

    def moveMario(self):
        self.rect.y += self.vel.get_y()
        self.collision.checkY()
        self.rect.x += self.vel.get_x()
        self.collision.checkX()

    def checkEntityCollision(self):
        for ent in self.levelObj.entityList:
            collisionState = self.EntityCollider.check(ent)
            if collisionState.isColliding:
                if ent.type == "Item":
                    self._onCollisionWithItem(ent)
                elif ent.type == "Block":
                    self._onCollisionWithBlock(ent)
                elif ent.type == "Mob":
                    self._onCollisionWithMob(ent, collisionState)

    def _onCollisionWithItem(self, item):
        self.levelObj.entityList.remove(item)
        self.dashboard.points += 100
        self.dashboard.coins += 1
        SOUND_CONTROLLER.play_sfx(COIN_SOUND)

    def _onCollisionWithBlock(self, block):
        if not block.triggered:
            self.dashboard.coins += 1
            SOUND_CONTROLLER.play_sfx(BUMP_SOUND)
        block.triggered = True

    def _onCollisionWithMob(self, mob, collisionState):
        if collisionState.isTop and (mob.alive or mob.alive == "shellBouncing"):
            SOUND_CONTROLLER.play_sfx(STOMP_SOUND)
            self.rect.bottom = mob.rect.top
            self.bounce()
            self.killEntity(mob)
        elif collisionState.isTop and mob.alive == "sleeping":
            SOUND_CONTROLLER.play_sfx(STOMP_SOUND)
            self.rect.bottom = mob.rect.top
            mob.timer = 0
            self.bounce()
            mob.alive = False
        elif collisionState.isColliding and mob.alive == "sleeping":
            if mob.rect.x < self.rect.x:
                mob.leftrightTrait.direction = -1
                mob.rect.x += -5
            else:
                mob.rect.x += 5
                mob.leftrightTrait.direction = 1
            mob.alive = "shellBouncing"
        elif collisionState.isColliding and mob.alive:
            self.gameOver()

    def bounce(self):
        self.traits["bounceTrait"].jump = True

    def killEntity(self, ent):
        if ent.__class__.__name__ != "Koopa":
            ent.alive = False
        else:
            ent.timer = 0
            ent.alive = "sleeping"
        self.dashboard.points += 100

    def gameOver(self):
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
            self.screen.blit(srf, (0, 0))
            pygame.display.update()
            self.input.checkForInput()
        while SOUND_CONTROLLER.playing_music():
            pygame.display.update()
            self.input.checkForInput()
        self.restart = True

    def getPos(self):
        return self.camera.x + self.rect.x, self.rect.y

    def setPos(self,x,y):
        self.rect.x = x
        self.rect.y = y




class RandomBox(EntityBase):
    def __init__(self, screen, spriteCollection, x, y, dashboard, gravity=0):
        super(RandomBox, self).__init__(x, y, gravity)
        self.screen = screen
        self.spriteCollection = spriteCollection
        self.animation = copy(self.spriteCollection.get("randomBox").animation)
        self.type = "Block"
        self.triggered = False
        self.time = 0
        self.maxTime = 10
        self.dashboard = dashboard
        self.vel = 1
        self.item = Item(spriteCollection, screen, self.rect.x, self.rect.y)

    def update(self, cam):
        if self.alive and not self.triggered:
            self.animation.update()
        else:
            self.animation.image = self.spriteCollection.get("empty").image
            self.item.spawnCoin(cam, self.dashboard)
            if self.time < self.maxTime:
                self.time += 1
                self.rect.y -= self.vel
            else:
                if self.time < self.maxTime * 2:
                    self.time += 1
                    self.rect.y += self.vel
        self.screen.blit(
            self.spriteCollection.get("sky").image,
            (self.rect.x + cam.x, self.rect.y + 2),
        )
        self.screen.blit(self.animation.image, (self.rect.x + cam.x, self.rect.y - 1))

class bounceTrait:
    def __init__(self, entity):
        self.vel = 5
        self.jump = False
        self.entity = entity

    def update(self):
        if self.jump:
            self.entity.vel = Vector2D(self.entity.get_x(), 0)
            self.entity.vel -= Vector(0, self.vel)
            self.jump = False
            self.entity.inAir = True

    def reset(self):
        self.entity.inAir = False



class goTrait:
    def __init__(self, animation, screen, camera, ent):
        self.animation = animation
        self.direction = 0
        self.heading = 1
        self.accelVel = 0.4
        self.decelVel = 0.25
        self.maxVel = 3.0
        self.screen = screen
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
                self.entity.vel = Vector2D(3.2 * self.heading, self.entity.vel.get_y())
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
                self.animation.inAir()
        else:
            self.animation.update()
            if self.entity.vel.get_x() >= 0:
                self.entity.vel -= Vector2D(self.decelVel, 0)
            else:
                self.entity.vel += Vector2D(self.decelVel, 0)
            if int(self.entity.vel.get_x()) == 0:
                self.entity.vel = Vector2D(0, self.entity.vel.get_y())
                if self.entity.inAir:
                    self.animation.inAir()
                else:
                    self.animation.idle()
        self.drawEntity()

    def drawEntity(self):
        if self.heading == 1:
            self.screen.blit(self.animation.image, self.entity.getPos())
        elif self.heading == -1:
            self.screen.blit(
                flip(self.animation.image, True, False), self.entity.getPos()
            )


class jumpTrait:
    def __init__(self, entity):
        self.vertical_speed = -12 #jump speed
        self.jumpHeight = 120 #jump height in pixels
        self.entity = entity
        self.initalHeight = 384 #stores the position of mario at jump
        self.deaccelerationHeight = self.jumpHeight - ((self.vertical_speed*self.vertical_speed)/(2*self.entity.gravity))

    def jump(self,jumping):
        if jumping:
            if not self.entity.inAir and not self.entity.inJump: #only jump when mario is on ground and not in a jump. redundant check
                SOUND_CONTROLLER.play_sfx(JUMP_SOUND)
                self.entity.vel = Vector2D(self.entity.vel.get_x(), self.vertical_speed)
                self.entity.inAir = True
                self.initalHeight = self.entity.rect.y
                self.entity.inJump = True
                self.entity.obeygravity = False #dont obey gravity in jump so as to reach jump height no matter what the speed

        if self.entity.inJump: #check vertical distance travelled while mario is in a jump
            if (self.initalHeight-self.entity.rect.y) >= self.deaccelerationHeight or self.entity.vel.get_y() == 0:
                self.entity.inJump = False
                self.entity.obeygravity = True #mario obeys gravity again and continues normal play

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
