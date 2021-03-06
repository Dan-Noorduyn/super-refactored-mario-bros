from pygame import mixer


class _Sound_Controller():
    def __init__(self):
        self.__music_ch: mixer.Channel = mixer.Channel(0)
        self.__music_ch.set_volume(0.1)
        self.__sfx_ch: mixer.Channel = mixer.Channel(1)
        self.__sfx_ch.set_volume(0.1)
        self.__sfx_muted: bool = False
        self.__music_muted: bool = False

    def play_sfx(self, sfx: mixer.Sound) -> None:
        if not self.sfx_muted():
            self.__sfx_ch.play(sfx)

    def stop_sfx(self) -> None:
        self.__sfx_ch.stop()

    def mute_sfx(self) -> None:
        self.stop_sfx()
        self.__sfx_muted = True

    def unmute_sfx(self) -> None:
        self.__sfx_muted = False

    def sfx_muted(self) -> bool:
        return self.__sfx_muted

    def playing_sfx(self) -> bool:
        return self.__sfx_ch.get_busy()

    def play_music(self, music: mixer.Sound) -> None:
        if not self.music_muted():
            self.__music_ch.play(music)

    def stop_music(self) -> None:
        self.__music_ch.stop()

    def mute_music(self) -> None:
        self.stop_music()
        self.__music_muted = True

    def unmute_music(self) -> None:
        self.__music_muted = False

    def music_muted(self) -> bool:
        return self.__music_muted

    def playing_music(self) -> bool:
        return self.__music_ch.get_busy()


mixer.pre_init(44100, -16, 2, 4096)
mixer.init()
SOUND_CONTROLLER = _Sound_Controller()

# DEFAULT SOUNDS
SOUNDTRACK       = mixer.Sound("./resources/sfx/main_theme.ogg")
HURRY_OVERWORLD  = mixer.Sound("./resources/sfx/hurry_overworld.wav")
GAME_OVER        = mixer.Sound("./resources/sfx/game_over.wav")
STAGE_CLEAR      = mixer.Sound("./resources/sfx/stage_clear.wav")
COIN_SOUND       = mixer.Sound("./resources/sfx/coin.ogg")
BUMP_SOUND       = mixer.Sound("./resources/sfx/bump.ogg")
STOMP_SOUND      = mixer.Sound("./resources/sfx/stomp.ogg")
JUMP_SOUND       = mixer.Sound("./resources/sfx/small_jump.ogg")
DEATH_SOUND      = mixer.Sound("./resources/sfx/death.wav")
MUSHROOM_SOUND   = mixer.Sound("./resources/sfx/powerup.ogg")
MUSHROOM_APPEARS = mixer.Sound("./resources/sfx/powerup_appears.ogg")
POWER_DOWN       = mixer.Sound("./resources/sfx/powerdown.wav")
KICK_SOUND       = mixer.Sound("./resources/sfx/kick.ogg")

__all__ = [
    "SOUND_CONTROLLER",
    "SOUNDTRACK",
    "HURRY_OVERWORLD",
    "GAME_OVER",
    "STAGE_CLEAR",
    "COIN_SOUND",
    "BUMP_SOUND",
    "STOMP_SOUND",
    "JUMP_SOUND",
    "DEATH_SOUND",
    "MUSHROOM_SOUND",
    "MUSHROOM_APPEARS",
    "POWER_DOWN",
    "KICK_SOUND"
]
