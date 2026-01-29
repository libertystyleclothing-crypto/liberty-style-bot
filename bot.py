import asyncio
import aiosqlite
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# Налаштування логів (ти побачиш це в Railway Console)
logging.basicConfig(level=logging.INFO)

TOKEN = "8586203068:AAHt8DeBVyOjQlKanMC1p3iNIbUzqro1bEI"
ADMINS = [843027482]
MANAGER_URL = "https://t.me/fuckoffaz"
CARD = "4874 0700 7049 2978"

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def init_db():
    async with aiosqlite.connect("liberty.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")
        await db.commit()

# --- КЛАВІАТУРИ ---
def main_kb():
    kb = [
        [InlineKeyboardButton(text="🛍 Каталог", callback_query_data="catalog")],
        [InlineKeyboardButton(text="📏 Таблиця розмірів", callback_query_data="sizes")],
        [InlineKeyboardButton(text="💳 Підтримати автора", callback_query_data="donate")],
        [InlineKeyboardButton(text="📱 Зв'язок з менеджером", url=MANAGER_URL)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def catalog_kb():
    kb = [
        [InlineKeyboardButton(text="Худі Liberty (1200 грн)", callback_query_data="buy_hoodie")],
        [InlineKeyboardButton(text="Футболка Style (600 грн)", callback_query_data="buy_tshirt")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_query_data="start_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def pay_kb():
    kb = [
        [InlineKeyboardButton(text="📥 Надіслати чек", url=MANAGER_URL)],
        [InlineKeyboardButton(text="⬅️ Назад", callback_query_data="start_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# --- ОБРОБНИКИ ---

@dp.message(Command("start"))
async def start_cmd(m: types.Message):
    print(f"DEBUG: Отримано /start від {m.from_user.id}") # Це з'явиться в логах
    async with aiosqlite.connect("liberty.db") as db:
        await db.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (m.from_user.id,))
        await db.commit()
    await m.answer("👋 Вітаємо в Liberty Style! Оберіть пункт меню:", reply_markup=main_kb())

@dp.callback_query(F.data == "start_back")
async def back_to_menu(c: types.CallbackQuery):
    await c.message.edit_text("Головне меню:", reply_markup=main_kb())

@dp.callback_query(F.data == "catalog")
async def show_catalog(c: types.CallbackQuery):
    await c.message.edit_text("🔥 Наш асортимент:", reply_markup=catalog_kb())

@dp.callback_query(F.data == "sizes")
async def show_sizes(c: types.CallbackQuery):
    await c.message.edit_text("📏 Розміри: S, M, L, XL.", reply_markup=main_kb())

@dp.callback_query(F.data.startswith("buy_"))
async def process_buy(c: types.CallbackQuery):
    await c.message.answer(f"💳 Карта для оплати:\n`{CARD}`", reply_markup=pay_kb(), parse_mode="Markdown")
    await c.answer()

@dp.callback_query(F.data == "donate")
async def process_donate(c: types.CallbackQuery):
    await c.message.answer(f"🙏 Дякуємо! Карта: `{CARD}`")
    await c.answer()

# --- АДМІНКА ---
@dp.message(Command("admin"))
async def admin_panel(m: types.Message):
    if m.from_user.id in ADMINS:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📢 Розсилка", callback_query_data="broadcast")]])
        await m.answer("🛠 Адмін-панель:", reply_markup=kb)

@dp.callback_query(F.data == "broadcast")
async def ask_broadcast(c: types.CallbackQuery):
    await c.message.answer("Напишіть текст для розсилки:")
    await c.answer()

@dp.message(lambda m: m.from_user.id in ADMINS and not m.text.startswith("/"))
async def send_broadcast(m: types.Message):
    async with aiosqlite.connect("liberty.db") as db:
        cursor = await db.execute("SELECT id FROM users")
        rows = await cursor.fetchall()
        for r in rows:
            try: await bot.send_message(r[0], m.text)
            except: pass
    await m.answer("✅ Розсилку відправлено!")

async def main():
    await init_db()
    # Видаляємо старі вебхуки, щоб бот точно почав читати повідомлення
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
