from PyQt5.QtWidgets import QLabel, QGroupBox, QGridLayout
from PyQt5.QtCore import Qt
from .widget_templates import TableLayout
from nanomi_optics.engine.lens_excitation import ur_asymmetric, ur_symmetric


class ResultsFrame(QGroupBox):
    def __init__(self, f_upper, f_lower, mag_upper, mag_lower, aper, mag, parent=None):
        super().__init__('Results', parent)
        self.layout = QGridLayout(self)

        self.ur = [
            ur_symmetric(f_upper[0]),
            ur_asymmetric(f_upper[1]),
            ur_asymmetric(f_upper[2])
        ]
        self.upper_units = ["", "mm", "x"]
        upper_data = [
            ("", "C1", "C2", "C3"),
            ("Lens Ur: ", *self.ur),
            ("Lens Focal length:", *f_upper),
            ("Lens Magnification:", *mag_upper)
        ]
        self.upper_results = TableLayout(upper_data, self.upper_units)
        self.layout.addWidget(self.upper_results, 0, 0, Qt.AlignRight)

        self.lower_units = ["mm", "x"]
        lower_data = [
            ("", "Objective", "Intermediate", "Projective"),
            ("Lens Focal Length: ", *f_lower),
            ("Lens Magnification:", *mag_lower)
        ]
        self.lower_results = TableLayout(lower_data, self.lower_units)
        self.layout.addWidget(self.lower_results, 0, 2, Qt.AlignLeft)

        aperature = aper * 1e3
        self.condensor = QLabel(f"Condensor Aperature = {aperature:.2f} nm")
        self.layout.addWidget(self.condensor, 1, 0, Qt.AlignRight)

        self.magnification = QLabel(f"Magnification = {mag:.2f} x")
        self.layout.addWidget(self.magnification, 1, 2, Qt.AlignLeft)

    def update_results(self, f_upper, f_lower, mag_upper, mag_lower, aper, mag):
        self.ur = [
            ur_symmetric(f_upper[0]),
            ur_asymmetric(f_upper[1]),
            ur_asymmetric(f_upper[2])
        ]
        self.upper_results.update_table(self.upper_units, self.ur, f_upper, mag_upper)
        self.lower_results.update_table(self.lower_units, f_lower, mag_lower)
        aperature = aper * 1e3
        self.condensor.setText(f"Condensor Aperature = {aperature:.2f} nm")
        self.magnification.setText(f"Magnification = {mag:.2f} x")
