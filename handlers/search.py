from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from keyboards import after_search_keyboard, search_result_keyboard, main_menu_keyboard
from database import (
    search_reports, vote_report, get_report_by_id, 
    add_subscription, get_user_subscriptions, deactivate_subscription
)
import aiosqlite
from config import DB_PATH
import logging
from datetime import datetime

router = Router()
logger = logging.getLogger(__name__)


class SearchStates(StatesGroup):
    waiting_item = State()
    waiting_region = State()
    waiting_location_for_radius = State()


@router.message(F.text == "🔍 Найти товар")
async def start_search(message: Message, state: FSMContext):
    await state.set_state(SearchStates.waiting_item)
    await message.answer(
        "🔍 Напишите название товара, который ищете:\n"
        "Например: Бензин АИ-95, Молоко, Парацетамол"
    )


@router.message(StateFilter(SearchStates.waiting_item))
async def process_search_item(message: Message, state: FSMContext):
    item_query = message.text.strip()
    if len(item_query) < 2:
        await message.answer("Слишком короткий запрос. Напишите название товара:")
        return
    
    await state.update_data(item_query=item_query)
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="🗺️ Указать регион", callback_data="search_by_region")
    builder.button(text="📍 Искать рядом со мной (радиус 50 км)", callback_data="search_near_me")
    builder.adjust(1)
    
    await message.answer(
        f"Ищем: <b>{item_query}</b>\n\nВыберите тип поиска:",
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data == "search_by_region", StateFilter(SearchStates.waiting_item))
async def choose_region_search(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SearchStates.waiting_region)
    await callback.message.edit_text("Укажите регион (город или область):")
    await callback.answer()


@router.callback_query(F.data == "search_near_me", StateFilter(SearchStates.waiting_item))
async def choose_radius_search(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    # Проверка премиума (упрощённая)
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT is_premium, premium_until FROM users WHERE user_id = ?", 
            (user_id,)
        )
        row = await cursor.fetchone()
    
    has_premium = False
    if row:
        is_prem, until = row
        if is_prem and until:
            try:
                if datetime.fromisoformat(until) > datetime.now():
                    has_premium = True
            except:
                pass
    
    if not has_premium:
        await callback.answer(
            "🔒 Поиск в радиусе доступен только премиум-пользователям.\n"
            "Добавляйте отчёты и получайте премиум бесплатно!",
            show_alert=True
        )
        return
    
    await state.set_state(SearchStates.waiting_location_for_radius)
    await callback.message.edit_text(
        "📍 Отправьте своё местоположение для поиска в радиусе 50 км."
    )
    await callback.answer()


@router.message(StateFilter(SearchStates.waiting_region))
async def process_search_region(message: Message, state: FSMContext):
    # ... (логика поиска по региону)
    # Для brevity здесь оставлена сокращённая версия.
    # Полную версию можно добавить позже.
    await message.answer("Поиск по региону (функция в разработке)")
    await state.clear()


@router.message(StateFilter(SearchStates.waiting_location_for_radius), F.location)
async def process_radius_search(message: Message, state: FSMContext):
    # ... (логика радиусного поиска)
    await message.answer("Радиусный поиск (функция в разработке)")
    await state.clear()


@router.callback_query(F.data.startswith("stats_"))
async def handle_station_stats(callback: CallbackQuery):
    # ... (логика статистики по АЗС)
    await callback.answer("Статистика по АЗС (в разработке)")