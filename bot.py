import os
import asyncio
import aiosqlite
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# Railway бере ці дані з розділу Variables
TOKEN = os.getenv("8586203068:AAHt8DeBVyOjQlKanMC1p3iNIbUzqro1bEI")
# Перетворюємо рядок "ID1,ID2" у список чисел
ADMINS_STR = os.getenv("843027482")
ADMINS = [int(i.strip()) for i in ADMINS_STR.split(",") if i.strip()]

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
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Каталог", callback_query_data="catalog")],
        [InlineKeyboardButton(text="📏 Таблиця розмірів", callback_query_data="sizes")],
        [InlineKeyboardButton(text="💳 Підтримати автора", callback_query_data="donate")],
        [InlineKeyboardButton(text="📱 Зв'язок з менеджером", url=MANAGER_URL)]
    ])

def catalog_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Худі Liberty (1200 грн)", callback_query_data="buy_hoodie")],
        [InlineKeyboardButton(text="Футболка Style (600 грн)", callback_query_data="buy_tshirt")],
        [InlineKeyboardButton(text="Світшот School (950 грн)", callback_query_data="buy_sweat")],
        [InlineKeyboardButton(text="Кепка (450 грн)", callback_query_data="buy_cap")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_query_data="start")]
    ])

# --- ОБРОБНИКИ ---
@dp.message(Command("start"))
async def start(m: types.Message):
    async with aiosqlite.connect("liberty.db") as db:
        await db.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (m.from_user.id,))
        await db.commit()
    await m.answer("👋 Вітаємо в Liberty Style!", reply_markup=main_kb())

@dp.callback_query(F.data == "start")
async def back(c: types.CallbackQuery):
    await c.message.edit_text("Головне меню:", reply_markup=main_kb())

@dp.callback_query(F.data == "catalog")
async def catalog(c: types.CallbackQuery):
    await c.message.edit_text("🔥 Наш асортимент:", reply_markup=catalog_kb())

@dp.callback_query(F.data == "sizes")
async def sizes(c: types.CallbackQuery):
    text = "📏 **Розміри:**\n• S (160-170)\n• M (170-180)\n• L (180-190)\n• XL (Oversize)"
    await c.message.edit_text(text, reply_markup=main_kb())

@dp.callback_query(F.data.startswith("buy_"))
async def pay(c: types.CallbackQuery):
    await c.message.answer(f"💳 Карта: `{CARD}`\nНадішліть чек менеджеру!", url=MANAGER_URL, parse_mode="Markdown")

# --- АДМІНКА ---
@dp.message(Command("admin"))
async def admin(m: types.Message):
    if m.from_user.id in ADMINS:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📢 Розсилка", callback_query_data="broadcast")]])
        await m.answer("🛠 Панель адміністратора:", reply_markup=kb)

@dp.callback_query(F.data == "broadcast")
async def broadcast_step(c: types.CallbackQuery):
    if c.from_user.id in ADMINS:
        await c.message.answer("Введіть текст розсилки:")

@dp.message(lambda m: m.from_user.id in ADMINS and not m.text.startswith("/"))
async def do_broadcast(m: types.Message):
    async with aiosqlite.connect("liberty.db") as db:
        cursor = await db.execute("SELECT id FROM users")
        users = await cursor.fetchall()
        for u in users:
            try: await bot.send_message(u[0], m.text)
            except: pass
    await m.answer("✅ Розсилка завершена!")

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

