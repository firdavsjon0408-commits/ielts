import os
import asyncio
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from groq import Groq

# 1. Tokenlar va sozlamalar
TOKEN = "8859239290:AAGmjuPB82BMDbEBaWh0kENkOZcTOgZiQiE"
GROQ_API_KEY = "gsk_caFeIAfnef5RLTh83i79WGdyb3FYvTMAzgQZW0S..."

# Groq mijoji
groq_client = Groq(api_key=GROQ_API_KEY)

# Logging
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Railway keep-alive uchun HTTP Server
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_http_server():
    server = HTTPServer(('0.0.0.0', 8080), SimpleHandler)
    server.serve_forever()

# Start komandasi
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "Men **IELTS Essay Checker** botiman. Menga istalgan IELTS inshongizni (Task 1 yoki Task 2) yuboring, "
        "va men uni professional ekzamenator sifatida tahlil qilib, **Band Score**, xatolar va yaxshilangan variantini beraman! ✍️"
    )

# Insholarni qabul qilib Groq (AI) orqali tekshirish
@dp.message(F.text)
async def check_essay(message: types.Message):
    if message.text.startswith('/'):
        return
        
    waiting_msg = await message.answer("⏳ Inshongiz AI tomonidan tahlil qilinmoqda, biroz kuting...")
    
    try:
        prompt = f"""
        You are a professional IELTS examiner. Analyze the following essay and provide:
        1. Estimated Band Score (Overall and criteria-wise).
        2. Detailed feedback on grammar, vocabulary, and coherence.
        3. Corrected version with improvements.

        Essay:
        {message.text}
        """
        
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        
        response_text = chat_completion.choices[0].message.content
        await bot.delete_message(chat_id=message.chat.id, message_id=waiting_msg.message_id)
        await message.answer(response_text)
        
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=waiting_msg.message_id)
        except:
            pass
        await message.answer("❌ Tahlil qilish vaqtida xatolik yuz berdi. Iltimos, birozdan keyin qayta urinib ko'ring.")

# Asosiy ishga tushirish funksiyasi
async def main():
    # Keep-alive serverni alohida oqimda ishga tushiramiz
    threading.Thread(target=run_http_server, daemon=True).start()
    print("Bot to'liq holda ishga tushdi...")
    
    # Eski webhooklarni tozalaymiz
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Pollingni boshlaymiz
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
