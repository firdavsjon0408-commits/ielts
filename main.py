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

# A1 dan C1 gacha har biri 20 tadan to'liq test savollari bazasi
LEVEL_TESTS = {
    "A1": [
        {"q": "1. Choose the correct pronoun: '___ is a student.'", "options": ["He", "Him", "His", "Them"], "correct": 0},
        {"q": "2. What color is the sky on a clear day?", "options": ["Red", "Blue", "Green", "Yellow"], "correct": 1},
        {"q": "3. Which word is plural?", "options": ["Cat", "Dog", "Children", "House"], "correct": 2},
        {"q": "4. Complete: 'I ___ an apple yesterday.'", "options": ["eat", "ate", "eaten", "eating"], "correct": 1},
        {"q": "5. Choose the correct article: 'She has ___ umbrella.'", "options": ["a", "an", "the", "some"], "correct": 1},
        {"q": "6. They ___ from London.", "options": ["is", "am", "are", "be"], "correct": 2},
        {"q": "7. This is ___ book.", "options": ["my", "me", "I", "mine"], "correct": 0},
        {"q": "8. There ___ three cats in the room.", "options": ["is", "are", "am", "be"], "correct": 1},
        {"q": "9. What time ___ it?", "options": ["is", "are", "do", "does"], "correct": 0},
        {"q": "10. He can ___ very fast.", "options": ["run", "runs", "running", "ran"], "correct": 0},
        {"q": "11. Do you like ___?", "options": ["swim", "swimming", "swims", "swam"], "correct": 1},
        {"q": "12. Whose bag is this? It is ___.", "options": ["my", "mine", "me", "I"], "correct": 1},
        {"q": "13. She doesn't ___ coffee.", "options": ["drinks", "drinking", "drink", "drank"], "correct": 2},
        {"q": "14. Where ___ you live?", "options": ["does", "do", "is", "are"], "correct": 1},
        {"q": "15. Today is Monday, tomorrow is ___.", "options": ["Sunday", "Tuesday", "Friday", "Wednesday"], "correct": 1},
        {"q": "16. I have got ___ friends.", "options": ["much", "any", "a", "an"], "correct": 1},
        {"q": "17. Look at ___ birds!", "options": ["this", "that", "these", "it"], "correct": 2},
        {"q": "18. My father is ___ engineer.", "options": ["a", "an", "the", "-"], "correct": 1},
        {"q": "19. We ___ English on Tuesdays.", "options": ["learn", "learns", "learning", "learned"], "correct": 0},
        {"q": "20. How ___ is this shirt?", "options": ["many", "much", "long", "old"], "correct": 1}
    ],
    "A2": [
        {"q": "1. Choose the correct form: 'She ___ to school every day.'", "options": ["go", "goes", "going", "gone"], "correct": 1},
        {"q": "2. What is the comparative form of 'big'?", "options": ["bigger", "biggest", "more big", "as big as"], "correct": 0},
        {"q": "3. 'Have you ever ___ to London?'", "options": ["be", "go", "been", "went"], "correct": 2},
        {"q": "4. Choose the correct modal verb: 'You ___ wear a seatbelt.'", "options": ["must", "can", "might", "may"], "correct": 0},
        {"q": "5. Complete: 'They ___ playing football now.'", "options": ["is", "am", "are", "be"], "correct": 2},
        {"q": "6. I was reading a book when she ___.", "options": ["arrive", "arrived", "arriving", "has arrived"], "correct": 1},
        {"q": "7. She is ___ than her sister.", "options": ["tall", "taller", "tallest", "more tall"], "correct": 1},
        {"q": "8. He works ___ an accountant.", "options": ["like", "as", "how", "such"], "correct": 1},
        {"q": "9. I haven't seen him ___ last year.", "options": ["for", "since", "from", "during"], "correct": 1},
        {"q": "10. If it rains, we ___ stay at home.", "options": ["will", "would", "did", "have"], "correct": 0},
        {"q": "11. She speaks English very ___.", "options": ["good", "fluent", "fluently", "best"], "correct": 2},
        {"q": "12. This car is ___ expensive than that one.", "options": ["much", "more", "less", "as"], "correct": 1},
        {"q": "13. I am interested ___ learning French.", "options": ["on", "at", "in", "with"], "correct": 2},
        {"q": "14. We need to buy ___ milk.", "options": ["some", "any", "many", "a"], "correct": 0},
        {"q": "15. He told me that he ___ tired.", "options": ["is", "was", "be", "has been"], "correct": 1},
        {"q": "16. Whose keys are these? They are ___.", "options": ["our", "ours", "us", "we"], "correct": 1},
        {"q": "17. She enjoys ___ books in her free time.", "options": ["read", "to read", "reading", "reads"], "correct": 2},
        {"q": "18. How ___ have you lived here?", "options": ["long", "much", "many", "often"], "correct": 0},
        {"q": "19. You ___ smoke in the hospital.", "options": ["must", "mustn't", "should", "can"], "correct": 1},
        {"q": "20. The test was ___ difficult than I expected.", "options": ["too", "more", "much", "very"], "correct": 1}
    ],
    "B1": [
        {"q": "1. Choose the correct passive voice: 'The book ___ by Mark Twain.'", "options": ["wrote", "was written", "is write", "has written"], "correct": 1},
        {"q": "2. If I had money, I ___ a new car.", "options": ["will buy", "bought", "would buy", "can buy"], "correct": 2},
        {"q": "3. Choose the correct preposition: 'Interested ___ learning languages.'", "options": ["on", "at", "in", "with"], "correct": 2},
        {"q": "4. 'She speaks English very ___.'", "options": ["good", "fluent", "fluently", "best"], "correct": 2},
        {"q": "5. What is the synonym of 'ancient'?", "options": ["modern", "new", "old", "fast"], "correct": 2},
        {"q": "6. By this time next year, I ___ my studies.", "options": ["will finish", "will have finished", "finish", "finished"], "correct": 1},
        {"q": "7. She suggested ___ to the cinema.", "options": ["go", "to go", "going", "went"], "correct": 2},
        {"q": "8. I wish I ___ how to swim.", "options": ["know", "knew", "known", "had known"], "correct": 1},
        {"q": "9. He is used to ___ up early.", "options": ["get", "getting", "got", "be getting"], "correct": 1},
        {"q": "10. Neither John nor his friends ___ coming.", "options": ["is", "are", "was", "has"], "correct": 1},
        {"q": "11. The film was ___ boring that I fell asleep.", "options": ["such", "so", "too", "enough"], "correct": 1},
        {"q": "12. She asked me where ___.", "options": ["do I live", "I live", "did I live", "live I"], "correct": 1},
        {"q": "13. Despite ___ hard, he failed the test.", "options": ["study", "studying", "studied", "to study"], "correct": 1},
        {"q": "14. This is the house ___ I was born.", "options": ["which", "where", "when", "who"], "correct": 1},
        {"q": "15. You look tired. You ___ go to bed.", "options": ["should", "must", "have to", "ought"], "correct": 0},
        {"q": "16. I'd rather you ___ do that.", "options": ["don't", "didn't", "won't", "not"], "correct": 1},
        {"q": "17. He is capable ___ doing the job well.", "options": ["of", "in", "at", "with"], "correct": 0},
        {"q": "18. Have you finished ___ your homework?", "options": ["do", "to do", "doing", "done"], "correct": 2},
        {"q": "19. Unless you ___, you will miss the train.", "options": ["hurry", "don't hurry", "hurried", "will hurry"], "correct": 0},
        {"q": "20. It's high time we ___ home.", "options": ["go", "went", "gone", "are going"], "correct": 1}
    ],
    "B2": [
        {"q": "1. Hardly had I arrived home ___ it started to rain.", "options": ["when", "than", "then", "after"], "correct": 0},
        {"q": "2. Choose the correct phrasal verb meaning 'to postpone':", "options": ["put off", "take off", "give up", "turn down"], "correct": 0},
        {"q": "3. 'It is crucial that he ___ present at the meeting.'", "options": ["is", "be", "was", "will be"], "correct": 1},
        {"q": "4. Despite ___ hard, he failed the exam.", "options": ["studied", "studying", "study", "to study"], "correct": 1},
        {"q": "5. Choose the correct word: 'The company achieved significant ___ this year.'", "options": ["grow", "growth", "growing", "grown"], "correct": 1},
        {"q": "6. Not only ___ late, but he also forgot his books.", "options": ["he was", "was he", "did he be", "he is"], "correct": 1},
        {"q": "7. Supposing you ___, what would you do?", "options": ["win", "won", "had won", "will win"], "correct": 1},
        {"q": "8. The project was put on hold ___ lack of funding.", "options": ["because", "due to", "owing", "resulted in"], "correct": 1},
        {"q": "9. She is said ___ the competition.", "options": ["win", "to win", "to have won", "winning"], "correct": 2},
        {"q": "10. Little ___ that the secret was out.", "options": ["he knew", "did he know", "knew he", "he knows"], "correct": 1},
        {"q": "11. I wish I ___ my job last month.", "options": ["didn't quit", "hadn't quit", "wouldn't quit", "haven't quit"], "correct": 1},
        {"q": "12. It's essential that every candidate ___ interviewed.", "options": ["is", "be", "was", "will be"], "correct": 1},
        {"q": "13. No sooner had I opened the door ___ the cat ran out.", "options": ["than", "when", "then", "after"], "correct": 0},
        {"q": "14. He acted as though he ___ everything.", "options": ["knows", "knew", "had known", "has known"], "correct": 1},
        {"q": "15. The authorities refused to give way ___ the protesters' demands.", "options": ["to", "for", "with", "on"], "correct": 0},
        {"q": "16. So successful ___ that they opened a new branch.", "options": ["was the company", "the company was", "did the company", "is the company"], "correct": 0},
        {"q": "17. Much ___ I respect your opinion, I disagree.", "options": ["as", "though", "although", "despite"], "correct": 0},
        {"q": "18. She takes ___ her mother in appearance.", "options": ["after", "off", "up", "over"], "correct": 0},
        {"q": "19. The manager insisted on ___ the report immediately.", "options": ["check", "checking", "to check", "checked"], "correct": 1},
        {"q": "20. Had I known about the traffic, I ___ another route.", "options": ["would take", "will take", "would have taken", "took"], "correct": 2}
    ],
    "C1": [
        {"q": "1. Scarcely had we stepped outside ___ the storm broke.", "options": ["than", "when", "then", "after"], "correct": 1},
        {"q": "2. The CEO's resignation came ___ the heels of the financial scandal.", "options": ["on", "at", "in", "with"], "correct": 0},
        {"q": "3. Were ___ to withdraw support, the project would collapse.", "options": ["they", "them", "their", "theirs"], "correct": 0},
        {"q": "4. The politician's evasive answers only served to ___ suspicion.", "options": ["allay", "fuel", "mitigate", "suppress"], "correct": 1},
        {"q": "5. Only by working collaboratively ___ achieve our goals.", "options": ["we can", "can we", "we are able to", "are we"], "correct": 1},
        {"q": "6. The novel is a poignant reflection ___ the human condition.", "options": ["on", "in", "at", "to"], "correct": 0},
        {"q": "7. Comprehensive reforms are paramount ___ economic recovery.", "options": ["to ensure", "ensuring", "ensure", "ensured"], "correct": 0},
        {"q": "8. His unremitting dedication was instrumental ___ the firm's success.", "options": ["in", "to", "for", "at"], "correct": 0},
        {"q": "9. Far from ___ consensus, the committee remained deeply divided.", "options": ["reach", "reaching", "having reached", "to reach"], "correct": 1},
        {"q": "10. She harbored a deep-seated resentment ___ her former employer.", "options": ["towards", "against", "for", "with"], "correct": 1},
        {"q": "11. Intelligent life may well exist elsewhere, ___ we have no proof.", "options": ["albeit", "whereas", "consequently", "furthermore"], "correct": 0},
        {"q": "12. The historical findings shed light ___ ancient migratory patterns.", "options": ["on", "in", "over", "into"], "correct": 0},
        {"q": "13. In no way ___ the company responsible for the breach.", "options": ["is", "it is", "does", "was"], "correct": 0},
        {"q": "14. The intricacies of quantum mechanics defy ___ comprehension.", "options": ["easy", "easily", "easier", "ease"], "correct": 0},
        {"q": "15. Such ___ the magnitude of the task that extra resources were required.", "options": ["was", "is", "were", "be"], "correct": 0},
        {"q": "16. He was reluctant to delegate authority, preferring instead to oversee everything ___.", "options": ["himself", "personally", "individually", "solely"], "correct": 0},
        {"q": "17. The transition to renewable energy is fraught ___ technical challenges.", "options": ["with", "by", "in", "of"], "correct": 0},
        {"q": "18. An overhaul of the archaic regulations is long ___.", "options": ["due", "overdue", "past", "pending"], "correct": 1},
        {"q": "19. To state that the proposal is risky is something of an ___.", "options": ["exaggeration", "understatement", "hyperbole", "overstatement"], "correct": 1},
        {"q": "20. Persistence is paramount; ___, failure is inevitable.", "options": ["otherwise", "therefore", "furthermore", "meanwhile"], "correct": 0}
    ]
}

