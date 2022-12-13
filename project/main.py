from telebot import custom_filters
from bot import bot
import handlers

bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.infinity_polling(skip_pending=True)
