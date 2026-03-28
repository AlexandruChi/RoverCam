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
        self._recv_queue = queue.Queue()

        self._error_queue = queue.Queue()

        self.is_connected.clear()

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

    def recv(self):
        try:
            data = self._recv_queue.get_nowait()
            return data
        except queue.Empty:
            return None

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
                                    self.serial.write(data)
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
        
                        data = self.serial.readline()
                        
                        if data == b'\r\n' or data == b'':
                            continue

                        if data:

                            try:
                                data = data.decode('utf-8').strip()

                            except UnicodeDecodeError:
                                self._error_queue.put('rvrcm unicode decode error')
                                continue

                            i = data.find("rvrcm")
                            if i == -1:
                                self._recv_queue.put(data)
                                continue

                            data = data[i:].strip()

                            command = data.split('|')
                            if (len(command) != 3 or command[0] != 'rvrcm'):
                                self._error_queue.put(f'rvrcm format error ({data})')
                                continue

                            match command[1]:
                                case 'gui':

                                    gui_data = command[2]
                                    values = gui_data.split(' ')

                                    if len(values[0]) != 1:
                                        self._error_queue.put(f'rvrcm gui format error ({data})')
                                        continue
                                    
                                    try:
                                        match values[0]:
                                            case 'c':
                                                rover_info.gear = None
                                                rover_info.braking = False
                                                rover_info.speed = 0.0
                                                rover_info.steer = 0.0
                                                rover_info.state = 0

                                                if len(values) > 2:
                                                    self._error_queue.put(f'rvrcm gui control [c] format error ({data})')
                                                    continue

                                                try:
                                                    control = values[1].split('/')

                                                    if len(control) != 5:
                                                        self._error_queue.put(f'rvrcm gui control [c] format error ({data})')
                                                        continue

                                                    rover_info.gear = control[0]
                                                    rover_info.state = int(control[1])
                                                    rover_info.braking = control[2] == '1'
                                                    rover_info.speed = float(control[3])
                                                    rover_info.steer = float(control[4])

                                                except IndexError:
                                                    pass

                                                except ValueError:
                                                    self._error_queue.put(f'rvrcm gui control [c] value error ({data})')
                                                    continue

                                            case 'l':
                                                rover_info.line_left = None
                                                rover_info.line_right = None

                                                if len(values) > 3:
                                                    self._error_queue.put(f'rvrcm gui lines [l] format error ({data})')
                                                    continue

                                                try:
                                                    points = values[1].split('/')

                                                    if len(points) != 4:
                                                        self._error_queue.put(f'rvrcm gui lines [l] format error ({data})')
                                                        continue

                                                    rover_info.line_left = Line(
                                                        int(points[0]), int(points[1]), int(points[2]), int(points[3])
                                                    )

                                                    points = values[2].split('/')

                                                    if len(points) != 4:
                                                        self._error_queue.put(f'rvrcm gui lines [l] format error ({data})')
                                                        continue

                                                    rover_info.line_right = Line(
                                                        int(points[0]), int(points[1]), int(points[2]), int(points[3])
                                                    )

                                                except IndexError:
                                                    pass

                                                except ValueError:
                                                    self._error_queue.put(f'rvrcm gui lines [l] value error ({data})')
                                                    continue

                                            case 'm':
                                                rover_info.center_line = None

                                                if len(values) > 2:
                                                    self._error_queue.put(f'rvrcm gui path [m] format error ({data})')
                                                    continue

                                                try:
                                                    points = values[1].split('/')

                                                    if len(points) != 4:
                                                        self._error_queue.put(f'rvrcm gui path [m] format error ({data})')
                                                        continue

                                                    rover_info.center_line = Line(
                                                        int(points[0]), int(points[1]), int(points[2]), int(points[3])
                                                    )
                                                
                                                except IndexError:
                                                    pass

                                                except ValueError:
                                                    self._error_queue.put(f'rvrcm gui path [m] value error ({data})')
                                                    continue

                                            case 'p':
                                                rover_info.lines = []

                                                try:
                                                    if len(values) > 1:
                                                        for line in values[1:]:
                                                            points = line.split('/')

                                                            if len(points) != 4:
                                                                self._error_queue.put(f'rvrcm gui pixy [p] format error ({data})')
                                                                continue

                                                            rover_info.lines.append(
                                                                Line(int(points[0]), int(points[1]), int(points[2]), int(points[3]))
                                                            )
                                                
                                                except ValueError:
                                                    self._error_queue.put(f'rvrcm gui pixy [p] value error ({data})')
                                                    continue

                                            case 'd':
                                                rover_info.distance = 0.0

                                                if len(values) > 2:
                                                    self._error_queue.put(f'rvrcm gui distance [d] format error ({data})')
                                                    continue

                                                try:        
                                                    rover_info.distance = float(values[1])

                                                except IndexError:
                                                    pass

                                                except ValueError:
                                                    self._error_queue.put(f'rvrcm gui distance [d] value error ({data})')
                                                    continue

                                            case 'b':
                                                rover_info.battery = False
                                                rover_info.battery_warning = 0
                                                rover_info.voltage = 0.0
                                                rover_info.amps = 0.0
                                                rover_info.battery_remaining = 0.0
                                                rover_info.run_time_left = 0

                                                if len(values) > 2:
                                                    self._error_queue.put(f'rvrcm gui battery [b] format error ({data})')
                                                    continue

                                                try:
                                                    battery = values[1].split('/')

                                                    if len(battery) != 6:
                                                        self._error_queue.put(f'rvrcm gui battery [b] format error ({data})')
                                                        continue

                                                    rover_info.battery = battery[0] == '1'
                                                    rover_info.battery_warning = int(battery[1])
                                                    rover_info.voltage = float(battery[2])
                                                    rover_info.amps = float(battery[3])
                                                    rover_info.battery_remaining = float(battery[4])
                                                    rover_info.run_time_left = int(battery[5])

                                                except IndexError:
                                                    pass

                                                except ValueError:
                                                    self._error_queue.put(f'rvrcm gui battery [b] value error ({data})')
                                                    continue

                                            case 't':
                                                rover_info.text = None

                                                if len(gui_data) >= 2:
                                                    rover_info.text = gui_data[2:]

                                        self.set_rover_info(rover_info)
                                    
                                    except ValueError:
                                        self._error_queue.put(f'rvrcm value error ({data})')
                                        continue

                                case 'cli':
                                    print(command[2])

                                case 'var':
                                    pass
                            
                        print(self._error_queue.get_nowait()) if not self._error_queue.empty() else None
                        print(self._recv_queue.get_nowait()) if not self._recv_queue.empty() else None

                        # time.sleep(0.01)

                    self.is_connected.clear()
                
            except sr.SerialException:
                self.is_connected.clear()

        rover_info = None