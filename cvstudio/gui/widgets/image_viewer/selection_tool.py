from enum import Enum, auto


class SELECTION_TOOL(Enum):
    POLYGON = auto()
    BOX = auto()
    ELLIPSE = auto()
    FREE = auto()
    POINTER = auto()
    EXTREME_POINTS = auto()
