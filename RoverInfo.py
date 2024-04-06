class Vector:
    def __init__(self, x0, y0, x1, y1, flags=None):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.flags = flags


class Intersection:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class RoverInfo:
    def __init__(
            self, line_left: Vector = None, line_right: Vector = None,
            speed: float = 0, steer: float = 0, breaking: bool = False,
            pixy=None
    ):
        if pixy is None:
            pixy = []
        self.pixy = pixy
        self.line_left = line_left
        self.line_right = line_right
        self.speed = speed
        self.steer = steer
        self.breaking = breaking
