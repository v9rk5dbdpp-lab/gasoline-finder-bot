from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards import main_menu_keyboard
from database import get_user_subscriptions, deactivate_subscription
import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message):
    welcome_text = (
        "👋 <b>Добро пожаловать!</b>\n\n"
        "Бот помогает быстро находить <b>бензин</b> на АЗС и другие дефицитные товары.\n\n"
        "<b>Что умеет бот:</b>\n"
        "• Показывать, где есть бензин рядом с вами\n"
        "• Присылать уведомления о появлении топлива\n"
        "• Показывать статистику по конкретным АЗС\n"
        "• Давать премиум за полезные отчёты\n\n"
        "Выберите действие:"
    )
    await message.answer(welcome_text, reply_markup=main_menu_keyboard(), parse_mode="HTML")


@router.message(F.text == "ℹ️ Помощь")
async def help_handler(message: Message):
    help_text = (
        "📖 <b>Как пользоваться ботом</b>\n\n"
        "• <b>Добавить отчёт</b> — расскажите другим, где вы нашли товар\n"
        "• <b>Найти товар</b> — посмотрите актуальные отчёты\n"
        "• <b>Мои подписки</b> — управляйте уведомлениями\n\n"
        "Активные пользователи получают премиум бесплатно!"
    )
    await message.answer(help_text, parse_mode="HTML", reply_markup=main_menu_keyboard())


@router.message(F.text == "🔔 Мои подписки")
async def my_subscriptions_button(message: Message):
    # ... (код из предыдущей версии)
    pass  # Мы добавим полный код на следующем шаге, если нужно