import inputimeout as it
import threading as th
import tkinter as tk
import copy as cp

from RoverInfo import RoverInfo, Vector

MACOS = 0

FPS = 60

WIDTH = 78
HEIGHT = 51

if MACOS:
    SCALE = 8
    TEXT_SIZE = 20
else:
    SCALE = 32
    TEXT_SIZE = 10


class RoverCam(tk.Tk):
    def __init__(self):
        super().__init__()

        self.protocol("WM_DELETE_WINDOW", self.close)

        self.geometry(str(WIDTH * SCALE) + 'x' + str(HEIGHT * SCALE))
        self.minsize(width=WIDTH * SCALE, height=HEIGHT * SCALE)
        self.resizable(False, False)

        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.connection = Connection()
        self.roverInfo = RoverInfo()

        self.draw_ui()

        self.connection.start()

    def close(self):
        self.connection.stop()
        self.destroy()

    def draw_ui(self):
        self.canvas.delete('all')
        self.roverInfo = self.connection.get_rover_info()

        for line in self.roverInfo.pixy:
            self.canvas.create_line(
                line.x0 * SCALE,
                line.y0 * SCALE,
                line.x1 * SCALE,
                line.y1 * SCALE,
                fill='grey', width=1
            )

            text = str(self.roverInfo.pixy.index(line) + 1)
            if line.flags is not None:
                text += ' α=' + str(line.flags)
            self.canvas.create_text(
                (line.x0 + line.x1) / 2 * SCALE, (line.y0 + line.y1) / 2 * SCALE, fill='black',
                font=('American Typewriter', TEXT_SIZE,), text=text
            )

        if self.roverInfo.line_left is not None:
            self.canvas.create_line(
                self.roverInfo.line_left.x0 * SCALE,
                self.roverInfo.line_left.y0 * SCALE,
                self.roverInfo.line_left.x1 * SCALE,
                self.roverInfo.line_left.y1 * SCALE,
                fill='green', width=3
            )

        if self.roverInfo.line_right is not None:
            self.canvas.create_line(
                self.roverInfo.line_right.x0 * SCALE,
                self.roverInfo.line_right.y0 * SCALE,
                self.roverInfo.line_right.x1 * SCALE,
                self.roverInfo.line_right.y1 * SCALE,
                fill='red', width=3
            )

        if self.roverInfo.center_line is not None:
            self.canvas.create_line(
                self.roverInfo.center_line.x0 * SCALE,
                self.roverInfo.center_line.y0 * SCALE,
                self.roverInfo.center_line.x1 * SCALE,
                self.roverInfo.center_line.y1 * SCALE,
                fill='orange', width=3
            )

        self.canvas.create_text(
            10, 20, text='speed: ' + str("{:+.2f}".format(self.roverInfo.speed)),
            fill='blue', anchor='w', font=('Courier New', TEXT_SIZE, 'bold')
        )
        self.canvas.create_text(
            10, 40, text='steer: ' + str("{:+.2f}".format(self.roverInfo.steer)),
            fill='blue', anchor='w', font=('Courier New', TEXT_SIZE, 'bold')
        )

        if self.roverInfo.distance == 0:
            colour = 'gray'
        elif self.roverInfo.distance < 1:
            colour = 'red'
        else:
            colour = 'blue'

        self.canvas.create_text(
            10, 100, text='distance: ' + str("{:.2f}".format(self.roverInfo.distance)),
            fill=colour, anchor='w', font=('Courier New', TEXT_SIZE, 'bold')
        )

        if self.roverInfo.braking:
            colour = 'red'
        else:
            colour = 'grey'

        self.canvas.create_text(
            WIDTH * SCALE - 20, 10, text='BRAKE',
            fill=colour, anchor='ne', font=('Courier New', TEXT_SIZE * 3, 'bold')
        )

        if self.roverInfo.info is not None:
            self.canvas.create_text(
                20, HEIGHT * SCALE - 20, text=self.roverInfo.info,
                fill="black", anchor='sw', font=('Courier New', TEXT_SIZE, 'bold')
            )

        if not self.connection.connected.is_set():
            self.canvas.create_text(
                WIDTH * SCALE / 2, HEIGHT * SCALE / 4,
                text='NO CONNECTION!', fill='red', font=('Times New Roman', 30)
            )

        self.after(1000 // FPS, self.draw_ui)


class Connection(th.Thread):
    def __init__(self):
        super().__init__()
        self.lock = th.Lock()
        self.event = th.Event()

        self.connected = th.Event()

        self.roverInfo = RoverInfo()

    def get_rover_info(self):
        self.lock.acquire()
        rover_into = cp.deepcopy(self.roverInfo)
        self.lock.release()
        return rover_into

    def set_rover_info(self, rover_info):
        self.lock.acquire()
        self.roverInfo = cp.deepcopy(rover_info)
        self.lock.release()

    def stop(self):
        self.event.set()
        self.join()

    def run(self):
        while True:
            if self.event.is_set():
                break

            try:
                rover_info = RoverInfo()
                while True:
                    if self.event.is_set():
                        break

                    try:
                        input_string = it.inputimeout(timeout=1).strip()
                        values = input_string.split(' ')

                        self.connected.set()

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
                                    rover_info.line_left = Vector(
                                        int(points[0]), int(points[1]), int(points[2]), int(points[3])
                                    )

                                    points = values[2].split('/')
                                    rover_info.line_right = Vector(
                                        int(points[0]), int(points[1]), int(points[2]), int(points[3])
                                    )

                                except IndexError:
                                    pass

                            case 'm':
                                rover_info.center_line = None

                                try:
                                    points = values[1].split('/')
                                    rover_info.center_line = Vector(
                                        int(points[0]), int(points[1]), int(points[2]), int(points[3])
                                    )
                                except IndexError:
                                    pass

                            case 'p':
                                rover_info.pixy = []

                                if len(values) > 1:
                                    for line in values[1:]:
                                        points = line.split('/')

                                        rover_info.pixy.append(
                                            Vector(int(points[0]), int(points[1]), int(points[2]), int(points[3]))
                                        )

                            case 'b':
                                rover_info.braking = False

                                if len(values) > 1:
                                    if values[1] == '1':
                                        rover_info.braking = True

                            case 'l':
                                if len(input_string) > 2:
                                    print(input_string[2:])

                            case 'i':
                                rover_info.info = None

                                if len(input_string) > 2:
                                    rover_info.info = input_string[2:]

                            case 'd':
                                rover_info.distance = float(values[1])

                        self.set_rover_info(rover_info)

                    except ValueError:
                        pass

            except it.TimeoutOccurred:
                self.connected.clear()

            except EOFError:
                self.connected.clear()


rover_cam = RoverCam()

try:
    rover_cam.mainloop()
except KeyboardInterrupt:
    rover_cam.close()
