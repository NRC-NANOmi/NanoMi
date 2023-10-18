from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QSlider, QCheckBox, QDoubleSpinBox, QComboBox
from PyQt5.QtCore import Qt
from nanomi_optics.engine.lens_excitation import (
    ur_symmetric, ur_asymmetric, cf_symmetric, cf_asymmetric
)


class AboveSampleFrame(QFrame):
    """frame to create modes and lens settings for upper lenses.
    lens setting adjust focal length and on/off.
    """
    def __init__(self, parent=None):
        """init frame and creates widgets

        Args:
            parent (QWidget): parent widget
        """
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.mode_widget = QComboBox(self)
        self.layout.addWidget(self.mode_widget)

        # label for sliders
        sliders_label = QLabel("Lens settings (mm):", self)
        self.layout.addWidget(sliders_label)

        # stores the values of the lenses
        self.focal_values = [67.29, 22.94, 39.88]

        self.lens_type = [True, False, False]

        # stores the status of the lenses on/off
        self.lens_status = [True, True, True]

        self.sliders = []
        self.spinboxs = []
        self.checkboxes = []
        self.slider_text = [
            "Lens C1: ", "Lens C2: ", "Lens C3: "
        ]

        for i, txt in enumerate(self.slider_text):
            slider = QSlider(Qt.Horizontal, self)
            slider.setValue(self.focal_values[i])
            slider.setRange(6, 300)
            slider.valueChanged.connect(self.set_mode)

            spinbox = QDoubleSpinBox(self)
            spinbox.setRange(6, 300)
            spinbox.setValue(self.focal_values[i])
            spinbox.valueChanged.connect(slider.setValue)

            slider.valueChanged.connect(spinbox.setValue)

            checkbox = QCheckBox(txt, self)
            checkbox.setChecked(self.lens_status[i])

            self.sliders.append(slider)
            self.spinboxs.append(spinbox)
            self.checkboxes.append(checkbox)

            self.layout.addWidget(checkbox)
            self.layout.addWidget(slider)
            self.layout.addWidget(spinbox)

    def set_mode(self, mode):
        """set modes and translate from focal length to lens activation

        Args:
            mode (bool): identify the mode selected by user
        """
        if mode:
            for spinbox in self.spinboxs:
                spinbox.setRange(6, 300)
                spinbox.setDecimals(2)
        else:
            for i, spinbox in enumerate(self.spinboxs):
                if self.lens_type[i]:
                    spinbox.setRange(0, 2)
                    spinbox.setDecimals(4)
                else:
                    spinbox.setRange(0, 2)
                    spinbox.setDecimals(4)
