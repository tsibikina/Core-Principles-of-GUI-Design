import sys
import json
import base64
import os
from datetime import datetime

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, pyqtProperty, QAbstractListModel, Qt, QModelIndex
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine

# --- Модель для отображения истории сохранений в QML ---
class SaveHistoryModel(QAbstractListModel):
    TimestampRole = Qt.UserRole + 1
    ImageDataRole = Qt.UserRole + 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self._saves = []

    def data(self, index, role=Qt.DisplayRole):
        if 0 <= index.row() < len(self._saves):
            save = self._saves[index.row()]
            if role == SaveHistoryModel.TimestampRole:
                return save["timestamp"]
            if role == SaveHistoryModel.ImageDataRole:
                return save["imageData"]
        return None

    def rowCount(self, parent=QModelIndex()):
        return len(self._saves)

    def roleNames(self):
        return {
            SaveHistoryModel.TimestampRole: b"timestamp",
            SaveHistoryModel.ImageDataRole: b"imageData",
        }

    def add_save(self, timestamp, image_data):
        self.beginInsertRows(QModelIndex(), 0, 0)
        self._saves.insert(0, {"timestamp": timestamp, "imageData": image_data})
        self.endInsertRows()

    def get_save(self, index):
        if 0 <= index < len(self._saves):
            return self._saves[index]
        return None

    def clear(self):
        self.beginResetModel()
        self._saves = []
        self.endResetModel()

# --- Основной класс-контроллер ---
class DrawingBackend(QObject):
    imageDataLoaded = pyqtSignal(str)
    saveStatusChanged = pyqtSignal(str) # Сигнал для отображения статуса в UI

    def __init__(self):
        super().__init__()
        self._history_model = SaveHistoryModel()
        self._save_file_path = "C:/Users/USER/PycharmProjects/image/saves.json"
        self._autosave_png_path = "C:/Users/USER/PycharmProjects/image/autosave_backup.png"
        self._load_history()

    @pyqtProperty(QAbstractListModel, constant=True)
    def historyModel(self):
        return self._history_model

    @pyqtSlot(str)
    def saveCanvas(self, image_data_url):
        """Ручное сохранение в историю (saves.json)."""
        try:
            header, encoded = image_data_url.split(",", 1)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._history_model.add_save(timestamp, encoded)
            self._save_history_to_file()
            self.saveStatusChanged.emit(f"Сохранено в историю: {timestamp}")
        except (ValueError, IndexError) as e:
            print(f"Ошибка при декодировании данных изображения: {e}")
            self.saveStatusChanged.emit(f"Ошибка сохранения: {e}")

    @pyqtSlot(str)
    def autoSaveToPng(self, image_data_url):
        """Автосохранение в один PNG-файл."""
        try:
            header, encoded = image_data_url.split(",", 1)
            image_data = base64.b64decode(encoded)
            with open(self._autosave_png_path, "wb") as f:
                f.write(image_data)
            # Можно убрать вывод в консоль, чтобы не засорять
            # print(f"Автосохранение в {self._autosave_png_path} выполнено.")
        except (ValueError, IndexError, IOError) as e:
            print(f"Ошибка при автосохранении в PNG: {e}")

    @pyqtSlot(int)
    def setAutoSaveInterval(self, interval_seconds):
        """Этот метод теперь управляет только таймером в QML."""
        if interval_seconds > 0:
            print(f"Автосохранение в историю включено с интервалом {interval_seconds} сек.")
        else:
            print("Автосохранение в историю выключено.")

    @pyqtSlot(int)
    def loadSave(self, index):
        """Загружает выбранное сохранение из истории."""
        save_data = self._history_model.get_save(index)
        if save_data:
            self.imageDataLoaded.emit(f"data:image/png;base64,{save_data['imageData']}")

    def _load_history(self):
        if os.path.exists(self._save_file_path):
            try:
                with open(self._save_file_path, 'r') as f:
                    data = json.load(f)
                    self._history_model.clear()
                    for item in reversed(data):
                        self._history_model.add_save(item['timestamp'], item['imageData'])
                print("История сохранений из saves.json загружена.")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Ошибка при чтении файла истории: {e}")

    def _save_history_to_file(self):
        data_to_save = self._history_model._saves[:50]
        try:
            with open(self._save_file_path, 'w') as f:
                json.dump(data_to_save, f, indent=2)
        except IOError as e:
            print(f"Ошибка при записи в файл истории: {e}")


if __name__ == "__main__":
    sys.argv += ['--style', 'material']
    app = QGuiApplication(sys.argv)

    engine = QQmlApplicationEngine()
    backend = DrawingBackend()
    engine.rootContext().setContextProperty("drawingBackend", backend)

    engine.load(os.path.join(os.path.dirname(__file__), "mainWindow.qml"))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())