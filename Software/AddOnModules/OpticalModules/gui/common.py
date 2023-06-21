from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QSlider, QDoubleSpinBox, QWidget
from PyQt5.Qt import Qt
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

    def __init__(self, value, value_range):
        """Creates a link between an existing slider and spinbox."""
        super().__init__()
        self.command = None
        self.decimals = 2
        self.scale = QSlider(Qt.Horizontal, self)
        self.spinbox = QDoubleSpinBox(self)
        self.scale.setValue(value)
        self.to_spinbox = lambda x: x
        self.from_spinbox = lambda x: x
        self.scale.valueChanged.connect(self.handle_scale)
        self.spinbox.valueChanged.connect(self.handle_spinbox)
        self.scale.setRange(value_range[0], value_range[1])
        self.spinbox.setRange(value_range[0], value_range[1])
        self.spinbox.setValue(value)

    @pyqtSlot(int)
    def handle_scale(self, value):
        """Called when the slider is moved."""
        self.update_spinbox(value)
        if self.command is not None:
            self.command(value)

    @pyqtSlot(float)
    def handle_spinbox(self, value):
        """Called when the spinbox is updated."""
        try:
            spinbox_value = self.from_spinbox(value)
            self.scale.setValue(spinbox_value)
        except Exception:
            pass

    def set_spinbox_mapping(
        self, to_spinbox, from_spinbox, decimals, spinbox_range
    ):
        """
        Sets a custom mapping for the value in the spinbox, while keeping
        the underlying slider values the same.
        For example the underlying slider values may be (0, 1).
        But you might want map that onto the range (0, 100).
        Or you may want to use and even more complicated mapping function.
        """
        self.to_spinbox = to_spinbox
        self.from_spinbox = from_spinbox
        self.update_spinbox(self.scale.value())
        self.decimals = decimals
        self.spinbox.setRange(spinbox_range[0], spinbox_range[1])
        

# Remaining implementation of your functions and methods...
