from telebot import types
from bot import bot
from request_api import user_request
from keyboards import keyboards


@bot.callback_query_handler(func=lambda call: True, state=user_request.state_set.place)
def select_location_get(call):
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


@bot.callback_query_handler(func=lambda call: True, state=user_request.state_set.departure)
def show_photo(call) -> None:
    """
    Получение даты выезда.
    Следующие действие - запрос количества фото для отображения или подтверждение запроса.
    :param call:
    :return:
    """
    try:
        match call.data:
            case 'yes':
                bot.set_state(call.from_user.id, user_request.state_set.photo)
                bot.send_message(call.message.chat.id, 'Сколько необходимо вывести фото?\nНе более 7.')
            case 'no':
                bot.set_state(call.from_user.id,  user_request.state_set.photo)
                bot.set_state(call.from_user.id, user_request.state_set.number_hotels)
                markup = keyboards.final()
                bot.send_message(call.from_user.id, 'Проверьте запрос', reply_markup=markup)

    except BaseException:
        bot.send_message(call.message.chat.id, 'Что-то не работает')


@bot.callback_query_handler(func=lambda call: True, state=user_request.state_set.number_photo)
def confirmation(call):
    """
    Ответ на кнопку подтверждения запроса.
    Следующе действие - вызов вывода запроса или обнуление запроса.
    """
    try:
        match call.data:
            case 'search':
                end(call.from_user.id)
            case 'cancel':
                bot.delete_state(call.from_user.id)

    except BaseException:
        bot.send_message(call.message.chat.id, 'Что-то не работает')


def end(user_id):
    """
    Отправляет запрос на поиск потелей.
    Для каждого отеля находит дополнительные сведения.
    При запросе на вывод фото - дополнительно отправляет фото.
    """

    bot.send_message(user_id, 'Ищем отели...')

    user_request.find_hotels()  # Запускает запрос на поиск отелей.

    if len(user_request.hotels) == 0:
        bot.send_message(user_id, 'Ничего не найдено. Попробуйте изменить критерии поиска.')
        bot.delete_state(user_id)


    for number, hotel in enumerate(user_request.hotels):
        hotel.find_details()  # Запускает запрос на уточнее информации об отеле.

        if number >= user_request.number_hotels:
            break

        msg = (
            f'Отель: {hotel.name}\n'
            f'Адрес: {hotel.adress_hotel}\n'
            f'Расстояние до центра: {hotel.distance_to_center}\n'
            f'Цена за ночь: {hotel.price_day}\n'
            f'Цена за весь период: {hotel.price_total}\n'
            f'https://www.hotels.com/h{hotel.id}.Hotel-Information'
        )
        bot.send_message(user_id, msg)

        if user_request.number_photo:  # Если не нужны - будет None.

            all_photo_url = hotel.photo_list[:user_request.number_photo]
            media = [types.InputMediaPhoto(photo_url) for photo_url in all_photo_url]

            bot.send_media_group(user_id, media)

    bot.delete_state(user_id)  # Обнуляет машину состояний запроса.

