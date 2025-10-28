from PyQt6.QtCore import QObject, pyqtSignal

class EURSignals(QObject):
    eur_changed = pyqtSignal(str)

eur_signals = EURSignals()