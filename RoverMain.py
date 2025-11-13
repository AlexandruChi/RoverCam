from tkinter import messagebox
from RoverConnection import RoverConnection
from SerialPorts import SerialPorts
from RoverCam import RoverCam
from RoverCommand import RoverCommand
import sys

if False:
    # Custom window size
    SCALE = 30
    TEXT_SIZE = 20
elif sys.platform == 'darwin':
    # 14 inch MacBook Pro
    SCALE = 15
    TEXT_SIZE = 20
else:
    # 900p screen linux default
    SCALE = 15
    TEXT_SIZE = 10

connection = None
window = None
command = None

commands = {
    'START': [b'nxpcup_work start\n',],
    'STOP': [b'nxpcup_work stop\n',],

    'N': [b'nxpcup_work n\n',],
    'D': [b'nxpcup_work d\n',],
    'B': [b'nxpcup_work b\n',],
}

def on_select(port, baud):
    global connection
    global window
    global command

    if connection is not None:
        messagebox.showwarning('Connected', 'Already connected')
        return

    if port is None:
        messagebox.showwarning('No port selected', 'Select a serial port')
        return

    if baud is None:
        messagebox.showwarning('No baudrate entered', 'Enter a baudrate')
        return

    connection = RoverConnection(port, baud)
    window.lock() if window is not None else None

    def on_close():
        global connection
        global window
        global camera
        global command

        camera = None
        command = None

        if connection is not None:
            connection.stop()
            connection = None

        window.unlock() if window is not None else None

    camera = RoverCam(master=window, scale=15, text_size=20, recv=connection.get_rover_info, connected=connection.connected, on_close=on_close)
    command = RoverCommand(master=camera, commands=commands, send=None, connected=connection.connected)


window = SerialPorts(title='Rover Serial Ports', on_select=on_select, on_close=lambda: globals().update({'window': None}))
window.createcommand('tk::mac::Quit', window.close)

window.mainloop()
