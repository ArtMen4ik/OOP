class Client:
    """Клиент фотостудии"""
    def __init__(self, fname, lname, phone):
        self.fname = fname
        self.lname = lname
        self.phone = phone

    def __str__(self):
        return f"{self.fname} {self.lname}, Телефон: {self.phone}"


class Hall:
    """Зал для фотосессии"""
    def __init__(self, number, price):
        self.number = number
        self.price = price

    def __str__(self):
        return f"Зал {self.number}, Цена: {self.price} руб/час"


class Equipment:
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
    def __init__(self):
        self.bookings = []

    def add_booking(self, booking):
        self.bookings.append(booking)
        print("Бронирование успешно добавлено!")

    def cancel_booking(self, client_name):
        self.bookings = [b for b in self.bookings if b.client.fname != client_name]
        print(f"Бронирование клиента {client_name} удалено.")

    def show_bookings(self):
        if not self.bookings:
            print("Нет активных бронирований.")
        else:
            for booking in self.bookings:
                print(booking, "\n")


# Пример работы системы
if __name__ == "__main__":
    client1 = Client("Анна", "Иванова", "89001234567")
    hall1 = Hall(1, 2000)
    equipment1 = Equipment("Профессиональный свет", "Белый фон", "Стул, цветы")

    studio = Studio()

    booking1 = Booking(client1, hall1, equipment1, "10.02.2025", "15:00", 2)
    studio.add_booking(booking1)

    studio.show_bookings()

    studio.cancel_booking("Анна")
    studio.show_bookings()
