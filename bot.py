import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from supabase import create_client

# Sozlamalar
BOT_TOKEN = "8980966419:AAFVmCqV8Q7GOP0aBqvjxy-GXu-EOytA9do"
SUPABASE_URL = "https://waarsonurnghoocakrac.supabase.co"
SUPABASE_KEY = "bu_yerga_anon_key_yozing"

# Boshlash
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

logging.basicConfig(level=logging.INFO)

# Asosiy menyu
menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📚 Kitoblar"), KeyboardButton(text="🎧 Audio-kitoblar")],
    [KeyboardButton(text="🔍 Qidirish"), KeyboardButton(text="📂 Kategoriyalar")],
    [KeyboardButton(text="👤 Profilim"), KeyboardButton(text="👥 Do'st taklif qil")],
], resize_keyboard=True)

# /start
@dp.message(Command("start"))
async def start(message: types.Message):
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("ref_"):
        referrer_id = args[1].replace("ref_", "")
        # Referral saqlash
        supabase.table("referrals").insert({
            "referrer_id": referrer_id,
            "new_user_id": str(message.from_user.id)
        }).execute()

    # Foydalanuvchini saqlash
    supabase.table("users").upsert({
        "user_id": str(message.from_user.id),
        "username": message.from_user.username,
        "full_name": message.from_user.full_name,
        "premium": False
    }).execute()

    await message.answer(
        f"📚 *KitobUy ga xush kelibsiz!*\n\n"
        f"Minglab kitoblar, darsliklar va audio-kitoblar — barchasi bepul!\n\n"
        f"Quyidagi menyudan tanlang 👇",
        reply_markup=menu,
        parse_mode="Markdown"
    )

# Kitoblar
@dp.message(lambda m: m.text == "📚 Kitoblar")
async def kitoblar(message: types.Message):
    await message.answer("📚 Kategoriyani tanlang:", reply_markup=ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🏫 Darsliklar"), KeyboardButton(text="📖 Badiiy")],
        [KeyboardButton(text="🧠 Rivojlanish"), KeyboardButton(text="🔙 Orqaga")],
    ], resize_keyboard=True))

# Qidirish
@dp.message(lambda m: m.text == "🔍 Qidirish")
async def qidirish(message: types.Message):
    await message.answer("🔍 Kitob nomini yozing:")

# Profil
@dp.message(lambda m: m.text == "👤 Profilim")
async def profil(message: types.Message):
    user = supabase.table("users").select("*").eq(
        "user_id", str(message.from_user.id)
    ).execute()
    refs = supabase.table("referrals").select("*").eq(
        "referrer_id", str(message.from_user.id)
    ).execute()
    ref_count = len(refs.data) if refs.data else 0
    status = "⭐ Premium" if user.data and user.data[0].get("premium") else "🆓 Bepul"

    await message.answer(
        f"👤 *Profilingiz*\n\n"
        f"Ism: {message.from_user.full_name}\n"
        f"Status: {status}\n"
        f"Taklif qilganlar: {ref_count} kishi\n",
        parse_mode="Markdown"
    )

# Referral
@dp.message(lambda m: m.text == "👥 Do'st taklif qil")
async def referral(message: types.Message):
    link = f"https://t.me/KitobUY_bot?start=ref_{message.from_user.id}"
    await message.answer(
        f"👥 *Do'st taklif qil — Premium och!*\n\n"
        f"Sizning havolangiz:\n`{link}`\n\n"
        f"3 do'st → 1 oy Premium\n"
        f"10 do'st → VIP status 🏆",
        parse_mode="Markdown"
    )

# Matn qidirish
@dp.message()
async def search_book(message: types.Message):
    query = message.text
    results = supabase.table("books").select("*").ilike(
        "title", f"%{query}%"
    ).limit(5).execute()

    if not results.data:
        await message.answer("❌ Kitob topilmadi. Boshqa nom bilan qidiring.")
        return

    for book in results.data:
        await message.answer(
            f"📗 *{book['title']}*\n"
            f"👨‍🏫 Muallif: {book.get('author', 'Noma\\'lum')}\n"
            f"📄 Format: PDF\n",
            parse_mode="Markdown"
        )

# Ishga tushirish
if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
