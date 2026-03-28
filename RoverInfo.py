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
            speed: float = 0.0, steer: float = 0.0, braking: bool = False,
            lines=None, text=None, distance: float = 0.0, gear = None, 
            battery: bool = False, battery_warning: int = 0, voltage: float = 0.0,
            amps: float = 0.0, battery_remaining: float = 0.0, run_time_left: int = 0,
            state: int = 0
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
        self.state = state

        self.text = text

        self.battery = battery
        self.battery_warning = battery_warning
        self.voltage = voltage
        self.amps = amps
        self.battery_remaining = battery_remaining
        self.run_time_left = run_time_left
