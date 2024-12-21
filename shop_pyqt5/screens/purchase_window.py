from config.window_settings import WindowSettings

from PyQt5.QtWidgets import QWidget, QMessageBox, QLabel, QGridLayout, QPushButton, QApplication
from PyQt5.QtGui import QPixmap, QImage, QPixmap, QFont, QFontDatabase
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QRegExp, QRect
from PyQt5.uic import loadUi

class PurchaseWindow(QWidget):
    """
    Форма для совершения покупки
    """
    def __init__(self, app):
        super(PurchaseWindow, self).__init__()
        loadUi("ui/purchase.ui", self)

        self.app = app
        self.window_settings = WindowSettings(self, app)

        self.window_settings.settings()
        self.available_fonts = self.window_settings.load_fonts(app)
        
        self.mousePressEvent = self.window_settings.mousePressEvent # Эта и то что ниже чтобы Drag (перетаскивать) окно по экрану
        self.mouseMoveEvent = self.window_settings.mouseMoveEvent
        self.mouseDoubleClickEvent = self.window_settings.mouseDoubleClickEvent

        self.minimize_app = self.window_settings.minimize_app
        self.maximize_app = self.window_settings.maximize_app

        self.exitButton.clicked.connect(self.window_exit)
        self.minimizeButton.clicked.connect(self.minimize_app)
        self.maximizeButton.clicked.connect(self.maximize_app)

        self.purchase_button_pay.clicked.connect(self.get_payment)
    
    def get_payment(self):
        print('Оформляем покупку...')

        if self.number_line_edit.text() == '9999999999999999' and self.csv_line_edit.text() == '999':
            self.purchase_image_label.setPixmap(QPixmap('resources/images/accept_payment.png'))
            self.payment_position_label.setText(f'Тестовая покупка совершена, {self.name_line_edit.text()}...')
        else:
            self.payment_position_label.setText('Ошибка: Неверные данные')

    def window_exit(self):
        self.close()
    
