from enum import IntEnum
from loguru import logger
from typing import Optional, Any

from command_base import CommandBase, CommandParserBase


class Command(CommandBase):
    SET_TIME = 24
    SET_SYSTEM_COLOR = 36
    SEND_APP_NEWEST_TIME = 38
    LIGHT_CURRENT_LEVEL = 49
    SET_BOX_COLOR = 68
    SET_BOX_MODE = 69
    GET_BOX_MODE = 70
    SET_MUL_BOX_COLOR = 73
    SET_SYSTEM_BRIGHTNESS = 116
    SET_GAME = 160
    SET_SLEEP_COLOR = 173
    SET_USER_GIF = 177

    @classmethod
    def get_name(cls, value: int) -> str:
        try:
            return cls(value).name
        except ValueError:
            return "UNKNOWN"


# when one of the following commands is sent the device doesn't send back a response
without_response = [
    Command.SEND_APP_NEWEST_TIME,
    Command.SET_SLEEP_COLOR,
]


class CommandParser(CommandParserBase):
    @staticmethod
    def parse(cmd_type: int, data: Optional[bytes]) -> Any:
        if cmd_type == Command.SET_BOX_COLOR.value:
            return SetBoxColor.from_data(data)
        elif cmd_type == Command.SET_MUL_BOX_COLOR.value:
            return SetMulBoxColor.from_data(data)
        else:
            name = Command.get_name(cmd_type)
            logger.warning(f"parser for cmd_type {cmd_type} ({name}) not implemented")

        return None

    @staticmethod
    def parse_response(cmd_type: int, data: Optional[bytes]) -> Any:
        if cmd_type == Command.GET_BOX_MODE.value:
            return GetBoxMode.from_data(data)
        else:
            name = Command.get_name(cmd_type)
            logger.warning(f"response parser for cmd_type {cmd_type} ({name}) not implemented")

        return None


class BoxMode(IntEnum):
    ENV = 0
    LIGHT = 1
    HOT = 2
    SPECIAL = 3
    MUSIC = 4
    USER_DEFINE = 5
    WATCH = 6  # is actually score blue/red board
    SCORE = 7  # doesn't work?


class LightMode(IntEnum):
    CLOCK = 0
    TEMPERATURE = 1
    COLOR = 2
    SPECIAL = 3
    SOUND = 4
    USER = 5


class TimeType(IntEnum):
    BIG = 0
    RAINBOW = 1
    BORDER = 2
    ANALOG = 3
    BIG_INV = 4
    ANALOG_ROUND = 5
    SMALL = 6


class ActivatedModes:
    @staticmethod
    def get_default() -> 'ActivatedModes':
        return ActivatedModes(clock=True)

    def __init__(self, **kwargs):
        self.clock = kwargs.get("clock", False)
        self.weather = kwargs.get("weather", False)
        self.temperature = kwargs.get("temperature", False)
        self.date = kwargs.get("date", False)


class GetBoxMode:
    @staticmethod
    def from_data(data: bytes) -> 'GetBoxMode':
        return GetBoxMode(
            mode=data[0],
            temp_type=data[1],
            light_mode=data[2],
            light_r=data[3],
            light_g=data[4],
            light_b=data[5],
            level=data[6],
            music_type=data[7],
            sys_light=data[8],
            time_type=data[9],
            time_r=data[10],
            time_g=data[11],
            time_b=data[12],
            temp_r=data[13],
            temp_g=data[14],
            temp_b=data[15],
            raw=data,
        )

    def __init__(self, **kwargs):
        self.raw = kwargs.get("raw")

        self.mode = kwargs.get("mode")
        self.temp_type = kwargs.get("temp_type")
        self.light_mode = kwargs.get("light_mode")
        self.light_r = kwargs.get("light_r")
        self.light_g = kwargs.get("light_g")
        self.light_b = kwargs.get("light_b")
        self.light_level = kwargs.get("light_level")
        self.music_type = kwargs.get("music_type")
        self.sys_light = kwargs.get("sys_light")
        self.time_type = kwargs.get("time_type")
        self.time_r = kwargs.get("time_r")
        self.time_g = kwargs.get("time_g")
        self.time_b = kwargs.get("time_b")
        self.temp_r = kwargs.get("temp_r")
        self.temp_g = kwargs.get("temp_g")
        self.temp_b = kwargs.get("temp_b")

    def __str__(self):
        return f"GetBoxMode<mode={self.mode} temp_type={self.temp_type} light_mode={self.light_mode} " + \
               f"light_r={self.light_r} light_g={self.light_g} light_b={self.light_b} time_type={self.time_type} " + \
               f"time_r={self.time_r} time_g={self.time_g} time_b={self.time_b} " + \
               f"temp_r={self.temp_r} temp_g={self.temp_g} temp_b={self.temp_b}>"


class SetBoxColor:
    @staticmethod
    def from_data(data: bytes) -> 'SetBoxColor':
        # crap = 00 0a 0a 04 aa 7f 00 f4 01 00
        _ = data[:10]

        palette_len = data[10]
        palette = data[11:11 + 3 * palette_len]
        image = data[11 + 3 * palette_len:]

        return SetBoxColor(
            palette=palette,
            image=image,
            raw=data,
        )

    def __init__(self, **kwargs):
        self.raw = kwargs.get("raw")

        self.palette = kwargs.get("palette")
        self.image = kwargs.get("image")

    def __str__(self):
        return f"SetBoxColor<palette={self.palette} image={self.image}>"


class SetMulBoxColor(SetBoxColor):
    @staticmethod
    def from_data(data: bytes) -> 'SetBoxColor':
        # crap = 2c 01 00 aa a2 00 1b 01 00
        _ = data[:9]
        palette_len = data[9]
        palette = data[10:10 + 3 * palette_len]
        image = data[10 + 3 * palette_len:]

        return SetBoxColor(
            palette=palette,
            image=image,
            raw=data,
        )