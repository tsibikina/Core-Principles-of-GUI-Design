from PyQt6.QtCore import QObject, pyqtSignal

class USDSignals(QObject):
    usd_changed = pyqtSignal(str)

usd_signals = USDSignals()