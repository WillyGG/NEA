from GUI import Window
import tkinter as tk
from Comparison_Tool import Comparison_Tool

class CT_GUI():
    def __init__(self):
        self.ct = Comparison_Tool()
        self.Init_Win = Init_Win(self)
        #self.isolated_comp = Iso_Win(self.ct, self,
                                     #parent=tk.Toplevel(self.Init_Win.parent))

    # starts the app
    def run(self):
        self.Init_Win.run()

    # hides the main menu and runs the next window
    def open_win(self, win_to_open):
        self.Init_Win.hide()
        if win_to_open == "iso_comp":
            self.isolated_comp = Iso_Win(self.ct, self, parent=tk.Toplevel(self.Init_Win.parent))
            self.isolated_comp.run()
        elif win_to_open == "rel_comp":
            pass # implement this!!

    def close_win(self, win_to_close):
        self.Init_Win.show()
        if win_to_close == "iso_comp":
            self.isolated_comp.destroy()
        elif win_to_close == "rel_comp":
            pass

# main menu class - window with buttons to traverse the gui
class Init_Win(Window):
    def __init__(self, parent=None, geometry="400x400"):
        self.ID = "Main_Menu"
        self.ct = Comparison_Tool()
        super().__init__(tk.Tk(), geometry)

    def build_widgets(self, fr):
        self.title = tk.Label(fr, text="Comparison Tool")
        self.title.grid(row=0, column=0)

        self.iso_comp_btn = tk.Button(fr, text="Isolated Comparison",
                                      command=lambda: self.open_win("iso_comp"))
        self.iso_comp_btn.grid(row=1, column=0)

        self.rel_comp_btn = tk.Button(fr, text="Relational Comparison",
                                      command=lambda: self.open_win("rel_comp"))
        self.rel_comp_btn.grid(row=2, column=0)

    # hides the main menu and runs the next window
    def open_win(self, win_to_open):
        self.hide()
        if win_to_open == "iso_comp":
            self.isolated_comp = Iso_Win(ct=self.ct, root=self, parent=tk.Toplevel())
        elif win_to_open == "rel_comp":
            self.rel_comp = Rel_Win(ct=self.ct, root=self, parent=tk.Toplevel())

# isolated user comparison
# enter user name and get data about them, in isolation
# todo turn this and the other window
class Iso_Win(Window):
    def __init__(self, ct, root, parent, geometry="400x400"):
        super().__init__(parent, geometry)
        self.ID = "iso_comp"
        self.ct = ct
        self.root = root
        self.default_text = True

    def build_widgets(self, fr):
        self.title = tk.Label(fr, text="Isolated Comparison")
        self.title.grid(row=0, column=0)

        self.un_entry = tk.Entry(fr)
        self.un_entry.insert(0, "Enter Username here")
        self.un_entry.bind("<Button-1>", self.clear_default)
        self.un_entry.grid(row=1, column=0)

        self.build_wr = tk.Button(fr, text="Output Winrates",
                                  command=lambda: self.wr_command(self.un_entry.get()))
        self.build_wr.grid(row=2, column=0)

        self.back_btn = tk.Button(fr, text="Back", command=self.back)
        self.back_btn.grid(row=3, column=0)

        self.res_label = tk.Label(fr, text="")
        self.res_label.grid(row=5,column=0)

    def wr_command(self, id):
        valid_id = self.ct.db_wrapper.check_valid_id(id)
        if not valid_id:
            self.res_label.config(text="User not Found")
            return False
        self.res_label.config(text="User Found")
        self.ct.output_player_wr(id)

    def clear_default(self, *args):
        if self.default_text:
            self.default_text = False
            self.un_entry.delete(0, "end")

    def back(self):
        self.root.show()
        self.destroy()

class Rel_Win(Window):
    def __init__(self, ct, root, parent, geometry="400x400"):
        super().__init__(parent, geometry)
        self.ID = "rel_comp"
        self.ct = ct
        self.root = root

        self.default_text_1 = True
        self.default_text_2 = True

    def build_widgets(self, fr):
        self.title = tk.Label(fr, text="Relational Comparison")
        self.title.grid(row=0, column=0)

        self.un1_entry = tk.Entry(fr)
        self.un1_entry.insert(0, "Enter Username 1 here")
        self.un1_entry.bind("<Button-1>", lambda *args: self.clear_default(1))
        self.un1_entry.grid(row=1, column=0)

        self.un2_entry = tk.Entry(fr)
        self.un2_entry.insert(0, "Enter Username 2 here")
        self.un2_entry.bind("<Button-1>", lambda *args: self.clear_default(2))
        self.un2_entry.grid(row=2, column=0)

        self.realtions_btn = tk.Button(fr, text="Relations") # implement the command for this
        self.realtions_btn.grid(row=3, column=0)

        self.back_btn = tk.Button(fr, text="Back", command=self.back)
        self.back_btn.grid(row=4, column=0)

        self.res_label = tk.Label(fr, text="")
        self.res_label.grid(row=5, column=0)

    def clear_default(self, entry_id, *args):
        if entry_id == 1 and self.default_text_1:
            self.default_text_1 = False
            self.un1_entry.delete(0, "end")
        elif entry_id == 2 and self.default_text_2:
            self.default_text_2 = False
            self.un2_entry.delete(0, "end")

    def back(self):
        self.root.show()
        self.destroy()

if __name__ == "__main__":
    g = Init_Win()
    g.run()