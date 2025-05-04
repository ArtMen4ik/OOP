import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Callable

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


class PhotographicEntity(ABC):
    """Абстрактный класс для сущностей фотостудии"""
    
    @abstractmethod
    def get_info(self) -> str:
        """Абстрактный метод для получения информации об объекте"""
        pass

    @abstractmethod
    def calculate_cost(self, hours: int) -> float:
        """Абстрактный метод для расчета стоимости"""
        pass

    def __str__(self):
        return self.get_info()


# ==================== Классы сущностей с полиморфизмом ====================
class Person(PhotographicEntity):
    """Базовый класс для персон"""
    def __init__(self, fname: str, lname: str):
        self._fname = fname
        self._lname = lname
        logger.info(f"Создан объект Person: {fname} {lname}")
        
    def get_info(self) -> str:
        return f"{self._fname} {self._lname}"
        
    def calculate_cost(self, hours: int) -> float:
        return 0  # Базовая персона не имеет стоимости


class Client(Person):
    """Клиент фотостудии"""
    def __init__(self, fname: str, lname: str, phone: str):
        super().__init__(fname, lname)
        self.phone = phone
        self._discount = 0
        logger.info(f"Создан клиент: {fname} {lname}, телефон: {phone}")
        
    def get_info(self) -> str:
        return f"Клиент: {super().get_info()}, Телефон: {self.phone}"
        
    def calculate_cost(self, hours: int) -> float:
        """Полиморфный метод - клиент может иметь стоимость (депозит)"""
        return 1000 * hours  # Пример: депозит


class Hall(PhotographicEntity):
    """Зал для фотосессии"""
    def __init__(self, number: int, price: float, capacity: int):
        self.number = number
        self.price = price
        self.capacity = capacity
        logger.info(f"Создан зал №{number}, цена: {price}, вместимость: {capacity}")

    def get_info(self) -> str:
        return f"Зал {self.number}, Цена: {self.price} руб/час, Вместимость: {self.capacity} чел."
    
    def calculate_cost(self, hours: int) -> float:
        """Полиморфный метод - расчет стоимости аренды зала"""
        return self.price * hours


class Equipment(PhotographicEntity):
    """Оборудование для съемки"""
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price
        logger.info(f"Создано оборудование: {name}, цена: {price}")

    def get_info(self) -> str:
        return f"Оборудование: {self.name}, Цена: {self.price} руб/час"
    
    def calculate_cost(self, hours: int) -> float:
        """Полиморфный метод - расчет стоимости аренды оборудования"""
        return self.price * hours


# ==================== Класс бронирования с лямбда-функциями ====================
class Booking:
    """Бронирование фотостудии"""
    def __init__(self, client: Client, hall: Hall, equipment: List[Equipment], date: str, time: str, duration: int):
        self.client = client
        self.hall = hall
        self.equipment = equipment
        self.date = date
        self.time = time
        self.duration = duration
        logger.info(f"Создано бронирование для {client.get_info()} на {date} {time}")

    def calculate_total_cost(self) -> float:
        """Расчет общей стоимости с использованием лямбда-функций"""
        hall_cost = self.hall.calculate_cost(self.duration)
        
        # Лямбда для расчета стоимости оборудования
        equipment_cost = sum(map(lambda e: e.calculate_cost(self.duration), self.equipment))
        
        # Лямбда для применения скидки клиента
        apply_discount = lambda cost, discount: cost * (1 - discount/100)
        
        total = hall_cost + equipment_cost
        return apply_discount(total, self.client._discount)

    def __str__(self):
        equipment_info = "\n".join([f"  - {eq.get_info()}" for eq in self.equipment])
        return (f"Бронирование:\n"
                f"Клиент: {self.client.get_info()}\n"
                f"Зал: {self.hall.get_info()}\n"
                f"Оборудование:\n{equipment_info}\n"
                f"Дата: {self.date}, Время: {self.time}, Длительность: {self.duration} ч\n"
                f"Общая стоимость: {self.calculate_total_cost():.2f} руб")


