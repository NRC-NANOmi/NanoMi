from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QSlider, QCheckBox, QDoubleSpinBox, QRadioButton, QGroupBox, QButtonGroup
from PyQt5.QtCore import Qt


class BelowSampleFrame(QFrame):
    """frame to create optimization settings and lens settings for
    below lenses. optimization settings selects image mode and lens
    to optimize. lens setting adjust focal length and on/off.
    """
    def __init__(self, parent=None):
        """init frame and creates widgets

        Args:
            parent (QWidget): parent widget
        """
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        # stores the values of the sliders
        self.slider_values = [10, 19.670, 6.498, 6]

        # stores the status of the lenses on/off
        self.lens_status = [True, True, True]

        # radio buttons for image mode
        self.opt_mode_buttons = QButtonGroup(self)
        opt_options = ["Diffraction", "Image"]
        opt_group = QGroupBox("Image Mode", self)
        opt_layout = QVBoxLayout(opt_group)
        for i, option in enumerate(opt_options):
            btn = QRadioButton(option, opt_group)
            btn.setChecked(i == 1)
            self.opt_mode_buttons.addButton(btn, i)
            opt_layout.addWidget(btn)
        self.layout.addWidget(opt_group)

        # radio buttons for auto setting
        self.auto_mode_buttons = QButtonGroup(self)
        auto_options = ["Objective", "Intermediate", "Projective", "None"]
        auto_group = QGroupBox("Auto Setting", self)
        auto_layout = QVBoxLayout(auto_group)
        for i, option in enumerate(auto_options):
            btn = QRadioButton(option, auto_group)
            self.auto_mode_buttons.addButton(btn, i)
            auto_layout.addWidget(btn)
        self.layout.addWidget(auto_group)

        # label for sliders
        sliders_label = QLabel("Lens settings (nm):", self)
        self.layout.addWidget(sliders_label)

        # Distance slider
        self.distance_slider = QSlider(Qt.Horizontal, self)
        self.distance_slider.setValue(self.slider_values[0])
        self.distance_slider.setRange(1, 1000)  # QSlider uses integers
        self.distance_slider.valueChanged.connect(self.on_distance_slider_changed)
        self.layout.addWidget(QLabel("Distance:", self))
        self.layout.addWidget(self.distance_slider)

        self.distance_spinbox = QDoubleSpinBox(self)
        self.distance_spinbox.setRange(0.1, 100)
        self.distance_spinbox.setValue(self.slider_values[0])
        self.distance_spinbox.valueChanged.connect(self.distance_slider.setValue)
        self.layout.addWidget(self.distance_spinbox)

        # Initialize arrays for sliders, spinboxes, checkboxes, and labels
        self.sliders = []
        self.spinboxes = []
        self.checkboxes = []
        labels = ["Objective:", "Intermediate:", "Projective:"]

        for i, label in enumerate(labels):
            # Slider
            slider = QSlider(Qt.Horizontal, self)
            slider.setValue(self.slider_values[i + 1])
            slider.setRange(6, 300)
            slider.valueChanged.connect(self.on_slider_changed)

            spinbox = QDoubleSpinBox(self)
            spinbox.setRange(6, 300)
            spinbox.setValue(self.slider_values[i + 1])
            spinbox.valueChanged.connect(slider.setValue)

            checkbox = QCheckBox("Toggle", self)

            self.sliders.append(slider)
            self.spinboxes.append(spinbox)
            self.checkboxes.append(checkbox)

            self.layout.addWidget(QLabel(label, self))
            self.layout.addWidget(slider)
            self.layout.addWidget(spinbox)
            self.layout.addWidget(checkbox)

    def on_distance_slider_changed(self, value):
        self.distance_spinbox.setValue(value / 10)

    def on_slider_changed(self, value):
        for spinbox, slider in zip(self.spinboxes, self.sliders):
            if slider == self.sender():
                spinbox.setValue(value)
                break
