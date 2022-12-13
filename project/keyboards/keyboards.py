from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def start(list_commands):
	"""
	Формирует клавиатуру для команды старт с доступными командами.
	"""
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
	markup.add(*(types.KeyboardButton(command) for command in list_commands))

	return markup


def select_location(locations: list) -> InlineKeyboardMarkup:
	"""
	Формирует клавиатуру с названиями локаций.
	"""

	markup = InlineKeyboardMarkup(row_width=1)
	for name_place, id_location in locations:
		markup.add(InlineKeyboardButton(name_place, callback_data=id_location))
	return markup

def photo() -> InlineKeyboardMarkup:
	"""
	Формирует клавиатуру для подтверждения на показ фото.
	"""

	markup = InlineKeyboardMarkup(row_width=2)

	markup.add(InlineKeyboardButton('Да', callback_data='yes'))
	markup.add(InlineKeyboardButton('Нет', callback_data='no'))

	return markup


def final() -> InlineKeyboardMarkup:
	"""
	Формирует клавиатуру для подтверждения запроса.
	"""

	markup = InlineKeyboardMarkup(row_width=2)

	markup.add(InlineKeyboardButton('Начать поиск', callback_data='search'))
	markup.add(InlineKeyboardButton('Новый запрос', callback_data='cancel'))

	return markup
