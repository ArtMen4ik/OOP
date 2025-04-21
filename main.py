from abc import ABC, abstractmethod
from collections import defaultdict

# ==================== Задание 1: Обработка исключений ====================
class StudioBaseError(Exception):
    """Базовое исключение для фотостудии"""
    pass

class ClientError(StudioBaseError):
    """Ошибка, связанная с клиентом"""
    pass

class ClientNotFoundError(ClientError):
    """Клиент не найден"""
    pass

class BookingError(StudioBaseError):
    """Ошибка бронирования"""
    pass

class HallNotAvailableError(BookingError):
    """Зал недоступен"""
    pass

# ==================== Базовые классы ====================
class PhotographicEntity(ABC):
    """Абстрактный класс для сущностей фотостудии"""
    
    @abstractmethod
    def get_info(self):
        """Абстрактный метод для получения информации об объекте"""
        pass

    def __str__(self):
        return self.get_info()

    def __repr__(self):
        """Задание 6: Строковое представление для воссоздания объекта"""
        attrs = ", ".join(f"{k}={repr(v)}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"


# ==================== Задание 3: Наследование ====================
class Person(PhotographicEntity):
    """Базовый класс для персон"""
    def __init__(self, fname, lname):
        self._fname = fname  # Задание 4: Защищенный атрибут
        self._lname = lname
        
    def get_info(self):
        return f"{self._fname} {self._lname}"
        
    def greet(self):
        return f"Привет, я {self._fname}!"


class Client(Person):
    """Клиент фотостудии (производный класс от Person)"""
    
    def __init__(self, fname, lname, phone):
        super().__init__(fname, lname)  # Задание 5: Вызов конструктора базового класса
        self.phone = phone
        self._discount = 0  # Задание 4: Защищенный атрибут

    # Переопределение метода базового класса
    def get_info(self):
        return f"{super().get_info()}, Телефон: {self.phone}"
        
    # Задание 3: Метод, использующий и базовый, и переопределенный методы
    def full_greeting(self, is_vip=False):
        if is_vip:
            return f"{super().greet()} Я VIP-клиент! Мой телефон: {self.phone}"
        else:
            return f"{self.get_info()} - обычный клиент"

    def validate_phone(self):
        """Пример обработки строк: валидация номера телефона"""
        try:
            if not (self.phone.isdigit() and len(self.phone) == 11):
                raise ValueError("Номер телефона должен содержать 11 цифр")
            return True
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
            return False
        finally:
            print("Проверка телефона завершена")

    def update_phone(self, new_phone):
        """Метод для обновления номера телефона"""
        try:
            if not new_phone.isdigit():
                raise ValueError("Номер должен содержать только цифры")
            if len(new_phone) != 11:
                raise ValueError("Номер должен содержать 11 цифр")
                
            self.phone = new_phone
            print("Телефон успешно обновлен.")
        except ValueError as e:
            print(f"Ошибка обновления: {e}")

    # Задание 4: Доступ к защищенному атрибуту в производном классе
    def apply_discount(self, amount):
        if 0 <= amount <= 30:
            self._discount = amount
            print(f"Скидка {amount}% применена")
        else:
            print("Недопустимый размер скидки")


class Hall(PhotographicEntity):
    """Зал для фотосессии"""
    
    def __init__(self, number, price):
        self.number = number
        self.price = price

    def get_info(self):
        return f"Зал {self.number}, Цена: {self.price} руб/час"

    def __add__(self, other):
        """Перегрузка оператора сложения для увеличения цены"""
        if isinstance(other, Hall):
            return Hall(self.number, self.price + other.price)
        return self

    def __eq__(self, other):
        """Перегрузка оператора сравнения залов"""
        return self.number == other.number and self.price == other.price


class Equipment(PhotographicEntity):
    """Оборудование для съемки"""
    
    def __init__(self, lighting, backdrop, props):
        self.lighting = lighting
        self.backdrop = backdrop
        self.props = props

    def get_info(self):
        return f"Свет: {self.lighting}, Фон: {self.backdrop}, Реквизит: {self.props}"


class Booking:
    """Бронирование фотостудии"""
    
    def __init__(self, client, hall, equipment, date, time, duration):
        self.client = client
        self.hall = hall
        self.equipment = equipment
        self.date = date
        self.time = time
        self.duration = duration

    def __str__(self):
        return (f"Бронирование: {self.client}\nЗал: {self.hall}\n"
                f"Оборудование: {self.equipment}\nДата: {self.date}, Время: {self.time}, Длительность: {self.duration} ч")


# ==================== Задание 2: Работа с массивами объектов ====================
class Studio:
    """Фотостудия для управления бронированиями"""
    
    total_bookings = 0  # Статическое поле для отслеживания всех бронирований

    def __init__(self):
        self.bookings_by_date = defaultdict(list)  # Использование динамической структуры данных
        self._halls = [[Hall(1, 2000), Hall(2, 3000)], 
                      [Hall(3, 2500), Hall(4, 3500)]]  # Двумерный список залов

    def add_booking(self, booking):
        """Добавление бронирования с обработкой исключений"""
        try:
            if not booking.client.validate_phone():
                raise BookingError("Неверный формат телефона клиента")
                
            if not self._is_hall_available(booking.hall, booking.date, booking.time):
                raise HallNotAvailableError(f"Зал {booking.hall.number} уже занят в это время")
                
            self.bookings_by_date[booking.date].append(booking)
            Studio.total_bookings += 1
            print("Бронирование успешно добавлено!")
            
        except BookingError as e:
            print(f"Ошибка бронирования: {e}")
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
        finally:
            print("=" * 40)

    def _is_hall_available(self, hall, date, time):
        """Проверка доступности зала (защищенный метод)"""
        for booking in self.bookings_by_date.get(date, []):
            if booking.hall == hall and booking.time == time:
                return False
        return True

    def cancel_booking(self, client_name):
        """Отмена бронирования по имени клиента"""
        try:
            found = False
            for date, bookings in self.bookings_by_date.items():
                original_count = len(bookings)
                self.bookings_by_date[date] = [b for b in bookings if b.client._fname != client_name]
                if len(self.bookings_by_date[date]) != original_count:
                    found = True
                    Studio.total_bookings -= (original_count - len(self.bookings_by_date[date]))
            
            if not found:
                raise ClientNotFoundError(f"Клиент {client_name} не найден")
                
            print(f"Бронирование клиента {client_name} удалено.")
            
        except ClientNotFoundError as e:
            print(f"Ошибка: {e}")
        finally:
            print("Операция отмены завершена")

    def show_bookings(self):
        """Вывод всех бронирований"""
        if not self.bookings_by_date:
            print("Нет активных бронирований.")
        else:
            for date, bookings in self.bookings_by_date.items():
                print(f"Дата: {date}")
                for booking in bookings:
                    print(booking, "\n")

    # Задание 2: Метод для поиска объекта с максимальным значением атрибута в двумерном списке
    def find_max_price_hall(self):
        """Находит зал с максимальной ценой в двумерном списке"""
        try:
            if not self._halls or all(not row for row in self._halls):
                raise ValueError("Нет доступных залов")
                
            max_hall = None
            for row in self._halls:
                for hall in row:
                    if max_hall is None or hall.price > max_hall.price:
                        max_hall = hall
            return max_hall
            
        except ValueError as e:
            print(f"Ошибка: {e}")
            return None

    @staticmethod
    def get_total_bookings():
        """Статический метод для получения общего числа бронирований"""
        return Studio.total_bookings


# ==================== Пример работы системы ====================
if __name__ == "__main__":
    print("=" * 40)
    print("Демонстрация работы системы фотостудии")
    print("=" * 40)
    
    # Создание объектов
    try:
        client1 = Client("Анна", "Иванова", "89001234567")
        client2 = Client("Иван", "Петров", "неверный_номер")
        
        # Задание 6: Проверка repr
        print("\nПроверка repr:")
        print(repr(client1))  # Должно вывести строку для воссоздания объекта
        
        # Воссоздание объекта из repr
        client1_copy = eval(repr(client1))
        print(f"Воссозданный клиент: {client1_copy}")
        
    except Exception as e:
        print(f"Ошибка при создании клиентов: {e}")

    hall1 = Hall(1, 2000)
    hall2 = Hall(2, 3000)
    equipment1 = Equipment("Профессиональный свет", "Белый фон", "Стул, цветы")

    studio = Studio()

    # Демонстрация работы с массивами объектов (Задание 2)
    print("\nЗал с максимальной ценой:")
    max_hall = studio.find_max_price_hall()
    print(max_hall.get_info() if max_hall else "Нет залов")

    # Демонстрация обработки исключений (Задание 1)
    print("\nПопытка бронирования с неверным номером телефона:")
    booking_bad = Booking(client2, hall1, equipment1, "10.02.2025", "15:00", 2)
    studio.add_booking(booking_bad)

    print("\nКорректное бронирование:")
    booking1 = Booking(client1, hall1, equipment1, "10.02.2025", "15:00", 2)
    studio.add_booking(booking1)

    # Попытка повторного бронирования того же зала
    print("\nПопытка повторного бронирования зала:")
    booking2 = Booking(client1, hall1, equipment1, "10.02.2025", "15:00", 2)
    studio.add_booking(booking2)

    # Демонстрация наследования (Задание 3)
    print("\nДемонстрация наследования:")
    print(client1.full_greeting())  # Обычный клиент
    print(client1.full_greeting(is_vip=True))  # VIP клиент

    # Демонстрация работы с защищенными атрибутами (Задание 4)
    print("\nРабота с защищенными атрибутами:")
    client1.apply_discount(10)
    try:
        # Попытка доступа к защищенному атрибуту (не рекомендуется, но возможна)
        print(f"Текущая скидка: {client1._discount}%")
    except Exception as e:
        print(f"Ошибка доступа: {e}")

    # Вывод всех бронирований
    print("\nТекущие бронирования:")
    studio.show_bookings()

    # Отмена бронирования
    print("\nОтмена бронирования:")
    studio.cancel_booking("Анна")
    studio.show_bookings()

    print(f"\nВсего бронирований: {Studio.get_total_bookings()}")
