"""Application state shared by independent bridge controllers."""
from PyQt5.QtCore import QObject, pyqtSignal


class BridgeRuntime(QObject):
    pause_changed = pyqtSignal(bool)
    notification = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.paused = False
        self.closing = False

    def is_paused(self):
        return self.paused

    def set_paused(self, value):
        value = bool(value)
        if value != self.paused:
            self.paused = value
            self.pause_changed.emit(value)
