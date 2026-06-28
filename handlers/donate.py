from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, SuccessfulPayment
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import save_donation
from config import ADMIN_IDS
import logging

logger = logging.getLogger(__name__)
router = Router()

DONATION_OPTIONS = [
    (50, "50 ⭐ — Кофе разработчику"),
    (100, "100 ⭐ — Поддержка сервера"),
    (250, "250 ⭐ — Большое спасибо!"),
    (500, "500 ⭐ — Герой сообщества"),
]


@router.message(F.text == "❤️ Поддержать звёздами")
async def donate_start(message: Message):
    builder = InlineKeyboardBuilder()
    for amount, label in DONATION_OPTIONS:
        builder.button(text=label, callback_data=f"donate_{amount}")
    builder.adjust(1)
    
    text = (
        "❤️ <b>Поддержать проект</b>\n\n"
        "Бот бесплатный и существует благодаря вашей поддержке.\n"
        "Выберите сумму пожертвования:"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("donate_"))
async def process_donate(callback: CallbackQuery, bot: Bot):
    amount = int(callback.data.split("_")[1])
    
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Поддержка бота «Наличие товаров»",
        description=f"Спасибо за поддержку проекта!",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Пожертвование", amount=amount)],
        payload=f"donation_{amount}",
    )
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    payment = message.successful_payment
    amount = payment.total_amount
    
    try:
        await save_donation(
            user_id=message.from_user.id,
            username=message.from_user.username,
            amount=amount
        )
    except Exception as e:
        logger.error(f"Ошибка сохранения доната: {e}")

    await message.answer(
        f"🎉 Спасибо! Вы пожертвовали <b>{amount} ⭐</b>.\n"
        "Это очень помогает развитию проекта!"
    )