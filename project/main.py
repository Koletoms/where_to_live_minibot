from telebot import custom_filters
from bot import bot
import handlers

if __name__ == '__main__':
	bot.add_custom_filter(custom_filters.StateFilter(bot))
	bot.infinity_polling(skip_pending=True)
