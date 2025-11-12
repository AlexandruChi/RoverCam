import tkinter as tk
from RoverInfo import RoverInfo

FPS = 60

WIDTH = 78
HEIGHT = 51

PADDING = 10
BORDER = 3

class RoverCam(tk.Toplevel):
    def __init__(self, master=None, title='Rover Camera', scale=15, text_size=10, recv=None, connected=None, on_close=None, **kw):
        super().__init__(master, **kw)

        self.scale = scale
        self.text_size = text_size
        self.recv = recv
        self.connected = connected
        self.on_close = on_close

        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind("<Destroy>", lambda e: self.on_close() if e.widget == self and self.on_close else None)

        self.title(title)
        self.geometry(str(WIDTH * self.scale + PADDING * 2 + BORDER * 2) + 'x' + str(HEIGHT * self.scale + PADDING * 2 + BORDER * 2))
        self.minsize(width=WIDTH * self.scale, height=HEIGHT * self.scale)
        self.resizable(False, False)

        self.canvas = tk.Canvas(self, bg='white', bd=BORDER, relief='solid', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)

        self.roverInfo = RoverInfo()

        self.draw_ui()

    def close(self):
        self.on_close() if self.on_close else None
        self.destroy()

    def draw_ui(self):
        if not self.winfo_exists():
            return

        self.canvas.delete('all')

        self.roverInfo = self.recv() if self.recv else self.roverInfo

        for line in self.roverInfo.lines:
            self.canvas.create_line(
                line.x0 * self.scale,
                line.y0 * self.scale,
                line.x1 * self.scale,
                line.y1 * self.scale,
                fill='grey', width=1
            )

            text = str(self.roverInfo.lines.index(line) + 1)
            if line.flags is not None:
                text += ' α=' + str(line.flags)
            self.canvas.create_text(
                (line.x0 + line.x1) / 2 * self.scale, (line.y0 + line.y1) / 2 * self.scale, fill='black',
                font=('American Typewriter', self.text_size,), text=text
            )

        if self.roverInfo.line_left is not None:
            self.canvas.create_line(
                self.roverInfo.line_left.x0 * self.scale,
                self.roverInfo.line_left.y0 * self.scale,
                self.roverInfo.line_left.x1 * self.scale,
                self.roverInfo.line_left.y1 * self.scale,
                fill='green', width=3
            )

        if self.roverInfo.line_right is not None:
            self.canvas.create_line(
                self.roverInfo.line_right.x0 * self.scale,
                self.roverInfo.line_right.y0 * self.scale,
                self.roverInfo.line_right.x1 * self.scale,
                self.roverInfo.line_right.y1 * self.scale,
                fill='red', width=3
            )

        if self.roverInfo.center_line is not None:
            self.canvas.create_line(
                self.roverInfo.center_line.x0 * self.scale,
                self.roverInfo.center_line.y0 * self.scale,
                self.roverInfo.center_line.x1 * self.scale,
                self.roverInfo.center_line.y1 * self.scale,
                fill='orange', width=3
            )

        self.canvas.create_text(
            10, 20, text='speed: ' + str("{:+.2f}".format(self.roverInfo.speed)),
            fill='blue', anchor='w', font=('Courier New', self.text_size, 'bold')
        )
        self.canvas.create_text(
            10, 40, text='steer: ' + str("{:+.2f}".format(self.roverInfo.steer)),
            fill='blue', anchor='w', font=('Courier New', self.text_size, 'bold')
        )

        if self.roverInfo.distance == 0:
            colour = 'gray'
        elif self.roverInfo.distance < 1:
            colour = 'red'
        else:
            colour = 'blue'

        self.canvas.create_text(
            10, 100, text='distance: ' + str("{:.2f}".format(self.roverInfo.distance)),
            fill=colour, anchor='w', font=('Courier New', self.text_size, 'bold')
        )

        if self.roverInfo.braking:
            colour = 'red'
        else:
            colour = 'grey'

        self.canvas.create_text(
            WIDTH * self.scale - 15, 10, text='BRAKE',
            fill=colour, anchor='ne', font=('Courier New', self.text_size * 3, 'bold')
        )

        if self.roverInfo.variables is not None:
            self.canvas.create_text(
                20, HEIGHT * self.scale - 20, text=self.roverInfo.variables,
                fill="black", anchor='sw', font=('Courier New', self.text_size, 'bold')
            )

        if not self.connected() if self.connected else False:
            self.canvas.create_text(
                WIDTH * self.scale / 2, HEIGHT * self.scale / 3,
                text='NO CONNECTION!', fill='red', font=('Times New Roman', 70)
            )

        self.after(1000 // FPS, self.draw_ui)
