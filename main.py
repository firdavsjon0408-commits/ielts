import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = "8775259780:AAE0Gym25W5ganATBHJT-f6EsBbNSC91grg"
ADMIN_ID = 6773733838

bot = Bot(token=TOKEN)
dp = Dispatcher()
users_db = set()
user_quiz_state = {}

# Darajalar bo'yicha testlar bazasi (A1, A2, B1, B2)
LEVEL_TESTS = {
    "A1": [
        {"q": "1. Choose the correct pronoun: '___ is a student.'", "options": ["He", "Him", "His", "Them"], "correct": 0},
        {"q": "2. What color is the sky on a clear day?", "options": ["Red", "Blue", "Green", "Yellow"], "correct": 1},
        {"q": "3. Which word is plural?", "options": ["Cat", "Dog", "Children", "House"], "correct": 2},
        {"q": "4. Complete: 'I ___ an apple yesterday.' (Past simple - trick or basic)", "options": ["eat", "ate", "eaten", "eating"], "correct": 1},
        {"q": "5. Choose the correct article: 'She has ___ umbrella.'", "options": ["a", "an", "the", "some"], "correct": 1}
    ],
    "A2": [
        {"q": "1. Choose the correct form: 'She ___ to school every day.'", "options": ["go", "goes", "going", "gone"], "correct": 1},
        {"q": "2. What is the comparative form of 'big'?", "options": ["bigger", "biggest", "more big", "as big as"], "correct": 0},
        {"q": "3. 'Have you ever ___ to London?'", "options": ["be", "go", "been", "went"], "correct": 2},
        {"q": "4. Choose the correct modal verb for obligation: 'You ___ wear a seatbelt.'", "options": ["must", "can", "might", "may"], "correct": 0},
        {"q": "5. Complete: 'They ___ playing football now.'", "options": ["is", "am", "are", "be"], "correct": 2}
    ],
    "B1": [
        {"q": "1. Choose the correct passive voice: 'The book ___ by Mark Twain.'", "options": ["wrote", "was written", "is write", "has written"], "correct": 1},
        {"q": "2. If I had money, I ___ a new car.", "options": ["will buy", "bought", "would buy", "can buy"], "correct": 2},
        {"q": "3. Choose the correct preposition: 'Interested ___ learning languages.'", "options": ["on", "at", "in", "with"], "correct": 2},
        {"q": "4. 'She speaks English very ___.'", "options": ["good", "fluent", "fluently", "best"], "correct": 2},
        {"q": "5. What is the synonym of 'ancient'?", "options": ["modern", "new", "old", "fast"], "correct": 2}
    ],
    "B2": [
        {"q": "1. Hardly had I arrived home ___ it started to rain.", "options": ["when", "than", "then", "after"], "correct": 0},
        {"q": "2. Choose the correct phrasal verb meaning 'to postpone':", "options": ["put off", "take off", "give up", "turn down"], "correct": 0},
        {"q": "3. 'It is crucial that he ___ present at the meeting.'", "options": ["is", "be", "was", "will be"], "correct": 1},
        {"q": "4. Despite ___ hard, he failed the exam.", "options": ["studied", "studying", "study", "to study"], "correct": 1},
        {"q": "5. Choose the correct word: 'The company achieved significant ___ this year.'", "options": ["grow", "growth", "growing", "grown"], "correct": 1}
    ]
}

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    users_db.add(message.from_user.id)
    user_quiz_state[message.from_user.id] = {"session_id": asyncio.get_event_loop().time()}
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📊 Daraja bo'yicha testlar (A1-B2)", callback_data="level_tests_menu"))
    builder.row(
        types.InlineKeyboardButton(text="🚀 Coming Soon 1", callback_data="coming_soon_1"),
        types.InlineKeyboardButton(text="🚀 Coming Soon 2", callback_data="coming_soon_2")
    )
    await message.answer("Salom! Botimizga xush kelibsiz. Quyidagi menyudan kerakli bo'limni tanlang:", reply_markup=builder.as_markup())

