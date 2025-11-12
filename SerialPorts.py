import tkinter as tk
import tkinter.ttk as ttk
import serial.tools.list_ports

class SerialPorts(tk.Tk):
    def __init__(self, title='Serial Ports', on_select=None, on_close=None, **kw):
        super().__init__(**kw)

        self.on_close = on_close
        self.placeholder = "Select port ..."

        frame = ttk.Frame(self, padding=(7, 7, 7, 7))
        frame.pack(fill='both', expand=True)

        self.title(title)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind("<Destroy>", lambda e: self.on_close() if e.widget == self and self.on_close else None)

        self.baud = None
        self.port = tk.StringVar()
        self.baudEntry = tk.StringVar()
        self.baudEntry.trace_add("write", self.validate)
        self.combobox = ttk.Combobox(frame, textvariable=self.port)
        self.combobox.grid(row=1, column=0, columnspan=2)
        self.combobox.bind("<FocusIn>", lambda e: self.port.set('') if self.port.get() == self.placeholder else None)
        self.combobox.bind("<FocusOut>", lambda e: self.port.set(self.placeholder) if self.port.get() == '' else None)
        self.refresh()

        self.baudrate_select = ttk.Frame(frame)
        ttk.Label(self.baudrate_select, text='baudrate').grid(row=0, column=0)
        self.baudrate_entry = ttk.Entry(self.baudrate_select, textvariable=self.baudEntry)
        self.baudrate_entry.grid(row=0, column=1)
        self.baudrate_select.grid(row=2, column=0, columnspan=2)

        self.refresh_button = ttk.Button(frame, text='Refresh', command=self.refresh)
        self.refresh_button.grid(row=3, column=0)
        ttk.Button(frame, text='Select', command=lambda: on_select(
            self.port.get() if self.port.get() != self.placeholder else None, self.baud
        ) if on_select is not None else None).grid(row=3, column=1)

        for widget in frame.winfo_children():
            widget.grid_configure(sticky="nsew")

    def refresh(self):
        self.baud = 115200
        self.port.set(self.placeholder)
        self.baudEntry.set(str(self.baud))
        self.combobox['values'] = self.get_ports()

    def get_ports(self):
        return [port.device for port in serial.tools.list_ports.comports()]

    def validate(self, *args):
        try:
            self.baud = int(self.baudEntry.get()) if self.baudEntry.get() != '' else None
        except ValueError:
            self.baudEntry.set(str(self.baud) if self.baud is not None else '')

    def lock(self):
        self.combobox.config(state='disabled')
        self.baudrate_entry.config(state='disabled')
        self.refresh_button.config(state='disabled')

    def unlock(self):
        self.combobox.config(state='normal')
        self.baudrate_entry.config(state='normal')
        self.refresh_button.config(state='normal')

    def close(self):
        self.on_close() if self.on_close else None
        self.destroy()

