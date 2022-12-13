from telebot.handler_backends import State, StatesGroup


class LowAndHighPrice(StatesGroup):
    """
    Машина состояний для команд lowprice и highprice.
    """
    command = State()
    place = State()
    location_id = State()
    number_hotels = State()
    arrival = State()
    departure = State()
    photo = State()
    number_photo = State()
    final = State()
