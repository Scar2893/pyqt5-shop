import re
import sys 
import sqlite3

from config.window_settings import WindowSettings

from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi


class RegistrationWindow(QWidget):
    """
    Тут будет длинная документ-строка!
    """
    def __init__(self, app):
        super(RegistrationWindow, self).__init__()
        loadUi("ui/registration.ui", self)

        self.app = app
        self.window_settings = WindowSettings(self, app)
    
        self.window_settings.settings()

        self.mousePressEvent = self.window_settings.mousePressEvent # Эта и то что ниже чтобы Drag (перетаскивать) окно по экрану
        self.mouseMoveEvent = self.window_settings.mouseMoveEvent
        self.mouseDoubleClickEvent = self.window_settings.mouseDoubleClickEvent
        
        self.exit = self.window_settings.exit # Прописан выход (кнопки в левом верхнем углу)
        self.minimize_app = self.window_settings.minimize_app
        self.maximize_app = self.window_settings.maximize_app

        self.exitButton.clicked.connect(self.exit)
        self.minimizeButton.clicked.connect(self.minimize_app)
        self.maximizeButton.clicked.connect(self.maximize_app)

        self.register_button.clicked.connect(self.create_account)
        self.return_button.clicked.connect(self.return_to_auth)
        self.uploadImage.clicked.connect(self.upload_avatar)

    def upload_avatar(self):
        print('Аватар в процессе создания...')
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog  # Убираем если хотим обычный проводник
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите фото профиля",
            "",
            "Images (*.png *.jpeg *.jpg)",
            options=options
        )
        if file_name:
            pixmap = QPixmap(file_name)
            scaled_pixmap = pixmap.scaled(128, 128, Qt.KeepAspectRatio)
            icon = QIcon(scaled_pixmap)
            self.uploadImage.setIcon(icon)
            self.uploadImage.setIconSize(QtCore.QSize(128, 128))
            self.avatar = file_name
            self.upload_avatar_label.setText('Аватар успешно загружен...')

    def create_account(self):
        """
        Функция большая, объяснений будет много.  Ыыыы
        """
        name = self.login_line_edit.text()
        password = self.password_line_edit.text()
        email = self.mail_line_edit.text()
        avatar = getattr(self, 'avatar', None)  # getattr - get_atribute, забираем атрибут элемента

        if len(password) < 6:
            self.except_label.setText('Пароль должен содержать минимум 6 символов.')
            return

        
        email_regex = r'^([a-zA-Z0-9_.+-]+)@((?:[a-zA-Z0-9-]+\.)?(gmail|yahoo|hotmail|outlook|yandex|mail\.ru|rambler\.ru|ukr\.net|i\.ua|bigmir\.net|meta\.ua|google)[a-zA-Z]{2,4}|(?:[a-zA-Z0-9-]+\.)*(com|net|org|edu|gov|info|biz|io|me|ru|ua|by))$'
        if not re.fullmatch(email_regex, email):
            self.except_label.setText('Введите корректный адрес электронной почты.')
            return

        if not all([name, password, email, avatar]):    # Аналог if [name,password, email, avatr == "" (Пустое поле)]
            self.except_label.setText('Пожалуйста, заполните все поля.')
            
        if avatar is None:
            self.upload_avatar_label.setText('Аватар не добавлен...')
        else:
            with open(avatar, 'rb') as f:
                upload_avatar = f.read()

            con = sqlite3.connect('database/main_data.db')
            cur = con.cursor()
            print("Подключен к SQLite")
            try:
                cur.execute('''INSERT INTO users (name, password, email, avatar)
                VALUES (?, ?, ?, ?)''', (name, password, email, upload_avatar))
                con.commit()    # В данном запросе не добавляем id, т.к это наш первичный ключ и он заполнится сам
                print('Успешная регистрация...')
                QMessageBox.information(self, "Подтверждение", "\nВы успешно зарегистрировались", buttons=QMessageBox.Ok, defaultButton=QMessageBox.Ok)

                from screens.authorization_window import AuthorizationWindow
                self.close()
                main_win = AuthorizationWindow(self.app)
                main_win.show()
            except sqlite3.IntegrityError:
                self.except_label.setText('Такой пользователь уже существует.')
            con.close()
            print("Соединение с SQLite закрыто")

    def return_to_auth(self):
        print('Выходим из окна регистрации...')

        from screens.authorization_window import AuthorizationWindow
        self.close()
        main_win = AuthorizationWindow(self.app)
        main_win.show()