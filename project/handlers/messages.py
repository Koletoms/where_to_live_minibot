from bot import bot
from request_api import user_request
from keyboards import keyboards


@bot.message_handler(state=user_request.state_set.command)
def place(message):
    """
    Получение названий подходящих мест.
    Следующие действие - уточнение локации.
    """

    try:
        # if not isinstance(str, message.text):
        #     raise ValueError

        user_request.place = message.text
        user_request.find_locations()

        if len(user_request.locations) == 0:
            raise NameError

        bot.set_state(message.from_user.id, user_request.state_set.place)

        markup = keyboards.select_location(user_request.locations)
        bot.send_message(message.chat.id, 'Уточнение место', reply_markup=markup)

    except NameError:
        bot.send_message(message.chat.id, 'Место не найдено. Уточните название места')
    except ValueError:
        bot.send_message(message.chat.id, 'Не могу разобраться что это. Напишите пожалуйста название места.')


@bot.message_handler(state=user_request.state_set.location_id)
def number_hotels_get(message) -> None:
    """
    Получение количества отображаемых отелей.
    Следующие действие - ввод даты заезда.
    """
    try:
        number = int(message.text)

        if number <= 0:
            raise ValueError
        if number > 10:
            number = 10
        user_request.number_hotels = number

        bot.set_state(message.from_user.id, user_request.state_set.number_hotels)
        bot.send_message(message.chat.id, 'Выберете дату заезда в формате dd-mm-yyyy')

    except TypeError:
        bot.send_message(message.chat.id, 'Необходимо ввести число.')
    except ValueError:
        bot.send_message(message.chat.id, 'Выберете количество отелей от 1 до 10.')


@bot.message_handler(state=user_request.state_set.number_hotels)
def arrival_date_get(message):
    """
    Получение даты заезда.
    Следующие действие - ввод даты выезда.
    """
    try:
        user_request.arrival = map(int, message.text.split('-'))

        bot.set_state(message.from_user.id, user_request.state_set.arrival)
        bot.send_message(message.chat.id, 'Выберете дату выезда в формате dd-mm-yyyy')

    except BaseException:
        bot.send_message(message.chat.id, 'Я не понимаю. Введите дату в формате dd-mm-yyyy')


@bot.message_handler(state=user_request.state_set.arrival)
def departure_date_get(message):
    """
    Получение даты выезда.
    Следующие действие - запрос показывать ли фото.
    """
    try:
        # кнопка от календаря

        markup = keyboards.photo()

        user_request.departure = map(int, message.text.split('-'))

        bot.set_state(message.from_user.id, user_request.state_set.departure)

        bot.send_message(message.chat.id, 'Желаете ли вывести фото?', reply_markup=markup)

    except BaseException:
        bot.send_message(message.chat.id, 'Я не понимаю. Введите дату в формате dd-mm-yyyy')


@bot.message_handler(state=user_request.state_set.photo)
def number_photo_get(message):
    """
    Получение количества отображаемых фотографий для каждого отеля.
    Следующие действие - подтверждение запроса.
    """
    try:
        number = int(message.text)

        if number <= 0:
            raise ValueError
        if number > 7:
            number = 7
        user_request.number_photo = number

        bot.set_state(message.from_user.id, user_request.state_set.number_photo)

        markup = keyboards.final()
        bot.send_message(message.from_user.id, 'Проверьте запрос', reply_markup=markup)

    except TypeError:
        bot.send_message(message.chat.id, 'Необходимо ввести число.')
    except ValueError:
        bot.send_message(message.chat.id, 'Выберете количество отелей от 1 до 7.')


@bot.message_handler()
def unknown_message(message) -> None:
    """
    Функция обрабатывает все неизвестные сообщения.
    """

    bot.send_message(message.chat.id, 'Если бы мы знали что это такое, мы не знаем что это такое.')
