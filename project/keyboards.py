import calendar
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from datetime import date, timedelta


def start() -> ReplyKeyboardMarkup:
    """
    Формирует клавиатуру для команды старт с доступными командами.
    """

    list_commands = ['/help', '/history', '/lowprice', '/highprice', '/bestdeal']

    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
    markup.add(*(KeyboardButton(command) for command in list_commands))

    return markup


def select_location(locations: list[tuple]) -> InlineKeyboardMarkup:
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


def generate_calendar_days(view_year: int = date.today().year,
                           view_month: int = date.today().month,
                           start_year: int = date.today().year,
                           start_month: int = date.today().month,
                           start_day: int = date.today().day
                           ) -> InlineKeyboardMarkup:
    """
    Генерирует клавиатуру с датами, даты раньше стартовой даты не показываются.

    :param view_year: Год для отображения.
    :param view_month: Месяц для отображения.
    :param start_year: Год от которой формируется календарь.
    :param start_month: Месяц от которой формируется календарь.
    :param start_day: День от которой формируется календарь.
    """

    EMTPY_FIELD = '0'
    WEEK_DAYS = [calendar.day_abbr[i] for i in range(7)]

    keyboard = InlineKeyboardMarkup(row_width=7)

    # Отображение месяца и год сверху.
    keyboard.add(
        InlineKeyboardButton(
            text=date(year=view_year, month=view_month, day=1).strftime('%b %Y'),
            callback_data=EMTPY_FIELD
        )
    )
    # Сокращенные дни недели сверху.
    keyboard.add(*[InlineKeyboardButton(text=day, callback_data=EMTPY_FIELD) for day in WEEK_DAYS])

    # Добавляем даты.
    for week in calendar.Calendar().monthdayscalendar(year=view_year, month=view_month):
        week_buttons = []
        for day in week:
            day_name = ' '
            # Условия для отображения только позже стартовой даты.
            if start_year >= view_year and start_month > view_month:
                day_name = ' '
            elif day < start_day and start_year == view_year and start_month == view_month:
                day_name = ' '
            elif day != 0:
                day_name = str(day)

            week_buttons.append(InlineKeyboardButton(
                text=day_name,
                callback_data='-'.join(map(str, (day, view_month, view_year)))
                )
            )
        keyboard.add(*week_buttons)

    # Создание даты на которую пользователь может перелистнуть.
    previous_date = date(year=view_year, month=view_month, day=1) - timedelta(days=1)
    next_date = date(year=view_year, month=view_month, day=1) + timedelta(days=31)

    # Данные для передачи новой даты отображения.
    data_previous_date = (previous_date.year, previous_date.month, start_year, start_month, start_day)
    data_next_date = (next_date.year, next_date.month, start_year, start_month, start_day)

    # Кнопки для перелистывания месяцев.
    empty_button = InlineKeyboardButton(text=' ', callback_data=EMTPY_FIELD)
    left_button = InlineKeyboardButton(text='<<', callback_data='-'.join(map(str, data_previous_date)))
    right_button = InlineKeyboardButton(text='>>', callback_data='-'.join(map(str, data_next_date)))

    # Добавляем кнопки перелистывания месяцев или пустышку.
    if start_year >= view_year and start_month >= view_month:
        keyboard.add(empty_button, right_button)
    else:
        keyboard.add(left_button, right_button)
    return keyboard


def final() -> InlineKeyboardMarkup:
    """
    Формирует клавиатуру для подтверждения запроса.
    """

    markup = InlineKeyboardMarkup(row_width=2)

    markup.add(InlineKeyboardButton('Начать поиск', callback_data='search'))
    markup.add(InlineKeyboardButton('Новый запрос', callback_data='cancel'))

    return markup
