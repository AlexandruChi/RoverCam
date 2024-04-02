import socket as sk
import threading as th
import tkinter as tk

from RoverInfo import RoverInfo, Vector

SIMULATOR = 1

FPS = 30

IP = '127.0.0.1'
PORT = 10001

WIDTH = 78
HEIGHT = 51

SCALE = 8


class RoverCam(tk.Tk):
    def __init__(self):
        super().__init__()
        self.connected = False

        self.geometry(str(WIDTH * SCALE) + 'x' + str(HEIGHT * SCALE))
        self.minsize(width=WIDTH * SCALE, height=HEIGHT * SCALE)
        self.resizable(False, False)

        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.connection = Connection(self.start_callback, self.stop_callback, self.draw_callback)
        self.roverInfo = RoverInfo()

        self.draw_ui()

        self.connection.start()

    def draw_ui(self):
        self.canvas.delete('all')

        for line in self.roverInfo.pixy:
            self.canvas.create_line(
                line.x0 * SCALE,
                line.y0 * SCALE,
                line.x1 * SCALE,
                line.y1 * SCALE,
                fill='grey', width=1
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

        if not self.connected:
            self.canvas.create_text(
                WIDTH * SCALE / 2, HEIGHT * SCALE / 4,
                text='NO CONNECTION!', fill='red', font=('Charter', 30)
            )

        self.canvas.create_text(
            10, 20, text='speed: ' + str("{:+.2f}".format(self.roverInfo.speed)), fill='blue', anchor='w', font=('Courier New', 20)
        )
        self.canvas.create_text(
            10, 40, text='steer: ' + str("{:+.2f}".format(self.roverInfo.steer)), fill='blue', anchor='w', font=('Courier New', 20)
        )

        self.after(1000 // FPS, self.draw_ui)

    def start_callback(self):
        self.connected = True
        self.draw_ui()

    def stop_callback(self):
        self.connected = False
        self.draw_ui()

    def draw_callback(self):
        self.roverInfo = self.connection.get_rover_info()


class Connection(th.Thread):
    def __init__(self, start_callback, stop_callback, draw_callback):
        super().__init__()
        self.lock = th.Lock()

        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.draw_callback = draw_callback

        self.socketfd = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        self.socketfd.bind((IP, PORT))
        self.socketfd.listen(0)

        self.roverInfo = RoverInfo()

    def get_rover_info(self):
        self.lock.acquire()
        rover_into = self.roverInfo
        self.lock.release()
        return rover_into

    def run(self):
        while True:
            clientfd, _ = self.socketfd.accept()
            self.start_callback()
            while True:
                data = clientfd.recv(4096)

                if not data:
                    break

                rover_info = RoverInfo()
                lines = data.decode('ascii').split('\n')
                for line in lines:
                    if line is not None:
                        line_data = line.split(' ')
                        if len(line_data) == 2:
                            if line_data[0] == 'speed':
                                rover_info.speed = float(line_data[1])
                            elif line_data[0] == 'steer':
                                rover_info.steer = float(line_data[1])
                        elif len(line_data) == 6:
                            if line_data[0] == 'v1':
                                if line_data[1] == '1' and len(line_data) == 6:
                                    rover_info.line_left = Vector(
                                        int(line_data[2]), int(line_data[3]), int(line_data[4]), int(line_data[5])
                                    )
                                else:
                                    rover_info.line_left = None
                            elif line_data[0] == 'v2':
                                if line_data[1] == '1' and len(line_data) == 6:
                                    rover_info.line_right = Vector(
                                        int(line_data[2]), int(line_data[3]), int(line_data[4]), int(line_data[5])
                                    )
                                else:
                                    rover_info.line_right = None
                        elif len(line_data) == 5 and line_data[0] == 'px':
                            rover_info.pixy.append(Vector(
                                int(line_data[1]), int(line_data[2]), int(line_data[3]), int(line_data[4])
                            ))

                self.lock.acquire()
                self.roverInfo = rover_info
                self.lock.release()

                self.draw_callback()

            self.stop_callback()


RoverCam().mainloop()
