# contains templates for widgets that will be used in other classes
import tkinter as tk
from tkinter import ttk

PAD_X = 5
CELL_WIDTH = 18
LABEL_WIDTH = 12


# makes a standard drop down menu widget
# (upper sensors)
class DropDownWidget(ttk.Frame):

    def __init__(self, master):
        super().__init__(master)
        label = ttk.Label(self, text="Mode: ")
        label.pack(side='left')

        modes = ('Cf', 'Ur')
        self.option_var = tk.StringVar(self)
        self.option_var.set(modes[0])
        self.option_menu = tk.OptionMenu(self, self.option_var, *modes)
        self.option_menu.pack(side='left')


# makes a standard slider layout with: label, slider, box, and toggle
# (upper + lower sensors)
class SliderLayout(ttk.Frame):

    def __init__(self, master, name):
        super().__init__(master)

        self.columnconfigure(1, weight=1)

        # creates label
        sx_label = ttk.Label(self, text=name, width=LABEL_WIDTH, anchor="e")
        sx_label.grid(column=0, row=0, sticky="w", padx=PAD_X)

        # creates slider
        self.slider = ttk.Scale(self, orient='horizontal')
        self.slider.grid(column=1, row=0, padx=PAD_X, sticky="nwse")
        self.columnconfigure(1, weight=1)
        # creates entry box
        self.entry = ttk.Spinbox(self, width=6)
        self.entry.grid(column=2, row=0, padx=PAD_X)


# button for toggling the sliders on/off
class ToggleButton(tk.Button):

    def __init__(self, master, **kwargs):
        super().__init__(master, text="ON", **kwargs)
        self.config(command=self.click)
        self.status = True

    # set a command when user clicks
    def set_command(self, command):
        self.command = command

    # change the status, text when user clicks, add command params
    def click(self):
        if self.status:
            self.status = False
            self.config(text="OFF")
        else:
            self.status = True
            self.config(text="ON")
        if self.command is not None:
            self.command(self.status)

    # returns current status
    def get_status(self):
        return self.status


# radio button widgets layout - located inside its own labelframe
# (lower sensors)
class RadioLayout(tk.LabelFrame):

    def __init__(self, master, name, radio_names, var, int_val):
        super().__init__(master, text=name)
        # takes a list of names for radio widgets and puts them next
        # to each other inside of the label frame
        self.options = []
        for i, name in enumerate(radio_names):
            if int_val:
                self.options.append(
                    tk.Radiobutton(
                        self, text=name,
                        value=i if name != "None" else -1, variable=var
                    )
                )
            else:
                self.options.append(
                    tk.Radiobutton(self, text=name, value=name, variable=var)
                )

            self.options[i].pack(side="left", anchor="nw", padx=10)


# table layout created using Labels and Text
# (results)
class TableLayout(ttk.Frame):

    def __init__(self, master, data_list, units):
        super().__init__(master, borderwidth=5)
        self.table_data = []
        # takes in list and makes table
        for i, row in enumerate(data_list):
            self.table_data.append([])
            for j, value in enumerate(row):
                if i == 0 or j == 0:
                    self.table_data[i].append(
                        tk.Label(
                            self, text=value,
                            width=CELL_WIDTH
                        )
                    )
                    self.table_data[i][j].grid(row=i, column=j, sticky="w")
                else:
                    txt = f"{value:.4f} {units[i-1]}"
                    self.table_data[i].append(
                        tk.Label(
                            self, text=txt, width=CELL_WIDTH,
                            bd=1, relief="ridge"
                        )
                    )
                    self.table_data[i][j].grid(row=i, column=j, sticky="nwse")

    def update_table(self, unit, *args):
        for i, row in enumerate(args):
            for j in range(len(row)):
                self.table_data[i + 1][j + 1]["text"] = \
                    f"{row[j]:.4f} {unit[i]}"
