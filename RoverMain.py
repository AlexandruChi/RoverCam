from tkinter import messagebox
from RoverConnection import RoverConnection
from SerialPorts import SerialPorts
from RoverCam import RoverCam
from RoverCommand import RoverCommand
import sys
import signal

if False:
    # Custom window size
    SCALE = 30
    TEXT_SIZE = 20
elif sys.platform == 'darwin':
    # 14 inch MacBook Pro
    SCALE = 15
    TEXT_SIZE = 20
else:
    SCALE = 20
    TEXT_SIZE = 10

    # 900p screen linux default
    # SCALE = 15
    # TEXT_SIZE = 10

connection = None
window = None
command = None

commands = {
    'drive R': b'rover_pos_control mode R\r\n',
    'drive N': b'rover_pos_control mode N\r\n',
    'drive D': b'rover_pos_control mode D\r\n',
    'drive L': b'rover_pos_control mode L\r\n',
    'drive B': b'rover_pos_control mode B\r\n',
    '':'\r\n',
    'steer A': b'rover_pos_control steer A\r\n',
    'steer C': b'rover_pos_control steer C\r\n',
    'steer L': b'rover_pos_control steer L\r\n',
    'steer R': b'rover_pos_control steer R\r\n',
    '':'\r\n',
    'reboot': b'reboot\r\n'
}

# Call window.close() on Ctrl + C
signal.signal(signal.SIGINT, lambda s, f: window.after(0, window.close) if window is not None else None)

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

    camera = RoverCam(master=window, scale=SCALE, text_size=TEXT_SIZE, recv=connection.get_rover_info, connected=connection.connected, on_close=on_close)
    command = RoverCommand(master=camera, commands=commands, send=connection.send, connected=connection.connected)


window = SerialPorts(title='Rover Serial Ports', on_select=on_select, on_close=lambda: globals().update({'window': None}))
window.createcommand('tk::mac::Quit', window.close)

window.mainloop()
