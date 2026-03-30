import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

class RoverControl(tk.Toplevel):
    def __init__(self, master=None, title='Rover Control', send=None, connected=None, on_close=None, **kw):
        super().__init__(master, **kw)

        self.send_func = send
        self.connected = connected
        self.on_close = on_close

        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind("<Destroy>", lambda e: self.on_close() if e.widget == self and self.on_close else None)

        self.title(title)
        self.resizable(False, False)

        frame = ttk.Frame(self, padding=(10, 10, 10, 10))
        frame.pack(fill='both', expand=True)

        self.manual_mode = tk.BooleanVar(value=False)
        self.manual_checkbox = ttk.Checkbutton(
            frame, 
            text="Manual Control", 
            variable=self.manual_mode
        )
        self.manual_checkbox.pack(pady=10)

        # --- Define your specific commands here ---
        self.press_cmds = {
            'w': b'rover_pos_control mode L\r\n',
            's': b'rover_pos_control mode R\r\n',
            'a': b'rover_pos_control steer L\r\n',
            'd': b'rover_pos_control steer R\r\n',
            'space': b'rover_pos_control mode B\r\n'
        }
        
        self.release_cmds = {
            'w': b'rover_pos_control mode N\r\n',
            's': b'rover_pos_control mode N\r\n',
            'a': b'rover_pos_control steer C\r\n',
            'd': b'rover_pos_control steer C\r\n',
            'space': b'rover_pos_control mode N\r\n'
        }

        self.keys_held = set()
        self.active_ad = None
        self.active_ws = None

        self.bind("<KeyPress>", self.key_press)
        self.bind("<KeyRelease>", self.key_release)

    def key_press(self, event):
        if not self.manual_mode.get():
            return

        key = event.keysym.lower()
        if key not in ('w', 'a', 's', 'd', 'space'):
            return

        if key in self.keys_held:
            return
        self.keys_held.add(key)

        if key in ('a', 'd'):
            self.active_ad = key
            self.send(self.press_cmds[key])
            
        elif key in ('w', 's', 'space'):
            self.active_ws = key
            self.send(self.press_cmds[key])

    def key_release(self, event):
        if not self.manual_mode.get():
            return

        key = event.keysym.lower()
        if key not in ('w', 'a', 's', 'd', 'space'):
            return

        if key in self.keys_held:
            self.keys_held.remove(key)

        if key in ('a', 'd'):
            if self.active_ad == key:
                self.send(self.release_cmds[key])
                self.active_ad = None
                
        elif key in ('w', 's', 'space'):
            if self.active_ws == key:
                self.send(self.release_cmds[key])
                self.active_ws = None

    def send(self, command):
        if self.send_func is None:
            messagebox.showwarning('Warning', "Can't send commands")
            return
        
        if not (self.connected() if self.connected else False):
            messagebox.showwarning('Warning', 'Not connected')
            return
        
        self.send_func(command)

    def close(self):
        if self.on_close:
            self.on_close()
        self.destroy()