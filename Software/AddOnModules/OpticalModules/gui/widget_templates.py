from PyQt5.QtWidgets import QWidget, QSlider, QSpinBox, QPushButton, QRadioButton, QButtonGroup, QLabel, QGroupBox, QGridLayout, QVBoxLayout, QHBoxLayout, QComboBox
from PyQt5.QtCore import Qt

class DropDownWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.label = QLabel("Mode: ")
        self.combo_box = QComboBox()
        self.combo_box.addItems(['Cf', 'Ur'])
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combo_box)

class SliderLayout(QWidget):
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.label = QLabel(name)
        self.slider = QSlider(Qt.Horizontal)
        self.spin_box = QSpinBox()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.spin_box)

class ToggleButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__('ON', parent)
        self.setCheckable(True)
        self.clicked.connect(self.toggle)

    def toggle(self, checked):
        self.setText('ON' if checked else 'OFF')

class RadioLayout(QGroupBox):
    def __init__(self, name, radio_names, parent=None):
        super().__init__(name, parent)
        self.layout = QVBoxLayout(self)
        self.button_group = QButtonGroup(self)
        for i, name in enumerate(radio_names):
            radio_button = QRadioButton(name)
            self.button_group.addButton(radio_button, i)
            self.layout.addWidget(radio_button)

class TableLayout(QGridLayout):
    def __init__(self, data_list, units, parent=None):
        super().__init__(parent)
        self.labels = []
        for i, row in enumerate(data_list):
            row_labels = []
            for j, value in enumerate(row):
                text = f'{value}' if i == 0 or j == 0 else f'{value:.4f} {units[i-1]}'
                label = QLabel(text)
                self.addWidget(label, i, j)
                row_labels.append(label)
            self.labels.append(row_labels)

    def update_table(self, unit, *args):
        for i, row in enumerate(args):
            for j in range(len(row)):
                self.labels[i + 1][j + 1].setText(f'{row[j]:.4f} {unit[i]}')
