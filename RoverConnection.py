import threading as th
import time
import queue
import serial as sr
from copy import deepcopy
from RoverInfo import RoverInfo, Line

class RoverConnection(th.Thread):
    def __init__(self, port, baudrate):
        super().__init__()
        self.lock = th.Lock()
        self.event = th.Event()

        self.is_connected = th.Event()

        self.port = port
        self.baudrate = baudrate

        self.roverInfo = RoverInfo()
        self.serial = None
        self._send_queue = queue.Queue()
        self.start()

    def get_rover_info(self):
        with self.lock:
            rover_info = deepcopy(self.roverInfo)

        return rover_info

    def set_rover_info(self, rover_info):
        with self.lock:
            self.roverInfo = deepcopy(rover_info)

    def connected(self):
        return self.is_connected.is_set()

    def send(self, data):
        self._send_queue.put(data)

    def stop(self):
        self.event.set()
        self.join()

    def run(self):
        while not self.event.is_set():
            
            try:
                with sr.Serial(self.port, self.baudrate, timeout=1) as self.serial:

                    self.is_connected.set()
                    rover_info = RoverInfo()

                    while not self.event.is_set():

                        try:
                            while not self.event.is_set():
                                data = self._send_queue.get_nowait()
                                try:
                                    self.serial.write(bytes(data))
                                    try:
                                        self.serial.flush()
                                    except Exception:
                                        pass

                                except sr.SerialException:
                                    self.is_connected.clear()
                                    raise

                                except Exception:
                                    pass

                        except queue.Empty:
                            pass

                        while not self.event.is_set():
                            data = self.serial.readline().decode('utf-8').strip()
                            if not data:
                                break

                            print(data)

                            values = data.split(' ')
                            match values[0]:
                                case 'c':
                                    control = values[1].split('/')
                                    rover_info.speed = float(control[0])
                                    rover_info.steer = float(control[1])

                                case 'v':
                                    rover_info.line_left = None
                                    rover_info.line_right = None

                                    try:
                                        points = values[1].split('/')
                                        rover_info.line_left = Line(
                                            int(points[0]), int(points[1]), int(points[2]), int(points[3])
                                        )

                                        points = values[2].split('/')
                                        rover_info.line_right = Line(
                                            int(points[0]), int(points[1]), int(points[2]), int(points[3])
                                        )

                                    except IndexError:
                                        pass

                                case 'm':
                                    rover_info.center_line = None

                                    try:
                                        points = values[1].split('/')
                                        rover_info.center_line = Line(
                                            int(points[0]), int(points[1]), int(points[2]), int(points[3])
                                        )
                                    except IndexError:
                                        pass

                                case 'p':
                                    rover_info.lines = []

                                    if len(values) > 1:
                                        for line in values[1:]:
                                            points = line.split('/')

                                            rover_info.lines.append(
                                                Line(int(points[0]), int(points[1]), int(points[2]), int(points[3]))
                                            )

                                case 'b':
                                    rover_info.braking = False

                                    if len(values) > 1:
                                        if values[1] == '1':
                                            rover_info.braking = True

                                case 'l':
                                    if len(data) > 2:
                                        print(data[2:])

                                case 'i':
                                    rover_info.variables = None

                                    if len(data) > 2:
                                        rover_info.variables = data[2:]

                                case 'd':
                                    if len(values) > 1:
                                        rover_info.distance = float(values[1])

                            self.set_rover_info(rover_info)
                        
                        time.sleep(0.1)

                    self.is_connected.clear()
                
            except sr.SerialException:
                self.is_connected.clear()

        rover_info = None