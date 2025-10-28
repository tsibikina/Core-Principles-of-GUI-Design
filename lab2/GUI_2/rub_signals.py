from PyQt6.QtCore import QObject, pyqtSignal

class RUBSignals(QObject):
    rub_changed = pyqtSignal(str)

rub_signals = RUBSignals()