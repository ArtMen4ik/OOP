import sys
import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Callable

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QListWidget, QComboBox, 
                            QDateEdit, QTimeEdit, QSpinBox, QTabWidget, QMessageBox)
from PyQt5.QtCore import QDate, QTime, Qt
from PyQt5.QtGui import QFont, QIcon

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    filename='photo_studio.log',
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger('PhotoStudio')

# ==================== Базовые классы и исключения ====================
class StudioBaseError(Exception):
    """Базовое исключение для фотостудии"""
    def __init__(self, message="Произошла ошибка в работе фотостудии"):
        self.message = message
        super().__init__(self.message)
        logger.error(f"StudioBaseError: {message}")

    def __str__(self):
        return f"Ошибка фотостудии: {self.message}"

class ClientError(StudioBaseError):
    """Ошибка, связанная с клиентом"""
    def __init__(self, client_info, message="Ошибка с клиентом"):
        self.client_info = client_info
        full_message = f"{message} (клиент: {client_info})"
        super().__init__(full_message)

class BookingError(StudioBaseError):
    """Ошибка бронирования"""
    def __init__(self, booking_details, message="Ошибка бронирования"):
        self.booking_details = booking_details
        full_message = f"{message}: {booking_details}"
        super().__init__(full_message)

class HallNotAvailableError(BookingError):
    """Зал недоступен"""
    def __init__(self, hall_number, date, time, reason=""):
        details = f"Зал {hall_number} недоступен {date} в {time}"
        if reason:
            details += f" (причина: {reason})"
        super().__init__(details, "Ошибка доступности зала")
        self.hall_number = hall_number
        self.date = date
        self.time = time

# ==================== Бизнес-логика ====================
class PhotographicEntity(ABC):
    """Абстрактный класс для сущностей фотостудии"""
    
    @abstractmethod
    def get_info(self) -> str:
        pass

    @abstractmethod
    def calculate_cost(self, hours: int) -> float:
        pass

    def __str__(self):
        return self.get_info()

class Person(PhotographicEntity):
    """Базовый класс для персон"""
    def __init__(self, fname: str, lname: str):
        self._fname = fname
        self._lname = lname
        
    def get_info(self) -> str:
        return f"{self._fname} {self._lname}"
        
    def calculate_cost(self, hours: int) -> float:
        return 0

class Client(Person):
    """Клиент фотостудии"""
    def __init__(self, fname: str, lname: str, phone: str):
        super().__init__(fname, lname)
        self.phone = phone
        self._discount = 0
        
    def get_info(self) -> str:
        return f"Клиент: {super().get_info()}, Телефон: {self.phone}"
        
    def calculate_cost(self, hours: int) -> float:
        return 1000 * hours

    def apply_discount(self, amount):
        if 0 <= amount <= 30:
            self._discount = amount
            return True
        return False

class Hall(PhotographicEntity):
    """Зал для фотосессии"""
    def __init__(self, number: int, price: float, capacity: int):
        self.number = number
        self.price = price
        self.capacity = capacity

    def get_info(self) -> str:
        return f"Зал {self.number}, Цена: {self.price} руб/час, Вместимость: {self.capacity} чел."
    
    def calculate_cost(self, hours: int) -> float:
        return self.price * hours

class Equipment(PhotographicEntity):
    """Оборудование для съемки"""
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

    def get_info(self) -> str:
        return f"Оборудование: {self.name}, Цена: {self.price} руб/час"
    
    def calculate_cost(self, hours: int) -> float:
        return self.price * hours

class Booking:
    """Бронирование фотостудии"""
    def __init__(self, client: Client, hall: Hall, equipment: List[Equipment], date: str, time: str, duration: int):
        self.client = client
        self.hall = hall
        self.equipment = equipment
        self.date = date
        self.time = time
        self.duration = duration

    def calculate_total_cost(self) -> float:
        hall_cost = self.hall.calculate_cost(self.duration)
        equipment_cost = sum(eq.calculate_cost(self.duration) for eq in self.equipment)
        total = hall_cost + equipment_cost
        return total * (1 - self.client._discount/100)

    def __str__(self):
        equipment_info = "\n".join([f"  - {eq.get_info()}" for eq in self.equipment])
        return (f"Бронирование:\n"
                f"Клиент: {self.client.get_info()}\n"
                f"Зал: {self.hall.get_info()}\n"
                f"Оборудование:\n{equipment_info}\n"
                f"Дата: {self.date}, Время: {self.time}, Длительность: {self.duration} ч\n"
                f"Общая стоимость: {self.calculate_total_cost():.2f} руб")

