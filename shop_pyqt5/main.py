import sys 

from PyQt5.QtWidgets import QApplication
from screens.authorization_window import AuthorizationWindow
from screens.main_window import MainWindow
from config.window_settings import WindowSettings

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    current_user = WindowSettings.get_current_user()
    if current_user:
        # Если текущий пользователь найден, то сразу открываем главное окно
        main_win = MainWindow(app)
        main_win.window_settings.set_style('resources/styles/black_theme.qss')
        main_win.show()
    else:
        # Иначе показываем окно авторизации
        window = AuthorizationWindow(app)
        window.window_settings.set_style('resources/styles/black_theme.qss')
        window.show()

    sys.exit(app.exec())