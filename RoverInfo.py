class Line:
    def __init__(self, x0, y0, x1, y1, flags=None):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.flags = flags

class RoverInfo:
    def __init__(
            self, line_left=None, line_right=None, center_line=None,
            speed: float = 0, steer: float = 0, braking: bool = False,
            lines=None, variables=None, distance: float = 0, gear: int = 0
    ):
        self.lines = [] if lines is None else list(lines)
        self.line_left = line_left
        self.line_right = line_right
        self.center_line = center_line

        self.speed = speed
        self.steer = steer

        self.braking = braking
        self.distance = distance
        self.gear = gear

        self.variables = 'variables'
