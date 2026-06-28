from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="⛽ Добавить отчёт о товаре")
    builder.button(text="🔍 Найти товар")
    builder.button(text="🔔 Мои подписки")
    builder.button(text="📍 Мои отчёты")
    builder.button(text="❤️ Поддержать звёздами")
    builder.button(text="ℹ️ Помощь")
    builder.adjust(2, 2, 2)
    return builder.as_markup(resize_keyboard=True)


def category_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="⛽ Топливо / Бензин", callback_data="cat_fuel")
    builder.button(text="🛒 Продукты питания", callback_data="cat_groceries")
    builder.button(text="💊 Медикаменты", callback_data="cat_medicine")
    builder.button(text="📦 Другое", callback_data="cat_other")
    builder.adjust(1)
    return builder.as_markup()


def fuel_type_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="АИ-92", callback_data="fuel_ai92")
    builder.button(text="АИ-95", callback_data="fuel_ai95")
    builder.button(text="АИ-98", callback_data="fuel_ai98")
    builder.button(text="ДТ (Дизель)", callback_data="fuel_dt")
    builder.button(text="Свой вариант →", callback_data="fuel_custom")
    builder.adjust(3, 2)
    return builder.as_markup()


def confirm_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Опубликовать отчёт", callback_data="confirm_add")
    builder.button(text="✏️ Изменить данные", callback_data="edit_add")
    builder.button(text="❌ Отмена", callback_data="cancel_add")
    builder.adjust(1)
    return builder.as_markup()


def location_request_keyboard():
    from aiogram.utils.keyboard import ReplyKeyboardBuilder
    builder = ReplyKeyboardBuilder()
    builder.button(text="📍 Отправить моё местоположение", request_location=True)
    builder.button(text="✏️ Ввести адрес текстом")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def after_search_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура после поиска"""
    from aiogram.utils.keyboard import ReplyKeyboardBuilder
    builder = ReplyKeyboardBuilder()
    builder.button(text="🔍 Новый поиск")
    builder.button(text="🏠 В главное меню")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def search_result_keyboard(report_id: int):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="👍 Полезно", callback_data=f"vote_up_{report_id}")
    builder.button(text="👎 Неактуально", callback_data=f"vote_down_{report_id}")
    builder.button(text="🗺️ Показать на карте", callback_data=f"map_{report_id}")
    builder.button(text="📊 Статистика по АЗС", callback_data=f"stats_{report_id}")
    builder.adjust(2, 2)
    return builder.as_markup()