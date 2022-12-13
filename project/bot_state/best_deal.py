from telebot.handler_backends import State, StatesGroup

# дописать
class BestDeal(StatesGroup):
    """
    Машина состояний для команды bestdeal.
    """
    command = State()
    place = State()
    number_hotels = State()
    max_price = State()
    min_price = State()
    arrival = State()
    departure = State()
    distance = State()
    foto = State()
