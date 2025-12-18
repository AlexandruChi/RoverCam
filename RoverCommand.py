import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

class RoverCommand(tk.Toplevel):
    def __init__(self, master=None, title='Rover Command', commands=None, send=None, connected=None, on_close=None, **kw):
        super().__init__(master, **kw)

        self.commands = commands if commands is not None else {}
        self.send_func = send
        self.connected = connected
        self.on_close = on_close

        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind("<Destroy>", lambda e: self.on_close() if e.widget == self and self.on_close else None)

        self.title(title)
        self.resizable(False, False)

        frame = ttk.Frame(self, padding=(10, 10, 10, 10))
        frame.pack(fill='both', expand=True)

        if not self.commands:
            ttk.Label(frame, text='No commands').pack()
        else:
            for name, command in self.commands.items():
                ttk.Button(frame, text=name, command=lambda cmd=command: self.send(cmd)).pack(fill='x')

        self.custom = tk.StringVar()
        self.textbox = ttk.Entry(self, textvariable=self.custom).pack(fill='x')
        self.sendButton = ttk.Button(self, text="send", command=lambda: self.send(self.custom.get().encode() + b'\r\n') if len(self.custom.get()) > 0 else None).pack(fill='x')

    def send(self, command):
        if self.send_func is None:
            messagebox.showwarning('Warning', "Can't send commands")
            return
        
        if not self.connected() if self.connected else False:
            messagebox.showwarning('Warning', 'Not connected')
            return
        
        self.send_func(command)

    def required(self):
        return bool(self.commands)

    def close(self):
        if self.on_close:
            self.on_close()
            
        elif self.required():
            messagebox.showwarning('Warning', 'Window required')
            return
        
        self.destroy()
