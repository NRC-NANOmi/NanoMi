"""
Contains functionality that was shared between softwares when developed.
It has now been copied into each project.
"""

from tkinter import ttk
import tkinter as tk
import threading
import traceback


class AsyncHandler:
    """
    A handler spins off another theread and returns immediately.
    Used with sliders and other GUI components to prevent laggy behaviour.
    """

    def __init__(self, handler):
        """Wraps a handler and returns an asynchronous handler."""
        self.handler = handler
        # there will be only one async thread being executed at any given time
        self.thread = None
        # indicates whether a call to handler is currently queued/delayed
        self.delay = False
        # these variables will store arguments in-case a call to the handler
        # must be delayed
        self.next_args = None
        self.next_kwargs = None
        # a lock that prevents any weird edge cases
        # the handler is the only thing not executed in it
        self.mutex = threading.Lock()

    def __call__(self, *args, **kwargs):
        """
        Calls the async handler which either spins off a thread,
        or delays the call if one is already running.
        """
        with self.mutex:
            if self.thread is None:
                self.thread = threading.Thread(
                    target=self.async_thread, args=args, kwargs=kwargs)
                self.thread.start()
            else:
                self.delay = True
                self.next_args = args
                self.next_kwargs = kwargs

    def async_thread(self, *args, **kwargs):
        """The main method to be run by the thread."""
        # this will loop until there are no more delayed calls to make
        while self.thread is not None:
            try:
                self.handler(*args, **kwargs)
            except Exception as e:
                print(traceback.format_exc())
                print(e)
            finally:
                with self.mutex:
                    if self.delay:
                        self.delay = False
                        args = self.next_args
                        kwargs = self.next_kwargs
                    else:
                        # no delayed calls, get out of here
                        self.thread = None


class ScaleSpinboxLink:
    """A link between a slider and a spinbox."""

    def __init__(self, scale, spinbox, value, value_range):
        """Creates a link between an existing slider and spinbox."""
        self.command = None
        self.decimals = 2
        self.scale = scale
        self.spinbox = spinbox
        scale.set(value)
        self.to_spinbox = lambda x: x
        self.from_spinbox = lambda x: x
        self.spinbox_var = tk.StringVar()
        self.trace_id = self.spinbox_var.trace(
            'w', lambda a, b, c: self.handle_spinbox()
        )
        self.scale.configure(
            from_=value_range[0],
            to=value_range[1],
            command=self.handle_scale
        )
        self.spinbox.configure(
            from_=value_range[0],
            to=value_range[1],
            textvariable=self.spinbox_var
        )
        self.spinbox.set(value)

    def set_command(self, command):
        """Sets the command to be called when updated."""
        self.command = command

    def set_disabled(self, is_disabled):
        """Enables or disables (greys out) the slider and spinbox."""
        if is_disabled:
            self.scale.config(state="disabled")
            self.spinbox.config(state="disabled")
        else:
            self.scale.config(state="normal")
            self.spinbox.config(state="normal")

    def get(self):
        """Returns value represeneted by the link."""
        return self.scale.get()

    def set(self, value):
        """Sets the value of the link."""
        value = float(value)
        self.scale.set(value)
        self.update_spinbox(value)

    def update_spinbox(self, value):
        """Updated the value of the spinbox independent from the slider."""
        if self.to_spinbox is not None:
            value = self.to_spinbox(value)
        rounded_value = round(value, self.decimals)
        self.spinbox.set(rounded_value)

    def handle_scale(self, value):
        """Called when the slider is moved."""
        value = float(value)
        self.update_spinbox(value)
        if self.command is not None:
            self.command(value)

    def handle_spinbox(self):
        """Called when the spinbox is updated."""
        try:
            spinbox_value = self.from_spinbox(float(self.spinbox_var.get()))
            self.scale.set(spinbox_value)
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
        self.update_spinbox(self.scale.get())
        self.decimals = decimals
        self.spinbox.configure(
            from_=spinbox_range[0],
            to=spinbox_range[1]
        )


class NumericSpinbox(ttk.Spinbox):
    """A spinbox with a validated numeric range and type."""

    def __init__(
        self, master, value_default=0, value_range=[0, 100], value_type=int,
        command=None, **kwargs
    ):
        """Creates a numeric spinbox."""
        super().__init__(
            master, from_=value_range[0], to=value_range[1], **kwargs
        )
        self.value_type = value_type
        self.value_range = value_range
        self.value_default = value_default
        self.value_cached = None
        self.command = command
        validate_command = (master.register(self.validate), '%P')
        invalid_command = (master.register(self.on_invalid),)
        self.config(validate="focusout", validatecommand=validate_command)
        self.config(invalidcommand=invalid_command, command=self.on_change)
        self.set(value_default)

    def get(self):
        """Returns the numeric value of the spinbox."""
        return self.value_type(super().get())

    def set(self, value):
        """Sets the numeric value of the spinbox."""
        self.value_cached = value
        super().set(value)

    def set_command(self, command):
        """Sets the command to be called when the spinbox in updated."""
        self.command = command

    def set_value_range(self, minimum, maxmimum):
        """Updates the range of values allowed in the spinbox."""
        self.config(from_=minimum, to=maxmimum)
        self.value_range = (minimum, maxmimum)
        if not self.validate(self.value_cached):
            self.on_invalid()

    def on_change(self):
        """
        Runs on any value change.
        Calls validate, but does not call on_invalid to correct value.
        """
        self.validate(self.get())

    def validate(self, value):
        """
        Returns validaty of the spinbox.
        Calls the command if the value is updated and it is valid.
        """
        try:
            value = self.value_type(value)
            if self.value_range is not None:
                if value < self.value_range[0]:
                    valid = False
                if value > self.value_range[1]:
                    valid = False
            valid = True
        except Exception:
            valid = False
        if valid and self.value_cached != value:
            self.value_cached = value
            if self.command is not None:
                self.command()
        return valid

    def on_invalid(self):
        """Updates the value to a previous valid value when invalid."""
        if self.value_cached is not None:
            self.set(self.value_cached)
        else:
            self.set(self.value_default)
