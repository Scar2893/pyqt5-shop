import sys 
import sqlite3

from config.window_settings import WindowSettings
from screens.main_window import MainWindow
from screens.registration_window import RegistrationWindow

from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi


class AuthorizationWindow(QWidget):
    """
    Тут будет длинная документ-строка!
    """
    def __init__(self, app):
        super(AuthorizationWindow, self).__init__()
        loadUi("ui/auth.ui", self)
        
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

        self.auth_button.clicked.connect(self.authorization)
        self.registration_button.clicked.connect(self.registration)
        
    
    def authorization(self):
        print('Кнопка авторизации нажата!')

        name = self.login_line_edit.text()
        password = self.password_line_edit.text()

        if len(name) == 0 or len(password) == 0:
            self.except_label.setText('Пожалуйста, заполните все поля')
        else:
            con = sqlite3.connect('database/main_data.db')
            cur = con.cursor()
            print("Подключен к SQLite")

            query = '''SELECT name, email, avatar FROM users WHERE name = ? AND password = ?'''
            cur.execute(query, (name, password))
            result = cur.fetchone()
            if result:
                print('Успешная авторизация...')

                user_data = {
                    'username': result[0],
                    'email': result[1],
                    'avatar_path': result[2]
                }
                if self.checkbox_remember_me.isChecked():
                    save_user_query = '''INSERT OR REPLACE INTO current_user (user_name, email, avatar_path) VALUES (?, ?, ?)'''
                    cur.execute(save_user_query, (result[0], result[1], result[2]))
                    con.commit()

                self.close()
                main_win = MainWindow(self.app, user_data)
                main_win.show()
            else:
                self.except_label.setText('Неверное имя пользователя или пароль.')

            con.close()
            print("Соединение с SQLite закрыто") 

    def registration(self):
        """
        Данная функция нужна для того чтобы закрыть окон авторизации,
        и перейти в окно регистрации.
        """
        print('Кнопка регистрации нажата!')
        self.close()
        main_win = RegistrationWindow(self.app)
        main_win.show()