def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📊 Daraja testlari (A1-C1)", callback_data="level_tests_menu"))
    builder.row(
        types.InlineKeyboardButton(text="🚀 Coming Soon 1", callback_data="coming_soon_1"),
        types.InlineKeyboardButton(text="🚀 Coming Soon 2", callback_data="coming_soon_2")
    )
    return builder.as_markup()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    users_db.add(message.from_user.id)
    user_quiz_state.pop(message.from_user.id, None)
    await message.answer(
        "Salom! Botimizga xush kelibsiz. Quyidagi menyudan kerakli bo'limni tanlang:",
        reply_markup=get_main_menu()
    )

@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id
    
    if data == "level_tests_menu":
        user_quiz_state.pop(user_id, None)
        builder = InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(text="A1 Level", callback_data="start_level_A1"),
            types.InlineKeyboardButton(text="A2 Level", callback_data="start_level_A2")
        )
        builder.row(
            types.InlineKeyboardButton(text="B1 Level", callback_data="start_level_B1"),
            types.InlineKeyboardButton(text="B2 Level", callback_data="start_level_B2")
        )
        builder.row(types.InlineKeyboardButton(text="C1 Level", callback_data="start_level_C1"))
        builder.row(types.InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_main"))
        await callback.message.edit_text("📊 O'zingizga mos darajadagi testni tanlang (20 ta savol):", reply_markup=builder.as_markup())
        await callback.answer()
        
    elif data.startswith("start_level_"):
        level = data.split("_")[2]
        user_quiz_state[user_id] = {
            "level": level,
            "q_index": 0,
            "score": 0,
            "lock": False
        }
        await send_level_question(callback.message, user_id)
        await callback.answer()
        
    elif data in ["coming_soon_1", "coming_soon_2"]:
        await callback.answer("⚠️ Bu bo'lim tez kunda ochiladi!", show_alert=True)
        
    elif data == "back_to_main":
        user_quiz_state.pop(user_id, None)
        await callback.message.edit_text("Asosiy menyu:", reply_markup=get_main_menu())
        await callback.answer()
        
    elif data.startswith("ans_"):
        parts = data.split("_")
        if len(parts) < 3:
            await callback.answer()
            return
            
        cb_q_index = int(parts[1])
        selected_option = int(parts[2])
        
        state = user_quiz_state.get(user_id)
        if not state:
            await callback.answer("Test yakunlangan yoki eskirgan. Iltimos, /start bosing.", show_alert=True)
            return
            
        # Tez bosib yuborish (double-click) va race condition oldini olish uchun qulf
        if state.get("lock", False):
            await callback.answer()
            return
            
        if cb_q_index != state["q_index"]:
            await callback.answer("Bu savolga allaqachon javob berilgan!", show_alert=False)
            return
            
        state["lock"] = True
        try:
            level = state["level"]
            questions = LEVEL_TESTS[level]
            
            if selected_option == questions[cb_q_index]["correct"]:
                state["score"] += 1
                
            state["q_index"] += 1
            
            if state["q_index"] < len(questions):
                await send_level_question(callback.message, user_id)
            else:
                score = state["score"]
                total = len(questions)
                user_quiz_state.pop(user_id, None)
                
                builder = InlineKeyboardBuilder()
                builder.row(types.InlineKeyboardButton(text="🔄 Qaytadan boshlash", callback_data="level_tests_menu"))
                builder.row(types.InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_main"))
                
                if score > 18:
                    result_text = f"🎉 <b>Tabriklaymiz! Sizning darajangiz shu: {level}!</b>\n\n📊 To'g'ri javoblar: {score} / {total}"
                else:
                    result_text = f"❌ <b>Afsuski, yetarlicha ball to'play olmadingiz ({score}/{total}).</b>\n\nQayta urinib ko'ring! 🔄"

                await callback.message.edit_text(result_text, reply_markup=builder.as_markup(), parse_mode="HTML")
        finally:
            state["lock"] = False
            
        await callback.answer()

async def send_level_question(message: types.Message, user_id: int):
    state = user_quiz_state[user_id]
    level = state["level"]
    q_index = state["q_index"]
    q_data = LEVEL_TESTS[level][q_index]
    
    builder = InlineKeyboardBuilder()
    for idx, option in enumerate(q_data["options"]):
        builder.row(types.InlineKeyboardButton(text=option, callback_data=f"ans_{q_index}_{idx}"))
        
    text = f"📊 <b>Daraja testi: {level}</b>\n\n<b>Savol ({q_index + 1}/{len(LEVEL_TESTS[level])}):</b>\n{q_data['q']}"
    
    try:
        await message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception:
        pass

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
    print("Test tizimi xatosiz qulf (lock) mexanizmi bilan ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
