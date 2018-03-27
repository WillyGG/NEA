from GUI import Window
import tkinter as tk
from Comparison_Tool import Comparison_Tool

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

        self.gen_stat_btn = tk.Button(fr, text="General Statistics",
                                      command=lambda: self.open_win("gen_stat"))
        self.gen_stat_btn.grid(row=3, column=0)

        self.data_win_btn = tk.Button(fr, text="Gen Data",
                              command=lambda: self.open_win("get_data"))
        self.data_win_btn.grid(row=4, column=0)

    # hides the main menu and runs the next window
    def open_win(self, win_to_open):
        self.hide()
        if win_to_open == "iso_comp":
            self.isolated_comp = Iso_Win(ct=self.ct, root=self, parent=tk.Toplevel())
        elif win_to_open == "rel_comp":
            self.rel_comp = Rel_Win(ct=self.ct, root=self, parent=tk.Toplevel())
        elif win_to_open == "gen_stat":
            self.gen_stat = Gen_Win(ct=self.ct, root=self, parent=tk.Toplevel())
        elif win_to_open == "get_data":
            self.data_win = Data_Win(ct=self.ct, root=self, parent=tk.Toplevel())

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

class Gen_Win(Window):
    def __init__(self, ct, root, parent, geometry="400x400"):
        super().__init__(parent, geometry)
        self.ID = "gen_stat"
        self.ct = ct
        self.root = root

    def build_widgets(self, fr):
        self.title = tk.Label(fr, text="General Stats")
        self.title.grid(row=0, column=0)

        self.stand_dist_btn = tk.Button(fr, text="Stand Value Distribution",
                                        command=lambda: self.display_dist_cmd("stand_dist"))
        self.stand_dist_btn.grid(row=1, column=0)

        self.hit_dist_btn = tk.Button(fr, text="Hit Value Distribution",
                                      command=lambda: self.display_dist_cmd("hit_dist"))
        self.hit_dist_btn.grid(row=2, column=0)

        self.stand_vs_wr_btn = tk.Button(fr, text="Win Rate Against Stand Value",
                                         command=lambda: self.display_dist_cmd("stand_win"))
        self.stand_vs_wr_btn.grid(row=3, column=0)

        self.hit_vs_bust_btn = tk.Button(fr, text="Bust Rate Against Hit Value",
                                         command=lambda: self.display_dist_cmd("hit_bust"))
        self.hit_vs_bust_btn.grid(row=4, column=0)

        self.back_btn = tk.Button(fr, text="Back", command=self.back)
        self.back_btn.grid(row=5, column=0)

    def display_dist_cmd(self, dist_type):
        if dist_type == "hit_dist":
            self.ct.output_hit_dist()
        elif dist_type == "stand_dist":
            self.ct.output_stand_dist()
        elif dist_type == "stand_win":
            self.ct.output_stand_vs_wr()
        elif dist_type == "hit_bust":
            self.ct.output_hit_vs_br()

    def back(self):
        self.root.show()
        self.destroy()

class Data_Win(Window):
    def __init__(self, ct, root, parent, geometry="400x400"):
        super().__init__(parent, geometry)
        self.ID = "get_data"
        self.ct = ct
        self.root = root

        self.default_text = True

    def build_widgets(self, fr):
        self.title_lbl = tk.Label(fr, text="Get Data")
        self.title_lbl.grid(row=0, column=0)

        self.no_games_ent = tk.Entry(fr)
        self.no_games_ent.insert(0, "Enter num of games to play here")
        self.no_games_ent.bind("<Button-1>", self.clear_default)
        self.no_games_ent.grid(row=1, column=0)

        self.instr_lbl = tk.Label(fr, text="Tick the AI you want to use in your sample")
        self.instr_lbl.grid(row=2, column=0)

        self.nn_var = tk.IntVar()
        self.nn_check = tk.Checkbutton(fr, text="nn", variable=self.nn_var)
        self.nn_check.grid(row=3, column=0)

        self.cc_ai_var = tk.IntVar()
        self.cc_ai_check = tk.Checkbutton(fr, text="cc ai", variable=self.cc_ai_var)
        self.cc_ai_check.grid(row=4, column=0)

        self.simple_var = tk.IntVar()
        self.simple_check = tk.Checkbutton(fr, text="simple", variable=self.simple_var)
        self.simple_check.grid(row=5, column=0)

        self.rand_var = tk.IntVar()
        self.rand_check = tk.Checkbutton(fr, text="rand ai", variable=self.rand_var)
        self.rand_check.grid(row=6, column=0)

        self.begin_btn = tk.Button(fr, text="Begin", command=self.begin_sample)
        self.begin_btn.grid(row=7, column=0)

        self.back_btn = tk.Button(fr, text="Back", command=self.back)
        self.back_btn.grid(row=8, column=0)

        self.res_lbl = tk.Label(fr, text="")
        self.res_lbl.grid(row=9, column=0)

    def begin_sample(self):
        agents_playing = []
        checkboxes = [self.nn_var, self.cc_ai_var, self.simple_var, self.rand_var]
        names = [self.ct.ID_NN, self.ct.ID_CC_AI, self.ct.ID_SIMPLE, self.ct.ID_RAND_AI]

        # check checkbox state, if checked append to list of agent ids who are playing
        for i in range(len(checkboxes)):
            cbox_state = checkboxes[i].get()
            name = names[i]
            if cbox_state:
                agents_playing.append(name)
        if agents_playing == []:
            self.res_lbl.config(text="Please select at least one ai to play")
            return False

        no_games = self.no_games_ent.get()
        try:
            no_games = int(no_games)
        except:
            self.res_lbl.config(text="Please enter a valid number of games")
            return False

        self.res_lbl.config(text="Commencing testing for {0} games".format(str(no_games)))
        self.ct.get_data(agents_playing, no_games=no_games)
        self.res_lbl.config(text="Data gathered and pushed")
        return True

    def clear_default(self, *args):
        if self.default_text:
            self.default_text = False
            self.no_games_ent.delete(0, "end")

    def back(self):
        self.root.show()
        self.destroy()

if __name__ == "__main__":
    g = Init_Win()
    #g.run()
    g.ct.update_nn()