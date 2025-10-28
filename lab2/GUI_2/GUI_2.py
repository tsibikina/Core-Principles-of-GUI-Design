import sys
import requests
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QThread, pyqtSignal

# Импортируем сигналы
from common_signals import common_signals
from usd_signals import usd_signals
from eur_signals import eur_signals
from rub_signals import rub_signals


class ExchangeRateWorker(QThread):
    """Поток для получения курсов валют из API"""
    rates_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.api_url = "https://api.exchangerate-api.com/v4/latest/USD"

    def run(self):
        try:
            response = requests.get(self.api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                rates = {
                    'USD_RUB': data['rates']['RUB'],
                    'EUR_RUB': data['rates']['RUB'] / data['rates']['EUR'],
                    'USD_EUR': data['rates']['EUR']
                }
                self.rates_ready.emit(rates)
            else:
                self.error_occurred.emit(f"Ошибка API: {response.status_code}")
        except Exception as e:
            # Используем запасные курсы при ошибке
            backup_rates = {
                'USD_RUB': 90.0,
                'EUR_RUB': 98.0,
                'USD_EUR': 0.92
            }
            self.rates_ready.emit(backup_rates)
            self.error_occurred.emit(f"Используются запасные курсы: {str(e)}")


class CurrencyConverter:
    def __init__(self):
        self.exchange_rates = {
            'USD_RUB': 90.0,
            'EUR_RUB': 98.0,
            'USD_EUR': 0.92
        }
        self.updating = False

        # Подключаем обработчики сигналов
        self.connect_signals()

        # Запускаем получение актуальных курсов
        self.get_exchange_rates()

    def connect_signals(self):
        """Подключение всех сигналов"""
        rub_signals.rub_changed.connect(self.on_rub_changed)
        usd_signals.usd_changed.connect(self.on_usd_changed)
        eur_signals.eur_changed.connect(self.on_eur_changed)
        common_signals.clear_all.connect(self.clear_all)
        common_signals.rates_updated.connect(self.update_rates)

    def get_exchange_rates(self):
        """Запуск потока для получения курсов валют"""
        self.worker = ExchangeRateWorker()
        self.worker.rates_ready.connect(self.on_rates_ready)
        self.worker.error_occurred.connect(self.on_rates_error)
        self.worker.start()

    def on_rates_ready(self, rates):
        """Обработка полученных курсов"""
        self.exchange_rates = rates
        common_signals.rates_updated.emit(rates)

    def on_rates_error(self, error_message):
        """Обработка ошибки получения курсов"""
        print(f"Ошибка: {error_message}")

    def update_rates(self, rates):
        """Обновление курсов валют"""
        self.exchange_rates = rates

    def clear_all(self):
        """Очистка всех полей"""
        self.updating = True
        # Сигнал будет обработан в UI
        self.updating = False

    def on_rub_changed(self, text):
        """Обработка изменения рублей"""
        if self.updating or not text:
            return

        try:
            rub_value = float(text.replace(',', '.'))
            self.updating = True

            # Конвертация в USD
            usd_value = rub_value / self.exchange_rates['USD_RUB']
            usd_signals.usd_changed.emit(f"{usd_value:.2f}")

            # Конвертация в EUR
            eur_value = rub_value / self.exchange_rates['EUR_RUB']
            eur_signals.eur_changed.emit(f"{eur_value:.2f}")

            self.updating = False
        except ValueError:
            if not self.updating:
                self.updating = True
                usd_signals.usd_changed.emit("")
                eur_signals.eur_changed.emit("")
                self.updating = False

    def on_usd_changed(self, text):
        """Обработка изменения долларов"""
        if self.updating or not text:
            return

        try:
            usd_value = float(text.replace(',', '.'))
            self.updating = True

            # Конвертация в RUB
            rub_value = usd_value * self.exchange_rates['USD_RUB']
            rub_signals.rub_changed.emit(f"{rub_value:.2f}")

            # Конвертация в EUR
            eur_value = usd_value * self.exchange_rates['USD_EUR']
            eur_signals.eur_changed.emit(f"{eur_value:.2f}")

            self.updating = False
        except ValueError:
            if not self.updating:
                self.updating = True
                rub_signals.rub_changed.emit("")
                eur_signals.eur_changed.emit("")
                self.updating = False

    def on_eur_changed(self, text):
        """Обработка изменения евро"""
        if self.updating or not text:
            return

        try:
            eur_value = float(text.replace(',', '.'))
            self.updating = True

            # Конвертация в RUB
            rub_value = eur_value * self.exchange_rates['EUR_RUB']
            rub_signals.rub_changed.emit(f"{rub_value:.2f}")

            # Конвертация в USD
            usd_value = eur_value / self.exchange_rates['USD_EUR']
            usd_signals.usd_changed.emit(f"{usd_value:.2f}")

            self.updating = False
        except ValueError:
            if not self.updating:
                self.updating = True
                rub_signals.rub_changed.emit("")
                usd_signals.usd_changed.emit("")
                self.updating = False


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(498, 367)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Поля ввода
        self.rub_input = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.rub_input.setGeometry(QtCore.QRect(60, 40, 151, 41))
        self.rub_input.setObjectName("rub_input")

        self.usd_input = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.usd_input.setGeometry(QtCore.QRect(60, 120, 151, 41))
        self.usd_input.setObjectName("usd_input")

        self.eur_input = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.eur_input.setGeometry(QtCore.QRect(60, 200, 151, 41))
        self.eur_input.setObjectName("eur_input")

        # Метки
        self.rub_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.rub_label.setGeometry(QtCore.QRect(220, 50, 51, 21))
        self.rub_label.setObjectName("rub_label")

        self.usd_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.usd_label.setGeometry(QtCore.QRect(220, 130, 51, 21))
        self.usd_label.setObjectName("usd_label")

        self.eur_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.eur_label.setGeometry(QtCore.QRect(220, 210, 51, 21))
        self.eur_label.setObjectName("eur_label")

        # Кнопка сброса
        self.clear_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.clear_button.setGeometry(QtCore.QRect(280, 100, 161, 71))
        self.clear_button.setObjectName("clear_button")

        # Информационная метка с курсами
        self.rates_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.rates_label.setGeometry(QtCore.QRect(60, 260, 381, 41))
        self.rates_label.setObjectName("rates_label")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 498, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Флаг для предотвращения рекурсивных обновлений
        self.updating = False

        # Подключаем UI сигналы
        self.connect_ui_signals()

        # Инициализируем конвертер
        self.converter = CurrencyConverter()

    def connect_ui_signals(self):
        """Подключение сигналов UI"""
        # Подключаем поля ввода к сигналам (отправка)
        self.rub_input.textChanged.connect(self.on_rub_input_changed)
        self.usd_input.textChanged.connect(self.on_usd_input_changed)
        self.eur_input.textChanged.connect(self.on_eur_input_changed)

        # Подключаем сигналы к полям ввода (получение)
        rub_signals.rub_changed.connect(self.on_rub_signal_received)
        usd_signals.usd_changed.connect(self.on_usd_signal_received)
        eur_signals.eur_changed.connect(self.on_eur_signal_received)

        # Подключаем кнопку очистки
        self.clear_button.clicked.connect(common_signals.clear_all.emit)

        # Подключаем обновление курсов
        common_signals.rates_updated.connect(self.update_rates_display)
        common_signals.clear_all.connect(self.clear_fields)

    def on_rub_input_changed(self, text):
        """Обработка изменения поля RUB (отправка сигнала)"""
        if not self.updating:
            rub_signals.rub_changed.emit(text)

    def on_usd_input_changed(self, text):
        """Обработка изменения поля USD (отправка сигнала)"""
        if not self.updating:
            usd_signals.usd_changed.emit(text)

    def on_eur_input_changed(self, text):
        """Обработка изменения поля EUR (отправка сигнала)"""
        if not self.updating:
            eur_signals.eur_changed.emit(text)

    def on_rub_signal_received(self, text):
        """Обработка получения сигнала RUB (обновление поля)"""
        self.updating = True
        self.rub_input.setText(text)
        self.updating = False

    def on_usd_signal_received(self, text):
        """Обработка получения сигнала USD (обновление поля)"""
        self.updating = True
        self.usd_input.setText(text)
        self.updating = False

    def on_eur_signal_received(self, text):
        """Обработка получения сигнала EUR (обновление поля)"""
        self.updating = True
        self.eur_input.setText(text)
        self.updating = False

    def clear_fields(self):
        """Очистка полей ввода"""
        self.updating = True
        self.rub_input.clear()
        self.usd_input.clear()
        self.eur_input.clear()
        self.updating = False

    def update_rates_display(self, rates):
        """Обновление отображения курсов валют"""
        rates_text = (f"Курсы: 1$ = {rates['USD_RUB']:.2f}₽ | "
                      f"1€ = {rates['EUR_RUB']:.2f}₽ | "
                      f"1$ = {rates['USD_EUR']:.2f}€")
        self.rates_label.setText(rates_text)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Конвертер валют"))

        self.rub_label.setText(_translate("MainWindow", "RUB ₽"))
        self.usd_label.setText(_translate("MainWindow", "USD $"))
        self.eur_label.setText(_translate("MainWindow", "EUR €"))

        self.clear_button.setText(_translate("MainWindow", "Очистить все"))

        # Временный текст, который обновится при получении курсов
        self.rates_label.setText(_translate("MainWindow", "Загрузка курсов..."))

        self.rub_input.setPlaceholderText(_translate("MainWindow", "Введите рубли"))
        self.usd_input.setPlaceholderText(_translate("MainWindow", "Введите доллары"))
        self.eur_input.setPlaceholderText(_translate("MainWindow", "Введите евро"))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())