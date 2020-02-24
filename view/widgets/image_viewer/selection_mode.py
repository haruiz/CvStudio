from enum import Enum,auto


class SELECTION_MODE(Enum):
    POLYGON=auto()
    BOX=auto()
    ELLIPSE = auto()
    FREE=auto()
    NONE=auto()
    EXTREME_POINTS = auto()