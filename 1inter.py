import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QListWidget, QComboBox, 
                            QDateEdit, QTimeEdit, QSpinBox, QTabWidget, QMessageBox)
from PyQt5.QtCore import QDate, QTime, Qt
from PyQt5.QtGui import QFont, QIcon

class PhotoStudioApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Фотостудия - Система бронирования")
        self.setWindowIcon(QIcon("camera_icon.png"))
        self.setMinimumSize(900, 600)
        
        # Основные данные
        self.clients = []
        self.bookings = []
        self.halls = [
            {"number": 1, "price": 2000, "capacity": 5},
            {"number": 2, "price": 3000, "capacity": 10},
            {"number": 3, "price": 2500, "capacity": 8}
        ]
        self.equipment = [
            {"name": "Профессиональный свет", "price": 500},
            {"name": "Фон белый", "price": 300},
            {"name": "Фон черный", "price": 300},
            {"name": "Реквизит", "price": 200}
        ]
        
        self.init_ui()
        self.apply_styles()
        
    def init_ui(self):
        # Главный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Создаем вкладки
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # Вкладка бронирований
        booking_tab = QWidget()
        self.setup_booking_tab(booking_tab)
        tab_widget.addTab(booking_tab, "Бронирования")
        
        # Вкладка клиентов
        clients_tab = QWidget()
        self.setup_clients_tab(clients_tab)
        tab_widget.addTab(clients_tab, "Клиенты")
        
        # Вкладка отчетов
        reports_tab = QWidget()
        self.setup_reports_tab(reports_tab)
        tab_widget.addTab(reports_tab, "Отчеты")
        
        # Боковая панель с информацией
        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Информация о студии
        studio_info = QLabel("Фотостудия LIGHT AND SHADOW \n\nЧасы работы:\n9:00 - 22:00\n\nКонтакты:\n+7 (123) 456-78-90")
        studio_info.setAlignment(Qt.AlignCenter)
        
        # Быстрые действия
        quick_actions_label = QLabel("Быстрые действия:")
        quick_actions_label.setAlignment(Qt.AlignCenter)
        
        new_booking_btn = QPushButton("Новое бронирование")
        new_booking_btn.clicked.connect(lambda: tab_widget.setCurrentIndex(0))
        
        new_client_btn = QPushButton("Новый клиент")
        new_client_btn.clicked.connect(lambda: tab_widget.setCurrentIndex(1))
        
        sidebar_layout.addWidget(studio_info)
        sidebar_layout.addWidget(quick_actions_label)
        sidebar_layout.addWidget(new_booking_btn)
        sidebar_layout.addWidget(new_client_btn)
        sidebar_layout.addStretch()
        
        main_layout.addWidget(sidebar)
        
    def setup_booking_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        # Форма бронирования
        booking_form = QWidget()
        form_layout = QVBoxLayout(booking_form)
        
        # Выбор клиента
        client_group = QWidget()
        client_layout = QHBoxLayout(client_group)
        client_layout.addWidget(QLabel("Клиент:"))
        self.client_combo = QComboBox()
        self.client_combo.setEditable(True)
        self.client_combo.setPlaceholderText("Выберите или введите нового клиента")
        client_layout.addWidget(self.client_combo)
        
        # Выбор зала
        hall_group = QWidget()
        hall_layout = QHBoxLayout(hall_group)
        hall_layout.addWidget(QLabel("Зал:"))
        self.hall_combo = QComboBox()
        for hall in self.halls:
            self.hall_combo.addItem(f"Зал {hall['number']} ({hall['price']} руб/час, до {hall['capacity']} чел.)", hall)
        hall_layout.addWidget(self.hall_combo)
        
        # Дата и время
        datetime_group = QWidget()
        datetime_layout = QHBoxLayout(datetime_group)
        datetime_layout.addWidget(QLabel("Дата:"))
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        datetime_layout.addWidget(self.date_edit)
        datetime_layout.addWidget(QLabel("Время:"))
        self.time_edit = QTimeEdit(QTime(12, 0))
        datetime_layout.addWidget(self.time_edit)
        
        # Длительность
        duration_group = QWidget()
        duration_layout = QHBoxLayout(duration_group)
        duration_layout.addWidget(QLabel("Длительность (часы):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 8)
        self.duration_spin.setValue(2)
        duration_layout.addWidget(self.duration_spin)
        
        # Оборудование
        equipment_group = QWidget()
        equipment_layout = QVBoxLayout(equipment_group)
        equipment_layout.addWidget(QLabel("Дополнительное оборудование:"))
        self.equipment_list = QListWidget()
        for item in self.equipment:
            self.equipment_list.addItem(f"{item['name']} (+{item['price']} руб/час)")
        self.equipment_list.setSelectionMode(QListWidget.MultiSelection)
        equipment_layout.addWidget(self.equipment_list)
        
        # Кнопка бронирования
        book_btn = QPushButton("Забронировать")
        book_btn.clicked.connect(self.create_booking)
        
        # Добавляем все в форму
        form_layout.addWidget(client_group)
        form_layout.addWidget(hall_group)
        form_layout.addWidget(datetime_group)
        form_layout.addWidget(duration_group)
        form_layout.addWidget(equipment_group)
        form_layout.addWidget(book_btn)
        
        # Список бронирований
        bookings_list_label = QLabel("Активные бронирования:")
        self.bookings_list = QListWidget()
        
        layout.addWidget(booking_form)
        layout.addWidget(bookings_list_label)
        layout.addWidget(self.bookings_list)
        
    def setup_clients_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        # Форма добавления клиента
        client_form = QWidget()
        form_layout = QVBoxLayout(client_form)
        
        # Имя
        name_group = QWidget()
        name_layout = QHBoxLayout(name_group)
        name_layout.addWidget(QLabel("Имя:"))
        self.first_name_edit = QLineEdit()
        self.first_name_edit.setPlaceholderText("Введите имя")
        name_layout.addWidget(self.first_name_edit)
        name_layout.addWidget(QLabel("Фамилия:"))
        self.last_name_edit = QLineEdit()
        self.last_name_edit.setPlaceholderText("Введите фамилию")
        name_layout.addWidget(self.last_name_edit)
        
        # Телефон
        phone_group = QWidget()
        phone_layout = QHBoxLayout(phone_group)
        phone_layout.addWidget(QLabel("Телефон:"))
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("+7 (XXX) XXX-XX-XX")
        phone_layout.addWidget(self.phone_edit)
        
        # Скидка
        discount_group = QWidget()
        discount_layout = QHBoxLayout(discount_group)
        discount_layout.addWidget(QLabel("Скидка (%):"))
        self.discount_spin = QSpinBox()
        self.discount_spin.setRange(0, 30)
        discount_layout.addWidget(self.discount_spin)
        
        # Кнопка добавления
        add_client_btn = QPushButton("Добавить клиента")
        add_client_btn.clicked.connect(self.add_client)
        
        # Добавляем все в форму
        form_layout.addWidget(name_group)
        form_layout.addWidget(phone_group)
        form_layout.addWidget(discount_group)
        form_layout.addWidget(add_client_btn)
        
        # Список клиентов
        clients_list_label = QLabel("Список клиентов:")
        self.clients_list = QListWidget()
        
        layout.addWidget(client_form)
        layout.addWidget(clients_list_label)
        layout.addWidget(self.clients_list)
        
    def setup_reports_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        # Статистика
        stats_label = QLabel("Статистика фотостудии")
        stats_label.setAlignment(Qt.AlignCenter)
        
        # Виджеты статистики
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        
        # Общая статистика
        total_stats = QLabel("Всего клиентов: 0\nВсего бронирований: 0\nОбщий доход: 0 руб")
        total_stats.setAlignment(Qt.AlignCenter)
        
        # График занятости (заглушка)
        schedule_label = QLabel("График занятости залов:")
        schedule_placeholder = QLabel("Здесь будет график занятости")
        schedule_placeholder.setAlignment(Qt.AlignCenter)
        schedule_placeholder.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc; min-height: 200px;")
        
        # Кнопка обновления
        refresh_btn = QPushButton("Обновить статистику")
        
        stats_layout.addWidget(total_stats)
        stats_layout.addWidget(schedule_label)
        stats_layout.addWidget(schedule_placeholder)
        stats_layout.addWidget(refresh_btn)
        
        layout.addWidget(stats_label)
        layout.addWidget(stats_widget)
        
    def apply_styles(self):
        # Основные стили
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            QLabel {
                font-size: 14px;
                color: #333;
            }
            
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
                min-width: 100px;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
            
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            
            QLineEdit, QComboBox, QDateEdit, QTimeEdit, QSpinBox, QListWidget {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
            
            QTabWidget::pane {
                border: 1px solid #ddd;
                background: white;
            }
            
            QTabBar::tab {
                background: #e0e0e0;
                padding: 8px 16px;
                border: 1px solid #ddd;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background: white;
                margin-bottom: -1px;
            }
            
            QListWidget {
                border: 1px solid #ddd;
                background: white;
                alternate-background-color: #f9f9f9;
            }
            
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #eee;
            }
            
            QListWidget::item:selected {
                background-color: #e0f7fa;
                color: black;
            }
        """)
        
        # Заголовки
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        
        for tab in self.findChildren(QLabel, "Статистика фотостудии"):
            tab.setFont(title_font)
            tab.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        
    def add_client(self):
        first_name = self.first_name_edit.text().strip()
        last_name = self.last_name_edit.text().strip()
        phone = self.phone_edit.text().strip()
        discount = self.discount_spin.value()
        
        if not first_name or not last_name or not phone:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля")
            return
            
        client = {
            "id": len(self.clients) + 1,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "discount": discount
        }
        
        self.clients.append(client)
        self.client_combo.addItem(f"{first_name} {last_name} ({phone})", client)
        self.clients_list.addItem(f"{first_name} {last_name}, тел.: {phone}, скидка: {discount}%")
        
        # Очищаем поля
        self.first_name_edit.clear()
        self.last_name_edit.clear()
        self.phone_edit.clear()
        self.discount_spin.setValue(0)
        
        QMessageBox.information(self, "Успех", "Клиент успешно добавлен")
        
    def create_booking(self):
        if self.client_combo.currentIndex() == -1:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите клиента")
            return
            
        hall_data = self.hall_combo.currentData()
        date = self.date_edit.date().toString("dd.MM.yyyy")
        time = self.time_edit.time().toString("hh:mm")
        duration = self.duration_spin.value()
        
        # Выбранное оборудование
        selected_equipment = []
        for item in self.equipment_list.selectedItems():
            eq_name = item.text().split(" (+")[0]
            for eq in self.equipment:
                if eq["name"] == eq_name:
                    selected_equipment.append(eq)
                    break
        
        # Расчет стоимости
        hall_cost = hall_data["price"] * duration
        equipment_cost = sum(eq["price"] * duration for eq in selected_equipment)
        total_cost = hall_cost + equipment_cost
        
        # Получаем данные клиента
        client_data = self.client_combo.currentData()
        if not client_data:  # Если клиент новый (введен вручную)
            client_name = self.client_combo.currentText()
            client_data = {
                "first_name": client_name.split()[0] if " " in client_name else client_name,
                "last_name": client_name.split()[1] if " " in client_name else "",
                "phone": "не указан",
                "discount": 0
            }
        
        # Создаем запись о бронировании
        booking = {
            "client": client_data,
            "hall": hall_data,
            "equipment": selected_equipment,
            "date": date,
            "time": time,
            "duration": duration,
            "total_cost": total_cost
        }
        
        self.bookings.append(booking)
        self.bookings_list.addItem(
            f"{date} {time} - {client_data['first_name']} {client_data['last_name']}, "
            f"Зал {hall_data['number']}, {duration} ч., {total_cost} руб"
        )
        
        QMessageBox.information(self, "Успех", "Бронирование успешно создано")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PhotoStudioApp()
    window.show()
    sys.exit(app.exec_())