class Studio:
    """Фотостудия для управления бронированиями"""
    def __init__(self):
        self.bookings: List[Booking] = []
        self._halls: List[Hall] = []
        self._equipment: List[Equipment] = []
        self._clients: List[Client] = []

    def add_hall(self, hall: Hall):
        self._halls.append(hall)

    def add_equipment(self, equipment: Equipment):
        self._equipment.append(equipment)

    def add_client(self, client: Client):
        self._clients.append(client)

    def add_booking(self, booking: Booking) -> bool:
        if not self._is_hall_available(booking.hall, booking.date, booking.time):
            raise HallNotAvailableError(booking.hall.number, booking.date, booking.time)
            
        self.bookings.append(booking)
        return True

    def _is_hall_available(self, hall: Hall, date: str, time: str) -> bool:
        for booking in self.bookings:
            if booking.hall == hall and booking.date == date and booking.time == time:
                return False
        return True

    def get_clients(self) -> List[Client]:
        return self._clients

    def get_halls(self) -> List[Hall]:
        return self._halls

    def get_equipment(self) -> List[Equipment]:
        return self._equipment

# ==================== Адаптер для GUI ====================
class StudioAdapter:
    def __init__(self):
        self.studio = Studio()
        self._init_default_data()

    def _init_default_data(self):
        """Инициализация тестовых данных"""
        # Добавляем залы
        self.studio.add_hall(Hall(1, 2000, 5))
        self.studio.add_hall(Hall(2, 3000, 10))
        self.studio.add_hall(Hall(3, 2500, 8))
        
        # Добавляем оборудование
        self.studio.add_equipment(Equipment("Профессиональный свет", 500))
        self.studio.add_equipment(Equipment("Фон белый", 300))
        self.studio.add_equipment(Equipment("Фон черный", 300))
        self.studio.add_equipment(Equipment("Реквизит", 200))

    def add_client(self, first_name: str, last_name: str, phone: str, discount: int = 0) -> Client:
        client = Client(first_name, last_name, phone)
        if discount > 0:
            client.apply_discount(discount)
        self.studio.add_client(client)
        return client

    def create_booking(self, client: Client, hall: Hall, equipment: List[Equipment], 
                      date: str, time: str, duration: int) -> Booking:
        booking = Booking(client, hall, equipment, date, time, duration)
        self.studio.add_booking(booking)
        return booking

    def get_available_halls(self, date: str, time: str) -> List[Hall]:
        return [hall for hall in self.studio.get_halls() 
                if self.studio._is_hall_available(hall, date, time)]

    def get_all_equipment(self) -> List[Equipment]:
        return self.studio.get_equipment()

    def get_all_clients(self) -> List[Client]:
        return self.studio.get_clients()

    def get_client_bookings(self, client: Client) -> List[Booking]:
        return [b for b in self.studio.bookings if b.client == client]

