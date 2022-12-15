from telebot import types
from bot import bot
from request_api import user_request
import keyboards
import re


@bot.callback_query_handler(func=lambda call: True, state=user_request.state_set.place)
def select_location_get(call: types.CallbackQuery) -> None:
    """
    Следующие действие - ввод количества отображаемых отелей.

    :param call: ответ на нажатие кнопки из функции place.
    """

    try:
        user_request.location_id = int(call.data)

        bot.set_state(call.from_user.id, user_request.state_set.location_id)

        bot.send_message(call.message.chat.id, 'Сколько отелей желаете отобразить?\nНе более 10.')

    except BaseException:
        bot.send_message(call.message.chat.id, 'Что-то пошло не так. Попробуйте еще раз')


@bot.callback_query_handler(func=lambda call: re.search(r'\d+-\d+-\d+-\d+-\d+', call.data))
def calendar_action_handler(call: types.CallbackQuery) -> None:
    """
    Меняет клавиатуру календаря.

    :param call: ответ на нажатие кнопки изменения отображения месяца из клавиатуры календаря.
    """

    new_year, new_month, start_year, start_month, start_day = map(int, call.data.split('-'))

    markup = keyboards.generate_calendar_days(view_year=new_year,
                                              view_month=new_month,
                                              start_year=start_year,
                                              start_month=start_month,
                                              start_day=start_day)

    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True, state=user_request.state_set.number_hotels)
def arrival_date_get(call: types.CallbackQuery) -> None:
    """
    Получение даты заезда.
    Следующие действие - ввод даты выезда.

    :param call: ответ на нажатие кнопки даты из клавиатуры календаря.
    """

    try:
        day, month, year = map(int, call.data.split('-'))
        user_request.arrival = day, month, year

        bot.set_state(call.from_user.id, user_request.state_set.arrival)

        markup = keyboards.generate_calendar_days(view_year=year,
                                                  view_month=month,
                                                  start_year=year,
                                                  start_month=month,
                                                  start_day=day + 1)
        msg = 'Выберете дату выезда или введите в формате dd-mm-yyyy'
        bot.send_message(call.message.chat.id, msg, reply_markup=markup)
    except BaseException:
        bot.send_message(call.message.chat.id, 'Ошибка вводе даты заезда. Введите дату в формате dd-mm-yyyy')


@bot.callback_query_handler(func=lambda call: True, state=user_request.state_set.arrival)
def departure_date_get(call: types.CallbackQuery) -> None:
    """
    Получение даты выезда.
    Следующие действие - запрос показывать ли фото.

    :param call: ответ на нажатие кнопки даты из клавиатуры календаря.
    """

    try:
        day, month, year = map(int, call.data.split('-'))
        user_request.departure = day, month, year

        bot.set_state(call.from_user.id, user_request.state_set.departure)

        markup = keyboards.photo()

        bot.send_message(call.message.chat.id, 'Желаете ли вывести фото?', reply_markup=markup)
    except BaseException:
        bot.send_message(call.message.chat.id, 'Ошибка вводе даты выезда. Введите дату в формате dd-mm-yyyy')


@bot.callback_query_handler(func=lambda call: True, state=user_request.state_set.departure)
def show_photo(call: types.CallbackQuery) -> None:
    """
    Получение запроса на показ фотографий отелей.
    Следующие действие - запрос количества фото для отображения или подтверждение запроса.

    :param call: ответ на нажатие кнопки даты из клавиатуры календаря.
    """

    try:
        match call.data:
            case 'yes':
                bot.set_state(call.from_user.id, user_request.state_set.photo)
                bot.send_message(call.message.chat.id, 'Сколько необходимо вывести фото?\nНе более 7.')
            case 'no':
                bot.set_state(call.from_user.id,  user_request.state_set.photo)
                bot.set_state(call.from_user.id, user_request.state_set.number_photo)
                markup = keyboards.final()
                msg = (f'Проверьте запрос\n'
                       f'Локация: {user_request.place}\n'
                       f'Дата заезда: {"-".join(map(str, user_request.arrival))}\n'
                       f'Дата выезда: {"-".join(map(str, user_request.departure))}\n'
                       )
                bot.send_message(call.from_user.id, msg, reply_markup=markup)

    except BaseException:
        bot.send_message(call.message.chat.id, 'Что-то не работает. Ошибка в выборе количества фото.')


@bot.callback_query_handler(func=lambda call: True, state=user_request.state_set.number_photo)
def confirmation(call: types.CallbackQuery) -> None:
    """
    Подтверждения запроса на поиск отелей.
    Следующе действие - вызов вывода запроса или обнуление запроса.

    :param call: ответ на нажатие кнопки подтверждения запроса.
    """

    try:
        match call.data:
            case 'search':
                end(call.from_user.id)
            case 'cancel':
                bot.delete_state(call.from_user.id)

    except BaseException:
        bot.send_message(call.message.chat.id, 'Что-то не работает в кнопке ответа')


def end(user_id: int) -> None:
    """
    Отправляет запрос на поиск отелей.
    Для каждого отеля находит дополнительные сведения.
    При запросе на вывод фото - дополнительно отправляет фото.
    """

    bot.send_message(user_id, 'Ищем отели...')
    user_request.find_hotels()  # Запускает запрос на поиск отелей.

    if len(user_request.hotels) == 0:
        bot.send_message(user_id, 'Ничего не найдено. Попробуйте изменить критерии поиска.')

    for number, hotel in enumerate(user_request.hotels):
        hotel.find_details()  # Запускает запрос на уточнее информации об отеле.

        if number >= user_request.number_hotels:
            break

        msg = (
            f'Отель: {hotel.name}\n'
            f'Адрес: {hotel.adress_hotel}\n'
            f'Расстояние до центра: {hotel.distance_to_center}\n'
            f'Цена за ночь/ общая: {hotel.price_day}/ {hotel.price_total}\n'
            f'https://www.hotels.com/h{hotel.id}.Hotel-Information'
        )
        bot.send_message(user_id, msg)

        if user_request.number_photo:  # Если не нужны - будет None.

            all_photo_url = hotel.photo_list[:user_request.number_photo]
            media = [types.InputMediaPhoto(photo_url) for photo_url in all_photo_url]

            bot.send_media_group(user_id, media)

    bot.delete_state(user_id)  # Обнуляет машину состояний запроса.
