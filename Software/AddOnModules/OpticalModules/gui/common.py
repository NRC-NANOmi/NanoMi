from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import traceback


class AsyncHandler(QThread):
    """
    AsyncHandler to offload tasks from the main GUI thread.
    """
    finished = pyqtSignal()

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """
        Overloading QThread's run function.
        This will be run in a separate thread when calling self.start().
        """
        try:
            self.func(*self.args, **self.kwargs)
        except Exception as e:
            print(traceback.format_exc())
            print(e)
        finally:
            self.finished.emit()


class ScaleSpinboxLink(QWidget):
    """A link between a slider and a spinbox."""

    def __init__(self, scale, spinbox, value, value_range):
        """Creates a link between an existing slider and spinbox."""
        super().__init__()
        self.command = None
        self.decimals = 2
        self.layout = QHBoxLayout()
        self.scale = QSlider(Qt.Horizontal)
        self.spinbox = QDoubleSpinBox()
        self.layout.addWidget(self.scale)
        self.layout.addStrut(self.spinbox)

        self.scale.valueChanged.connect(self.handle_scale)
        self.spinbox.valueChanged.connect(self.handle_spinbox)

        self.scale.setRange(value_range[0]*100, value_range[1]*100)
        self.scale.setSingleStep(1)
        self.spinbox.setRange(value_range[0], value_range[1])
        self.spinbox.setSingleStep(0.01)
        self.spinbox.setValue(value)

    def handle_scale(self):
        """Called when the slider is moved."""
        self.spinbox.setValue(self.scale.value()/100)

    def handle_spinbox(self):
        """Called when the spinbox is updated."""
        self.scale.setValue(self.spinbox.value()*100)
    
    def getValue(self):
        return self.spinbox.value()
    
    def setValue(self, value):
        self.spinbox.setValue(value)
        