@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id
    
    if data == "level_tests_menu":
        builder = InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(text="A1 Level", callback_data="start_level_A1"),
            types.InlineKeyboardButton(text="A2 Level", callback_data="start_level_A2")
        )
        builder.row(
            types.InlineKeyboardButton(text="B1 Level", callback_data="start_level_B1"),
            types.InlineKeyboardButton(text="B2 Level", callback_data="start_level_B2")
        )
        builder.row(types.InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_main"))
        await callback.message.edit_text("📊 O'zingizga mos darajadagi testni tanlang:", reply_markup=builder.as_markup())
        await callback.answer()
        
    elif data.startswith("start_level_"):
        level = data.split("_")[2]
        session_id = asyncio.get_event_loop().time()
        user_quiz_state[user_id] = {
            "session_id": session_id,
            "mode": "level",
            "level": level,
            "q_index": 0,
            "score": 0
        }
        try:
            await callback.message.delete()
        except Exception:
            pass
        await send_level_question(callback.message, user_id, session_id)
        await callback.answer()
        
    elif data in ["coming_soon_1", "coming_soon_2"]:
        await callback.answer("⚠️ Bu bo'lim tez kunda ochiladi!", show_alert=True)
        
    elif data == "back_to_main":
        user_quiz_state[user_id] = {"session_id": asyncio.get_event_loop().time()}
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="📊 Daraja bo'yicha testlar (A1-B2)", callback_data="level_tests_menu"))
        builder.row(
            types.InlineKeyboardButton(text="🚀 Coming Soon 1", callback_data="coming_soon_1"),
            types.InlineKeyboardButton(text="🚀 Coming Soon 2", callback_data="coming_soon_2")
        )
        await callback.message.edit_text("Asosiy menyu:", reply_markup=builder.as_markup())
        await callback.answer()
        
    elif data.startswith("ans_lvl_"):
        parts = data.split("_")
        selected_option = int(parts[2])
        btn_session = float(parts[3]) if len(parts) > 3 else 0.0
        
        state = user_quiz_state.get(user_id)
        if not state or state.get("session_id") != btn_session:
            await callback.answer("Bu eski tugma yoki boshqa sessiya testi. Iltimos, qaytadan /start bosing.", show_alert=True)
            return
            
        level = state["level"]
        q_index = state["q_index"]
        questions = LEVEL_TESTS[level]
        
        if selected_option == questions[q_index]["correct"]:
            state["score"] += 1
        state["q_index"] += 1
        
        if state["q_index"] < len(questions):
            try:
                await callback.message.delete()
            except Exception:
                pass
            await send_level_question(callback.message, user_id, state["session_id"])
        else:
            score = state["score"]
            total = len(questions)
            user_quiz_state[user_id] = {"session_id": asyncio.get_event_loop().time()}
            builder = InlineKeyboardBuilder()
            builder.row(types.InlineKeyboardButton(text="🔄 Qaytadan boshlash", callback_data="level_tests_menu"))
            builder.row(types.InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_main"))
            try:
                await callback.message.delete()
            except Exception:
                pass
            await callback.message.answer(
                f"🎯 <b>{level} Daraja testi yakunlandi!</b>\n\n"
                f"📊 Sizning natijangiz: {score} / {total} ta to'g'ri javob.",
                reply_markup=builder.as_markup(), parse_mode="HTML"
            )
        await callback.answer()

async def send_level_question(message: types.Message, user_id: int, session_id: float):
    state = user_quiz_state[user_id]
    level = state["level"]
    q_index = state["q_index"]
    q_data = LEVEL_TESTS[level][q_index]
    
    builder = InlineKeyboardBuilder()
    for idx, option in enumerate(q_data["options"]):
        builder.row(types.InlineKeyboardButton(text=option, callback_data=f"ans_lvl_{idx}_{session_id}"))
        
    text = f"📊 <b>Daraja testi: {level}</b>\n\n<b>Sual ({q_index + 1}/{len(LEVEL_TESTS[level])}):</b>\n{q_data['q']}"
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

@dp.message(Command("broadcast"))
async def broadcast_message(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Bu buyruq faqat admin uchun!")
        return
    text_to_send = message.text.replace("/broadcast", "").strip()
    if not text_to_send:
        await message.answer("Yuborish uchun matn yozmadingiz!")
        return
    count = 0
    for user_id in users_db:
        try:
            await bot.send_message(user_id, text_to_send)
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
    await message.answer(f"Xabar {count} ta foydalanuvchiga yuborildi!")

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

async def main():
    threading.Thread(target=run_http_server, daemon=True).start()
    print("Bot ishga tushdi va veb-server yoqildi...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
