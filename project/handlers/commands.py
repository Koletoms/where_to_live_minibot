from telebot import types
from bot import bot
from bot_state import LowAndHighPrice, BestDeal
from request_api import SearchHotels, user_request
from keyboards import keyboards



@bot.message_handler(commands=['start'])
def start(message) -> None:
    """
    Функция обрабатывает команду пользователя - start.
    Выводит старто
    """

    list_commands = ['/help', '/history', '/lowprice', '/highprice', '/bestdeal']

    markup = keyboards.start(list_commands)

    bot.send_message(message.chat.id,
                     "Начнем поиск отелей\nДля получения информации о командах нажмите /help или воспользуетесь меню.",
                     reply_markup=markup)


@bot.message_handler(commands=['lowprice', 'highprice'])
def low_high_price(message):
    """
    Выбор команды на поиск отелей по максимальной или минимальной цене.
    """

    user_request.command = message.text
    user_request.state_set = LowAndHighPrice

    bot.set_state(message.from_user.id, user_request.state_set.command)

    msg = 'Где будем искать отели?'
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['bestdeal'])
def bestdeal(message):
    """
    Выбор команды на поиск наиболее подходящих по цене отелей отели.
    """
    user_request = SearchHotels()
    user_request.command = message.text
    user_request.state_set = BestDeal

    bot.set_state(message.from_user.id, user_request.state_set.command)

    msg = 'Где будем искать отели?'
    bot.send_message(message.chat.id, msg)


@bot.message_handler(state="*", commands=['cancel'])
def cancel(message):
    """
    Обновляет состояние
    """
    bot.delete_state(message.from_user.id)

