import tkinter as tk
from tkinter import ttk
from .widget_templates import SliderLayout, RadioLayout, ToggleButton
from .common import ScaleSpinboxLink

PAD_Y = 5


# widgetsfor the settings below the sample
class BelowSampleFrame(tk.LabelFrame):
    """frame to create optimization settings and lens settings for
    below lenses. optimization settings selects image mode and lens
    to optimize. lens setting adjust focal length and on/off.
    """

    def __init__(self, master):
        """init frame and creates widgets

        Args:
            master (tk.Window): master window
        """
        super().__init__(master, text="Settings below sample")
        self.columnconfigure(1, weight=1)

        # stores the values of the sliders
        self.slider_values = [10, 19.670, 6.498, 6]

        # stores the status of the lenses on/off
        self.lens_status = [True, True, True]

        # radio buttons for image mode
        self.opt_sel = tk.StringVar()
        opt_options = ["Diffraction", "Image"]
        self.opt_sel.set(opt_options[1])
        self.opt_mode_buttons = RadioLayout(
            self, "Image Mode", opt_options, self.opt_sel, False
        )
        self.opt_mode_buttons.grid(row=0, column=0)

        # radio buttons for auto setting
        self.lens_sel = tk.IntVar()
        auto_options = [
            "Objective", "Intermediate", "Projective", "None"
        ]
        self.lens_sel.set(-1)
        auto_mode_buttons = RadioLayout(
            self, "Auto Setting", auto_options, self.lens_sel, True
        )
        auto_mode_buttons.grid(row=0, column=1, columnspan=2, sticky="w")

        # label for sliders
        sliders_label = ttk.Label(self, text="Lens settings (nm):")
        sliders_label.grid(row=1, column=0, sticky="we")

        # Distance slider
        self.distance_slider = SliderLayout(self, "Distance:")
        self.distance_link = ScaleSpinboxLink(
            self.distance_slider.slider,
            self.distance_slider.entry,
            self.slider_values[0], (0.1, 100)
        )
        self.distance_slider.grid(row=2, column=0, columnspan=2, sticky="nwse")

        # Initialize arrays for sliders, links, and buttons
        self.sliders = []
        self.links = []
        self.buttons = []
        labels = [
            "Objective:", "Intermediate:", "Projective:"
        ]

        for i, label in enumerate(labels):
            # Objective slider and button
            self.sliders.append(SliderLayout(self, label))
            self.links.append(
                ScaleSpinboxLink(
                    self.sliders[i].slider,
                    self.sliders[i].entry,
                    self.slider_values[i + 1], (6, 300)
                )
            )
            self.sliders[i].grid(
                row=i + 3, column=0, columnspan=2, sticky="nwse"
            )
            self.buttons.append(ToggleButton(self))
            self.buttons[i].grid(row=i + 3, column=2)
