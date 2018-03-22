from GUI import Window
import tkinter as tk
from Comparison_Tool import Comparison_Tool

class CT_GUI():
    def __init__(self):
        self.ct = Comparison_Tool()
        self.init_win = Init_Window(self.ct)

    def run(self):
        self.init_win.run()


class Init_Window(Window):
    def __init__(self, ct, parent=None, geometry="400x400"):
        super().__init__(parent, geometry)
        self.ct = ct

    def build_widgets(self, fr):
        self.title = tk.Label(fr, text="Comparison Tool")
        self.title.grid(row=0, column=0)

        self.un_entry = tk.Entry(fr)
        self.un_entry.grid(row=1, column=0)

        self.build_wr = tk.Button(fr, text="Output Winrates",
                                  command=lambda: self.wr_command(self.un_entry.get()))
        self.build_wr.grid(row=2, column=0)

    def wr_command(self, id):
        valid_id = self.ct.db_wrapper.check_valid_id(id)
        if not valid_id:
            print("nay")
            return False
        self.ct.output_player_wr(id)

if __name__ == "__main__":
    g = CT_GUI()
    g.run()