# ==================== Класс студии с обработкой коллекций ====================
class Studio:
    """Фотостудия для управления бронированиями"""
    def __init__(self):
        self.bookings: List[Booking] = []
        self._halls: List[Hall] = [
            Hall(1, 2000, 5),
            Hall(2, 3000, 10),
            Hall(3, 2500, 8)
        ]
        self._equipment: List[Equipment] = [
            Equipment("Профессиональный свет", 500),
            Equipment("Фон белый", 300),
            Equipment("Фон черный", 300),
            Equipment("Реквизит", 200)
        ]
        logger.info("Фотостудия инициализирована")

    def add_booking(self, booking: Booking) -> bool:
        """Добавление бронирования"""
        # Лямбда для проверки доступности зала
        is_hall_available = lambda: not any(
            b for b in self.bookings 
            if b.hall == booking.hall and b.date == booking.date and b.time == booking.time
        )
        
        if is_hall_available():
            self.bookings.append(booking)
            logger.info(f"Бронирование добавлено: {booking}")
            return True
        else:
            logger.warning(f"Зал {booking.hall.number} уже занят на {booking.date} {booking.time}")
            return False

    def filter_bookings(self, filter_func: Callable[[Booking], bool]) -> List[Booking]:
        """Фильтрация бронирований с помощью лямбда-функции"""
        return list(filter(filter_func, self.bookings))

    def sort_bookings(self, key_func: Callable[[Booking], any]) -> List[Booking]:
        """Сортировка бронирований с помощью лямбда-функции"""
        return sorted(self.bookings, key=key_func)

    def get_available_halls(self, date: str, time: str) -> List[Hall]:
        """Получение доступных залов"""
        # Лямбда для проверки занятости зала
        is_hall_booked = lambda hall: any(
            b for b in self.bookings 
            if b.hall == hall and b.date == date and b.time == time
        )
        
        return [hall for hall in self._halls if not is_hall_booked(hall)]

    def get_equipment_by_filter(self, filter_func: Callable[[Equipment], bool]) -> List[Equipment]:
        """Получение оборудования по фильтру"""
        return list(filter(filter_func, self._equipment))


# ==================== Пример использования ====================
if __name__ == "__main__":
    try:
        # Создание объектов
        client1 = Client("Анна", "Иванова", "79001234567")
        client2 = Client("Иван", "Петров", "79007654321")
        
        # Применение скидки
        client1.apply_discount(10)
        
        # Создание студии
        studio = Studio()
        
        # Получение доступных залов
        date = "2023-12-15"
        time = "15:00"
        available_halls = studio.get_available_halls(date, time)
        print("Доступные залы:")
        for hall in available_halls:
            print(f" - {hall.get_info()}")
        
        # Создание бронирования
        hall = available_halls[0]
        equipment = studio.get_equipment_by_filter(lambda e: "свет" in e.name or "фон" in e.name)
        booking1 = Booking(client1, hall, equipment, date, time, 3)
        
        # Добавление бронирования
        if studio.add_booking(booking1):
            print("\nБронирование успешно создано:")
            print(booking1)
        
        # Попытка создать конфликтующее бронирование
        booking2 = Booking(client2, hall, equipment, date, time, 2)
        if not studio.add_booking(booking2):
            print("\nОшибка: Зал уже занят в это время")
        
        # Фильтрация бронирований с помощью лямбда-функции
        print("\nБронирования Анны Ивановой:")
        annas_bookings = studio.filter_bookings(lambda b: b.client._fname == "Анна")
        for b in annas_bookings:
            print(b)
        
        # Сортировка бронирований по стоимости (лямбда-функция)
        print("\nВсе бронирования, отсортированные по стоимости:")
        sorted_bookings = studio.sort_bookings(lambda b: b.calculate_total_cost())
        for b in sorted_bookings:
            print(f"Стоимость: {b.calculate_total_cost():.2f} руб. - {b.client.get_info()}")
        
        # Демонстрация полиморфизма
        print("\nДемонстрация полиморфизма:")
        entities: List[PhotographicEntity] = [client1, hall, equipment[0]]
        for entity in entities:
            print(f"{entity.get_info()} - стоимость за 2 часа: {entity.calculate_cost(2):.2f} руб.")
            
    except Exception as e:
        logger.critical(f"Критическая ошибка: {str(e)}", exc_ientities nfo=True)
        print(f"Произошла ошибка: {e}")