from tkinter import messagebox
from RoverConnection import RoverConnection
from SerialPorts import SerialPorts
from RoverCam import RoverCam
from RoverCommand import RoverCommand

connection = None
window = None

def on_select(port, baud):
    global connection
    global window

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

        if connection is not None:
            connection.stop()
            connection = None

        window.unlock() if window is not None else None

    camera = RoverCam(master=window, scale=15, text_size=20, recv=connection.get_rover_info, connected=connection.connected, on_close=on_close)
    command = RoverCommand(master=camera, commands=None, send=None, connected=connection.connected)


window = SerialPorts(title='Rover Serial Ports', on_select=on_select)
window.mainloop()
