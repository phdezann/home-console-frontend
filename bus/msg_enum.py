from enum import Enum, auto


class MsgEnum(Enum):
    SHOW_MESSAGE = auto()
    CLEAR_SCREEN = auto()
    #
    SENSOR_TOUCHED = auto()
