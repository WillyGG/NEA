"""
    - abstract parent class for gui
    - allows
"""

import tkinter as tk
from abc import ABC, abstractmethod

class Window(ABC):
    def __init__(self, parent=None, geometry="400x400"):
        self.parent = parent
        if parent is None:
            self.parent = tk.Tk()
        self.parent.geometry(geometry)
        self.body = tk.Frame(self.parent)
        self.body.grid()

        self.build_widgets(self.body)

    @abstractmethod
    def build_widgets(self, fr):
        pass

    def run(self):
        self.parent.mainloop()
