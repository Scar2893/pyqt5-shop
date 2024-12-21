import sys 
import sqlite3

from PyQt5.QtWidgets import QMessageBox, QDesktopWidget, QWidget
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPixmap, QImage, QFontDatabase, QFont

class WindowSettings():
    """
    Данный класс является классом-конфигуратором, он нужен для того чтобы задать всем окнам один общий стиль,
    так же здесь есть функции позволяющие загружать/выгружать определенные данные из базы данных, 
    имеет за собой общие настройки приложения и он влияет на все окна в проекте (поменяете здесь шрифт - он поменяется везде)
    """
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.is_maximized = False
        self.load_fonts(app)  # Загружаем шрифтец

        self.is_resizing = False
        self.mouse_press_pos = None
        self.mouse_move_pos = None
        self.border_width = 10  # Ширина области захвата для изменения размера окна

    def settings(self):
        """Задаем параметры для всего приложения, шрифт, иконку для приложения и название."""
        self.parent.setWindowIcon(QtGui.QIcon('resources/images/shop_menu.png'))
        self.parent.setWindowTitle("Nightwalker's Shop")
        self.parent.oldPos = self.parent.pos()
        self.parent.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # Убираем через флаги дефолтное окно Windows

    @staticmethod
    def get_current_user():
        """ 
        Функция для получения текущего пользователя из базы данных. 
        Возвращает кортеж с данными пользователя (имя, почта, аватар), либо None, если пользователь не найден. 
        """
        try:
            con = sqlite3.connect('database/main_data.db')
            cur = con.cursor()
            print("Подключен к SQLite")
            cur.execute('''SELECT user_name, email, avatar_path FROM current_user LIMIT 1''')
            result = cur.fetchone()
            if result:
                print(f"Получены данные пользователя: {result[0]}, {result[1]}")  # Логируем полученные данные
                return result
            else:
                print("Текущий пользователь не найден.")
        except ConnectionError as e:
            print(f"Произошла ошибка: {e}")
        finally:
            con.close()
            print("Соединение с SQLite закрыто")

    @staticmethod
    def clear_current_user():
        """Очищает текущие данные пользователя."""
        try:
            con = sqlite3.connect('database/main_data.db')
            cur = con.cursor()
            print("Подключен к SQLite")
            cur.execute('''DELETE FROM current_user''')
            con.commit()
            print("Данные пользователя очищены.")
        except ConnectionError as e:
            print(f"Произошла ошибка: {e}")
        finally:
            con.close()
            print("Соединение с SQLite закрыто")

    def update_user_data(self, username_label, email_label, avatar_label):
        """Обновляет виджеты с информацией о пользователе."""
        user_data = self.get_current_user()
        if user_data is not None:
            username, email, avatar_path = user_data
            username_label.setText(username)
            email_label.setText(email)

            image = QImage.fromData(avatar_path)
            pixmap = QPixmap.fromImage(image)
            avatar_label.setPixmap(pixmap.scaled(avatar_label.width(), avatar_label.height()))
        else:
            username_label.setText("")
            email_label.setText("")
            avatar_label.setPixmap(QPixmap())  # тут прописываем условие если вдруг имени/аватарки не оказалось

    def set_style(self, filename):
        """
        Тут забираем стили для наших окон из файла style.qss
        qss - это как css, только что-то на питоновском
        """
        try:
            with open(filename, encoding='utf-8') as f:   # Применяем стили qss
                style = f.read()
                self.app.setStyleSheet(style)
        except FileNotFoundError:
            print('Файл стилей не найден')
            QMessageBox.warning(self.parent, 'Ошибка', 'Файл стилей не был обнаружен', buttons=QMessageBox.Ok, defaultButton=QMessageBox.Ok)
      
    def load_fonts(self, app):
        """Загружаем шрифт и устанавливаем его для всего приложения."""
        fonts = [
            'resources/fonts/copperplate_font.ttf',
            'resources/fonts/borsok_font.ttf',
            'resources/fonts/docker_font.ttf'
        ]

        available_fonts = []
        default_font = False

        for font in fonts:
            font_id = QFontDatabase.addApplicationFont(font)
            
            if font_id != -1:
                font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                available_fonts.append(font_family)
                print(f'Шрифт {font} успешно загружен...')
                
                if 'copperplate' in font.lower():
                    default_font = font_family
            else:
                print(f"Ошибка загрузки шрифта {font}...")

        if default_font:
            font = QFont(default_font)
            app.setFont(font)
            print(f'Шрифт по умолчанию установлен: {default_font}')

        return available_fonts
        
    def resizeEvent(self, event):
        """
        При помощи данной функции меняем нашу классическую форму на нашу кастомную,
        таким образом мы можем системные окна выводить с нашим стилем.
        """
        pixmap = QtGui.QPixmap(self.parent.size())
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setBrush(QtCore.Qt.black)
        painter.drawRoundedRect(pixmap.rect(), 15, 15)
        painter.end()	
        self.parent.setMask(pixmap.mask()) 

    def center(self):
        """
        Ну тут в общем ребята пониже (2 функции ниже) и эта,
        используются чтобы мы могли наше приложение адекватно перетаскивать на экране (Drag)
        """
        qr = self.parent.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.parent.move(qr.topLeft())

    def mousePressEvent(self, event): 
        self.parent.oldPos = event.globalPos()
                     
    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.parent.oldPos)
        self.parent.move(self.parent.x() + delta.x(), self.parent.y() + delta.y())
        self.parent.oldPos = event.globalPos()

    def mouseDoubleClickEvent(self, event):
        """При двойном клике на форму наше приложение сворачивается/разворачивается"""
        print('Окно изменилось при двойном клике!')
        self.maximize_app()

    def exit(self):
        """Функция для выхода из приложения, спрашивает будем выходить или нет."""
        answer = QMessageBox.warning(self.parent, 'Подтверждение', '\nВы действительно хотите выйти?', buttons=QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.Yes)
        if answer == QMessageBox.Yes:
            print('Приложение закрылось корректно.')
            sys.exit(self.app.quit())

    def minimize_app(self):
        """ Функция просто забирает метод для сворачивания приложения."""
        self.parent.showMinimized()

    def maximize_app(self):
        """
        Функция для расширения окна, проверяет в каком оно состоянии и потом либо сворачивает,
        либо разворачивает.
        parent.pos показывает координаты она на мониторе.
        """
        if not self.is_maximized:
            self.parent.showMaximized()
            self.is_maximized = True
        else:
            self.parent.showNormal()
            self.resizeEvent(None)
            self.is_maximized = False
        
        print(f"Текущие координаты окна: {self.parent.pos()}") # текущие координаты окна