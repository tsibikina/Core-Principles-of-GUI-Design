from PyQt6.QtCore import QObject, pyqtSignal

class CommonSignals(QObject):
    clear_all = pyqtSignal()
    rates_updated = pyqtSignal(dict)

common_signals = CommonSignals()