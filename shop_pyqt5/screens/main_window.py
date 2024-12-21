from config.window_settings import WindowSettings
from screens.purchase_window import PurchaseWindow

from PyQt5.QtWidgets import QWidget, QMessageBox, QLabel, QGridLayout, QPushButton, QApplication
from PyQt5.QtGui import QPixmap, QImage, QPixmap, QFont, QFontDatabase
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QRegExp
from PyQt5.uic import loadUi


class MainWindow(QWidget):
    """
    Тут будет длинная документ-строка!
    """
    def __init__(self, app, user_data=None):
        super(MainWindow, self).__init__()
        loadUi("ui/main.ui", self)

        self.app = app
        self.window_settings = WindowSettings(self, app)

        self.window_settings.settings()
        self.available_fonts = self.window_settings.load_fonts(app)
        
        self.mousePressEvent = self.window_settings.mousePressEvent # Эта и то что ниже чтобы Drag (перетаскивать) окно по экрану
        self.mouseMoveEvent = self.window_settings.mouseMoveEvent
        self.mouseDoubleClickEvent = self.window_settings.mouseDoubleClickEvent

        self.exit = self.window_settings.exit # Прописан выход (кнопки в левом верхнем углу)
        self.minimize_app = self.window_settings.minimize_app
        self.maximize_app = self.window_settings.maximize_app

        self.exitButton.clicked.connect(self.exit)
        self.minimizeButton.clicked.connect(self.minimize_app)
        self.maximizeButton.clicked.connect(self.maximize_app)

        self.contactsButton.clicked.connect(self.contact_info)
        self.clear_cart_button.clicked.connect(self.clear_cart)
        self.cart_button_purchase.clicked.connect(self.get_order)

        # Ловим объекты продукта чтобы добавить их в корзину при нажатии кнопки
        self.count_of_products = 0   # Количество товара для счетчика (button)
        product_categories = self.findChildren(QLabel, QRegExp("product_card_name_\d+"))
        purchase_buttons = self.findChildren(QPushButton, QRegExp("product_card_buy_button_\d+"))
        for button, label in zip(purchase_buttons, product_categories):
            button.clicked.connect(lambda checked, btn=button, lbl=label:self.purchased_item(btn.objectName(), lbl.text()))

        self.frame_2.setMaximumWidth(55)    # Устанавливаем начальное состояние шторки - она закрыта.
        self.frame_2.setMinimumWidth(55)    
        self.side_menu_num = 0
        self.toolButton.clicked.connect(self.side_menu_def)

        self.animated_menu_buttons = [self.toolButton_main, self.toolButton_profile, self.toolButton_storage, self.toolButton_information]
        
        for i, button in enumerate(self.animated_menu_buttons):
            button.clicked.connect(lambda _, index=i: self.change_page_menu(index))

        self.logoutButton.clicked.connect(self.logout)
        
        # Обновляем данные пользователя при открытии окна
        if user_data:
            self.update_user_data(user_data)
        else:
            # Если нет, пытаемся загрузить данные текущего пользователя из базы данных
            current_user_data = self.window_settings.get_current_user() # Вообще, это должно быть в config'e но и так сойдет)))
            if current_user_data:
                self.update_user_data({
                    'username': current_user_data[0],   # Ну и тут в общем-то, мы тупо дублируем user_data из auth.py
                    'email': current_user_data[1],
                    'avatar_path': current_user_data[2]
                })

        self.frames = [self.first_product, self.second_product, self.third_product, self.fourth_product,    # Список наших карточек с товаром
                  self.fifth_product, self.sixth_product, self.seventh_product, self.eighth_product, self.ninth_product, self.ten_product]  
        
        self.product_filter_combobox.currentIndexChanged.connect(self.product_filters)
        self.product_category_combobox.currentIndexChanged.connect(self.product_filters)
        self.change_font_combobox.currentIndexChanged.connect(self.font_changed)
        self.change_window_size_combobox.currentIndexChanged.connect(self.change_window_size)

        self.product_finder_line_edit.textChanged.connect(self.search)

        self.checkBox_cheapest_prices.stateChanged.connect(self.sort_frames_by_price)
        self.checkBox_switch_theme.stateChanged.connect(self.switch_theme)

    def update_user_data(self, user_data):
        username, email, avatar_path = user_data['username'], user_data['email'], user_data['avatar_path']

        self.username_label.setText(username)
        self.email_label.setText(email)

        image = QImage.fromData(avatar_path)
        pixmap = QPixmap.fromImage(image)
        self.avatar_label.setPixmap(pixmap.scaled(self.avatar_label.width(), self.avatar_label.height()))
    
    def change_window_size(self, index):
        """Функция служит для возможности менять размер окна"""
        selected_size = self.change_window_size_combobox.itemText(index)
        print(f'Размер окна {selected_size} выбран...')

        match (index):
            case 0:
                width, height = 1067, 659
            case 1:
                self.showFullScreen()
            case 2:
                width, height = 800, 600
            case 3:
                width, height = 1024, 720
            case 4:
                width, height = 1280, 1024
            
        if index != 1:
            self.resize(width, height)

    def font_changed(self, index):
        """Меняем шрифт на основном экране"""
        selected_font = self.available_fonts[index]
        font = QFont()
        font.setFamily(selected_font)
        self.app.setFont(font)
        for widget in self.findChildren(QWidget):
            widget.setFont(self.app.font())
        print(f'Шрифт поменян на: {selected_font}')
        
        # Дополнительные проверки
        current_font = self.app.font().family()
        print(f"Текущий шрифт: {current_font}")

    def contact_info(self):
        print('Информация об разработчике...')
        QMessageBox.information(self, 'Основная информация', 'По вопросам и возникшим проблемам обращайтесь по электронной почте contacts@gmail.com\nMade by Nightwalker\n¯\_(ツ)_/¯')
    
    def switch_theme(self):
        """Переключение между светлой и темной темой"""
        if self.checkBox_switch_theme.isChecked():
            self.window_settings.set_style('resources/styles/purple_theme.qss')
        else:
            self.window_settings.set_style('resources/styles/black_theme.qss')

    def side_menu_def(self):
        def update_buttons(is_enabled):
            """Включаем/выключаем (enabled) кнопки в зависимости от состояния шторки"""
            for button in self.animated_menu_buttons:
                button.setEnabled(is_enabled)

        def animate_frame_width(start_value, end_value):
            """Задаем анимацию нашей шторке, чтобы она получала стартовое и заканчивающее значение"""
            self.animation_1 = QPropertyAnimation(self.frame_2, b"maximumWidth")
            self.animation_2 = QPropertyAnimation(self.frame_2, b"minimumWidth")

            for animation in (self.animation_1, self.animation_2):
                animation.setDuration(400)  # Длина анимации
                animation.setStartValue(start_value)
                animation.setEndValue(end_value)
                animation.setEasingCurve(QEasingCurve.InOutQuart)
                animation.start()

        if self.side_menu_num == 0:
            print('Открываем шторку...')
            animate_frame_width(start_value=55, end_value=160)
            update_buttons(True)
            self.side_menu_num = 1
        else:
            print('Закрываем шторку...')
            animate_frame_width(start_value=160, end_value=55)
            update_buttons(False)
            self.side_menu_num = 0

    def change_page_menu(self, index):
        current_index = self.stackedNavigateMenu.currentIndex()
        if current_index != index:
            print(f"Переключаемся на страницу {index}...")
            self.stackedNavigateMenu.setCurrentIndex(index)
        else:
            print("Пользователь уже находится на этой странице.")

    def logout(self):
        from screens.authorization_window import AuthorizationWindow
        answer = QMessageBox.warning(self, 'Подтверждение', '\nВыйти из аккаунта?', buttons=QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.Yes)
        if answer == QMessageBox.Yes:
            print('Выходим из аккаунта...')
            self.window_settings.clear_current_user()
            self.close()
            authorization_window = AuthorizationWindow(self.app)
            authorization_window.show()
      
    def search(self, text):
        """Функция для поиска необходимого товара по имени в lineEdit'e"""
         # Получаем введенный текст
        search_text = text.lower()
        
        # Проходим по всем фреймам
        for frame in self.frames:
            # По умолчанию считаем, что фрейм должен быть скрыт
            should_show_frame = False
            
            # Ищем метки названия товара внутри данного фрейма
            name_labels = frame.findChildren(QLabel, QRegExp("product_card_name_\d+"))
            
            # Проверяем каждую метку на наличие искомого текста
            for name_label in name_labels:
                if search_text in name_label.text().lower():
                    should_show_frame = True
                    break  # Прерываем цикл, если нашли хотя бы одно совпадение
            
            # Устанавливаем видимость фрейма в соответствии с результатом проверки
            if should_show_frame:
                frame.show()
            else:
                frame.hide()

    def sort_frames_by_price(self):
        """Сортировка цены по убыванию"""
        product_names = self.findChildren(QLabel, QRegExp("product_card_price_\d+"))
        layout = self.scroll_price_widget.widget().layout()

        def extract_price_from_label(label):
            text = label.text()
            price_pattern = QRegExp(r"\d+\.\d+")  # Регулярное выражение для поиска чисел вида 123.456
            index = price_pattern.indexIn(text)   # Находим позицию первого совпадения
            if index != -1:
                price_str = price_pattern.capturedTexts()[0]
                return float(price_str)           # Преобразуем строку в число с плавающей точкой
            else:
                return None                       # Если цена не найдена, возвращаем None

        if self.checkBox_cheapest_prices.isChecked():  # Проверяем, отмечен ли чекбокс
            print('Сортируем по возрастанию...')
            ascending = False  # Если отмечен, сортируем по возрастанию (наименьшей цене)
        else:
            print('Сортируем по убыванию...')
            ascending = True  # Если не отмечен, сортируем по убыванию (наибольшей цене)

        frames_with_prices = []  # Список пар (frame, price)
        
        for product_name in product_names:
            price = extract_price_from_label(product_name)
            frame = product_name.parent()  # Предполагаем, что метка находится внутри нужного фрейма
            frames_with_prices.append((frame, price))
        
        # Сортируем пары по цене
        sorted_frames = sorted(frames_with_prices, key=lambda item: item[1], reverse=not ascending)
        
        # Применяем новую последовательность фреймов
        for i, (frame, _) in enumerate(sorted_frames):
            layout.removeWidget(frame)
            layout.insertWidget(i, frame)
                
    def product_filters(self):
        """Функция отвечает за фильтрацию продуктов в карточках, в частности:
        current_index забирает текущий index combobox'a который нажмет пользователь
        frames - это наши карточки вместе взятые в виде списка"""

        filter_index = self.product_filter_combobox.currentIndex()
        category_index = self.product_category_combobox.currentIndex()

        product_names = self.findChildren(QLabel, QRegExp("product_fabricator_\d+"))
        product_categories = self.findChildren(QLabel, QRegExp("product_card_name_\d+"))

        fabricator_keywords = ['Все', 'apple', 'samsung', 'xiaomi']  # Ключевые слова для производителей
        category_keywords = ['Все', 'смартфон', 'ноутбук', 'планшет']  # Ключевые слова для категорий товаров

        fabricator_keyword = fabricator_keywords[filter_index].lower()
        category_keyword = category_keywords[category_index].lower()

        filtered_product_names = [product_name for product_name in product_names if fabricator_keyword.lower() in product_name.text().lower()]
        filtered_product_categories = [product_category for product_category in product_categories if category_keyword.lower() in product_category.text().lower()]

        # visible_frames_before_filtering = [frame for frame in self.frames if frame.isVisible()]

        def find_label_parents():
            for frame in self.frames:
                if (
                    any(label.parent() is frame for label in filtered_product_names) and
                    any(category.parent() is frame for category in filtered_product_categories)
                ):
                    frame.show()
                else:
                    frame.hide()
            print(f"Сортировка по {fabricator_keyword} и {category_keyword} выполнена...")

        match (filter_index, category_index):
            case (0, 0):  # Оба фильтра выбраны на "Все"
                print('Оба фильтра выбраны на "Все"')
                for frame in self.frames:
                    frame.show()
            case (0, _):  # Только фильтр категории
                print(f'Фильтр категории: {category_keyword}')
                for frame in self.frames:
                    if any(category.parent() is frame for category in filtered_product_categories):
                        frame.show()
                    else:
                        frame.hide()
                print(f'Сортировка по категории {category_keyword} выполнена...')
            case (_, 0):  # Только фильтр производителя
                print(f'Фильтр производителя: {fabricator_keyword}')
                for frame in self.frames:
                    if any(label.parent() is frame for label in filtered_product_names):
                        frame.show()
                    else:
                        frame.hide()
                print(f'Сортировка по производителю {fabricator_keyword} выполнена...')
            case (_, _):  # Оба фильтра
                print(f'Фильтр производителя: {fabricator_keyword}, Фильтр категории: {category_keyword}')
                find_label_parents()
   
    def update_total_price(self):
        """Тут ловим все суммарные ценники продуктов"""
        # Инициализируем переменную для хранения общей суммы
        total_sum = 0.0

        # Находим все виджеты с ценой в корзине
        price_labels = self.cartAreaGrid.findChildren(QLabel, QRegExp("product_card_price_\d+"))

        # Проходимся по всем найденным виджетам и суммируем их значения
        for price_label in price_labels:
            # Извлекаем цену из текста виджета
            price_text = price_label.text()
            # Очищаем строку от лишних символов
            clean_price = price_text.strip().split(':')[1].strip().replace(',', '.').replace(' рублей', '')  # Убираем "рублей"

            try:
                # Преобразуем в число с плавающей точкой
                total_sum += float(clean_price)
            except ValueError as e:
                print(f"Произошла ошибка при обработке цены: {e}")

        # Формируем строку для вывода в total_price_label
        total_price_str = f"Общая сумма: {total_sum:.3f} рублей"
        # Устанавливаем текст в виджет total_price_label
        self.total_price_label.setText(total_price_str)

    def purchased_item(self, button_name, product_name):
        # Получаем номер товара из имени кнопки
        item_number = int(button_name.split("_")[-1]) - 1  # Отнимаем 1, потому что индексация начинается с нуля
        original_frame = self.frames[item_number]   # Получаем оригинальный фрейм по номеру
        
        # Находим кнопку "купить" внутри этого фрейма
        buy_button = original_frame.findChild(QPushButton, f"product_card_buy_button_{item_number + 1}")
        on_sale_check = original_frame.findChild(QLabel, f"product_on_sale_check_{item_number + 1}")

        # Делаем кнопку невидимой
        buy_button.setVisible(False)
        on_sale_check.setText('Товар в корзине')

        # Добавляем товар в корзину
        self.add_to_cart(original_frame)
        print(f"Товар '{product_name}' (№{item_number + 1}) выбран...")

    def add_to_cart(self, frame):
        print('Продукт добавлен в корзину...')

        self.count_of_products += 1
        self.toolButton_profile.setText(f' Корзина ({self.count_of_products})')
        
        # Удаляем фрейм из старого места и добавляем в корзину
        old_layout = frame.parent().layout()
        old_index = old_layout.indexOf(frame)
        old_layout.removeWidget(frame)
        frame.setParent(None)
        
        self.cartAreaGrid.layout().addWidget(frame)
        print(f"Фрейм перемещён в корзину: {frame}")

        self.update_total_price()  # Обновляем общую стоимость после добавления товара

    def clear_cart(self):
        """Очищаем корзину (функция вернет исходное состояние всех виджетов)"""
        pass
        # self.main_window = MainWindow(self.app)
        # self.main_window.close()
        # self.main_window.show()

    def get_order(self):
        print('Формируем заказ...')

        if self.total_price_label.text() == 'Итоговая цена: 0.00 рублей':
            self.cart_error_label.setText('Ошибка: Корзина пуста')
        else:
            purchase_win = PurchaseWindow(self.app)
            purchase_win.show()
            self.cart_error_label.setText('')