from abc import ABC, abstractmethod

# Абстрактный класс для всех объектов, связанных с фотосессией
class PhotographicEntity(ABC):
    """Абстрактный класс для всех объектов, связанных с фотосессией"""
    @abstractmethod
    def __str__(self):
        pass


class Client(PhotographicEntity):
    """Клиент фотостудии"""
    def __init__(self, fname, lname, phone):
        self.fname = fname
        self.lname = lname
        self.phone = phone

    def __str__(self):
        return f"{self.fname} {self.lname}, Телефон: {self.phone}"

    def validate_phone(self):
        """Метод для проверки правильности телефона"""
        return len(self.phone) == 11 and self.phone.isdigit()

    def update_phone(self, new_phone):
        """Метод для обновления номера телефона клиента"""
        self.phone = new_phone
        print(f"Номер телефона для {self.fname} {self.lname} обновлен.")


class Hall(PhotographicEntity):
    """Зал для фотосессии"""
    def __init__(self, number, price):
        self.number = number
        self.price = price

    def __str__(self):
        return f"Зал {self.number}, Цена: {self.price} руб/час"

    def __add__(self, other):
        """Перегрузка оператора сложения для увеличения цены"""
        if isinstance(other, Hall):
            return Hall(self.number, self.price + other.price)
        return self

    def __eq__(self, other):
        """Перегрузка оператора сравнения для проверки одинаковости залов"""
        return self.number == other.number and self.price == other.price


class Equipment(PhotographicEntity):
    """Оборудование для съемки"""
    def __init__(self, lighting, backdrop, props):
        self.lighting = lighting
        self.backdrop = backdrop
        self.props = props

    def __str__(self):
        return f"Свет: {self.lighting}, Фон: {self.backdrop}, Реквизит: {self.props}"


class Booking:
    """Бронирование фотостудии"""
    def __init__(self, client, hall, equipment, date, time, duration):
        if not isinstance(client, Client):
            raise ValueError("Некорректный клиент!")
        if not isinstance(hall, Hall):
            raise ValueError("Некорректный зал!")
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
    total_bookings = 0  # Статическое поле для хранения общего числа бронирований

    def __init__(self):
        self.bookings_by_date = {}

    @staticmethod
    def get_total_bookings():
        return Studio.total_bookings  # Статический метод для получения числа бронирований

    def add_booking(self, booking):
        if booking.date not in self.bookings_by_date:
            self.bookings_by_date[booking.date] = []
        self.bookings_by_date[booking.date].append(booking)
        Studio.total_bookings += 1  # Увеличиваем счетчик бронирований
        print("Бронирование успешно добавлено!")

    def cancel_booking(self, client_name):
        self.bookings_by_date = {date: [b for b in bookings if b.client.fname != client_name] 
                                 for date, bookings in self.bookings_by_date.items()}
        Studio.total_bookings -= 1  # Уменьшаем счетчик бронирований
        print(f"Бронирование клиента {client_name} удалено.")

    def show_bookings(self):
        if not self.bookings_by_date:
            print("Нет активных бронирований.")
        else:
            for date, bookings in self.bookings_by_date.items():
                print(f"Дата: {date}")
                for booking in bookings:
                    print(booking, "\n")


# Пример работы системы
if __name__ == "__main__":
    # Создание объектов
    client1 = Client("Анна", "Иванова", "89001234567")
    hall1 = Hall(1, 2000)
    equipment1 = Equipment("Профессиональный свет", "Белый фон", "Стул, цветы")

    studio = Studio()

    # Добавление бронирования
    booking1 = Booking(client1, hall1, equipment1, "10.02.2025", "15:00", 2)
    studio.add_booking(booking1)

    # Показываем все бронирования
    studio.show_bookings()

    # Удаление бронирования
    studio.cancel_booking("Анна")
    studio.show_bookings()

    # Проверка статического метода
    print(f"Общее количество бронирований: {Studio.get_total_bookings()}")
    
    # Перегрузка операторов
    hall2 = Hall(2, 1500)
    hall3 = hall1 + hall2  # Сложение цен
    print(hall3)  # Зал 1, Цена: 3500 руб/час
    print(hall1 == hall2)  # False

    # Обновление номера телефона
    client1.update_phone("89005556678")
    print(client1)