# ==================== Графический интерфейс ====================
class PhotoStudioApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Фотостудия - Система бронирования")
        self.setWindowIcon(QIcon("camera_icon.png"))
        self.setMinimumSize(900, 600)
        
        # Инициализация адаптера бизнес-логики
        self.adapter = StudioAdapter()
        
        # Настройка интерфейса
        self.init_ui()
        self.apply_styles()
        
    def init_ui(self):
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
        
        # Боковая панель
        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        
        studio_info = QLabel("Фотостудия Light And Shadow\n\nЧасы работы:\n9:00 - 22:00\n\nКонтакты:\n+7 (123) 456-78-90")
        studio_info.setAlignment(Qt.AlignCenter)
        
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
        
        # Клиент
        client_group = QWidget()
        client_layout = QHBoxLayout(client_group)
        client_layout.addWidget(QLabel("Клиент:"))
        self.client_combo = QComboBox()
        self.client_combo.setEditable(True)
        self.client_combo.setPlaceholderText("Выберите или введите нового клиента")
        client_layout.addWidget(self.client_combo)
        
        # Зал
        hall_group = QWidget()
        hall_layout = QHBoxLayout(hall_group)
        hall_layout.addWidget(QLabel("Зал:"))
        self.hall_combo = QComboBox()
        for hall in self.adapter.studio.get_halls():
            self.hall_combo.addItem(
                f"Зал {hall.number} ({hall.price} руб/час, до {hall.capacity} чел.)",
                hall
            )
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
        for eq in self.adapter.studio.get_equipment():
            self.equipment_list.addItem(f"{eq.name} (+{eq.price} руб/час)")
        self.equipment_list.setSelectionMode(QListWidget.MultiSelection)
        equipment_layout.addWidget(self.equipment_list)
        
        # Кнопка бронирования
        book_btn = QPushButton("Забронировать")
        book_btn.clicked.connect(self.create_booking)
        
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
        
        # Заполняем список клиентов
        self.update_clients_combo()
        
    def setup_clients_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        # Форма клиента
        client_form = QWidget()
        form_layout = QVBoxLayout(client_form)
        
        # Имя
        name_group = QWidget()
        name_layout = QHBoxLayout(name_group)
        name_layout.addWidget(QLabel("Имя:"))
        self.first_name_edit = QLineEdit()
        name_layout.addWidget(self.first_name_edit)
        name_layout.addWidget(QLabel("Фамилия:"))
        self.last_name_edit = QLineEdit()
        name_layout.addWidget(self.last_name_edit)
        
        # Телефон
        phone_group = QWidget()
        phone_layout = QHBoxLayout(phone_group)
        phone_layout.addWidget(QLabel("Телефон:"))
        self.phone_edit = QLineEdit()
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
        
        # Заполняем список клиентов
        self.update_clients_list()
        
    def setup_reports_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        stats_label = QLabel("Статистика фотостудии")
        stats_label.setAlignment(Qt.AlignCenter)
        
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        
        # Статистика
        self.total_stats_label = QLabel()
        self.update_stats()
        
        # График занятости (заглушка)
        schedule_label = QLabel("График занятости залов:")
        schedule_placeholder = QLabel("Здесь будет график занятости")
        schedule_placeholder.setAlignment(Qt.AlignCenter)
        schedule_placeholder.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc; min-height: 200px;")
        
        # Кнопка обновления
        refresh_btn = QPushButton("Обновить статистику")
        refresh_btn.clicked.connect(self.update_stats)
        
        stats_layout.addWidget(self.total_stats_label)
        stats_layout.addWidget(schedule_label)
        stats_layout.addWidget(schedule_placeholder)
        stats_layout.addWidget(refresh_btn)
        
        layout.addWidget(stats_label)
        layout.addWidget(stats_widget)
        
    def apply_styles(self):
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
                border-radius: 4px;
            }
            QTabBar::tab:selected {
                background: white;
            }
            QListWidget {
                alternate-background-color: #f9f9f9;
            }
        """)
        
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        
        for label in self.findChildren(QLabel, "Статистика фотостудии"):
            label.setFont(title_font)
            label.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
    
    def update_clients_combo(self):
        self.client_combo.clear()
        for client in self.adapter.get_all_clients():
            self.client_combo.addItem(
                f"{client._fname} {client._lname} ({client.phone})",
                client
            )
    
    def update_clients_list(self):
        self.clients_list.clear()
        for client in self.adapter.get_all_clients():
            self.clients_list.addItem(
                f"{client._fname} {client._lname}, тел.: {client.phone}, скидка: {client._discount}%"
            )
    
    def update_stats(self):
        clients_count = len(self.adapter.get_all_clients())
        bookings_count = len(self.adapter.studio.bookings)
        total_income = sum(b.calculate_total_cost() for b in self.adapter.studio.bookings)
        
        self.total_stats_label.setText(
            f"Всего клиентов: {clients_count}\n"
            f"Всего бронирований: {bookings_count}\n"
            f"Общий доход: {total_income:.2f} руб"
        )
    
    def add_client(self):
        first_name = self.first_name_edit.text().strip()
        last_name = self.last_name_edit.text().strip()
        phone = self.phone_edit.text().strip()
        discount = self.discount_spin.value()
        
        if not first_name or not last_name or not phone:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля")
            return
            
        try:
            client = self.adapter.add_client(first_name, last_name, phone, discount)
            
            # Обновляем интерфейс
            self.update_clients_combo()
            self.update_clients_list()
            
            # Очищаем поля
            self.first_name_edit.clear()
            self.last_name_edit.clear()
            self.phone_edit.clear()
            self.discount_spin.setValue(0)
            
            QMessageBox.information(self, "Успех", "Клиент успешно добавлен")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить клиента: {str(e)}")
    
    def create_booking(self):
        if self.client_combo.currentIndex() == -1:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите клиента")
            return
            
        try:
            client = self.client_combo.currentData()
            hall = self.hall_combo.currentData()
            date = self.date_edit.date().toString("dd.MM.yyyy")
            time = self.time_edit.time().toString("hh:mm")
            duration = self.duration_spin.value()
            
            # Получаем выбранное оборудование
            selected_equipment = []
            for i in range(self.equipment_list.count()):
                if self.equipment_list.item(i).isSelected():
                    selected_equipment.append(self.adapter.studio.get_equipment()[i])
            
            # Создаем бронирование
            booking = self.adapter.create_booking(
                client=client,
                hall=hall,
                equipment=selected_equipment,
                date=date,
                time=time,
                duration=duration
            )
            
            # Добавляем в список
            self.bookings_list.addItem(
                f"{date} {time} - {client._fname} {client._lname}, "
                f"Зал {hall.number}, {duration} ч., {booking.calculate_total_cost():.2f} руб"
            )
            
            # Обновляем статистику
            self.update_stats()
            
            QMessageBox.information(self, "Успех", "Бронирование успешно создано")
            
        except HallNotAvailableError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать бронирование: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PhotoStudioApp()
    window.show()
    sys.exit(app.exec_())