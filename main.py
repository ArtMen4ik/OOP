from abc import ABC, abstractmethod
from collections import defaultdict

class PhotographicEntity(ABC):
    """Абстрактный класс для сущностей фотостудии"""
    
    @abstractmethod
    def get_info(self):
        """Абстрактный метод для получения информации об объекте"""
        pass

    def __str__(self):
        return self.get_info()


class Client(PhotographicEntity):
    """Клиент фотостудии"""
    
    def __init__(self, fname, lname, phone):
        self.fname = fname
        self.lname = lname
        self.phone = phone

    def get_info(self):
        return f"{self.fname} {self.lname}, Телефон: {self.phone}"

    def validate_phone(self):
        """Пример обработки строк: валидация номера телефона"""
        return self.phone.isdigit() and len(self.phone) == 11

    def update_phone(self, new_phone):
        """Метод для обновления номера телефона"""
        if new_phone.isdigit() and len(new_phone) == 11:
            self.phone = new_phone
            print("Телефон успешно обновлен.")
        else:
            print("Ошибка: Неверный формат номера.")


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


class Studio:
    """Фотостудия для управления бронированиями"""
    
    total_bookings = 0  # Статическое поле для отслеживания всех бронирований

    def __init__(self):
        self.bookings_by_date = defaultdict(list)  # Использование динамической структуры данных

    def add_booking(self, booking):
        """Добавление бронирования"""
        self.bookings_by_date[booking.date].append(booking)
        Studio.total_bookings += 1
        print("Бронирование успешно добавлено!")

    def cancel_booking(self, client_name):
        """Отмена бронирования по имени клиента"""
        for date, bookings in self.bookings_by_date.items():
            self.bookings_by_date[date] = [b for b in bookings if b.client.fname != client_name]

        print(f"Бронирование клиента {client_name} удалено.")

    def show_bookings(self):
        """Вывод всех бронирований"""
        if not self.bookings_by_date:
            print("Нет активных бронирований.")
        else:
            for date, bookings in self.bookings_by_date.items():
                print(f"Дата: {date}")
                for booking in bookings:
                    print(booking, "\n")

    @staticmethod
    def get_total_bookings():
        """Статический метод для получения общего числа бронирований"""
        return Studio.total_bookings


# Пример работы системы
if __name__ == "__main__":
    client1 = Client("Анна", "Иванова", "89001234567")
    hall1 = Hall(1, 2000)
    equipment1 = Equipment("Профессиональный свет", "Белый фон", "Стул, цветы")

    studio = Studio()

    booking1 = Booking(client1, hall1, equipment1, "10.02.2025", "15:00", 2)
    studio.add_booking(booking1)

    studio.show_bookings()

    print(f"Всего бронирований: {Studio.get_total_bookings()}")

    studio.cancel_booking("Анна")
    studio.show_bookings()

    print(f"Всего бронирований: {Studio.get_total_bookings()}")
