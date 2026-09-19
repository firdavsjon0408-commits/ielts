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

# Asl 10 ta mockdan saralab olingan eng zo'r 5 ta IELTS Reading Mock bazasi
READING_MOCKS = {
    1: {
        "passage": "<b>IELTS Academic Reading - Mock 1: The Evolution of Architecture & Urban Design</b>\n\nArchitecture has transformed dramatically over the centuries, reflecting technological breakthroughs, cultural shifts, and environmental awareness. Modern skyscrapers utilize sustainable materials, smart energy grids, and advanced aerodynamic designs to withstand extreme weather conditions while optimizing interior climate control.",
        "questions": [
            {"q": "1. What is the primary driver of modern architectural transformation?", "options": ["Aesthetics alone", "Technology, culture, and environment", "Historical preservation", "Cost reduction exclusively"], "correct": 1},
            {"q": "2. What do modern skyscrapers utilize for climate control and stability?", "options": ["Traditional brick and mortar", "Smart energy grids and sustainable materials", "Manual ventilation systems", "Heavy metallic shielding"], "correct": 1},
            {"q": "3. How do aerodynamic designs help skyscrapers?", "options": ["By increasing total weight", "To withstand extreme weather conditions", "To lower construction duration", "To expand floor capacity"], "correct": 1},
            {"q": "4. True or False: Architecture only reflects past historical events.", "options": ["True", "False", "Not Given", "Partially True"], "correct": 1},
            {"q": "5. Which factor is NOT mentioned as a driver of architectural change?", "options": ["Technological breakthroughs", "Cultural shifts", "Political elections", "Environmental awareness"], "correct": 2},
            {"q": "6. What type of materials are prioritized in contemporary high-rises?", "options": ["Disposable plastics", "Sustainable materials", "Untreated timber", "Brittle composites"], "correct": 1},
            {"q": "7. What system optimizes interior climate control according to the text?", "options": ["Smart energy grids", "Geothermal radiators", "Open window networks", "Manual HVAC units"], "correct": 0},
            {"q": "8. The text implies that modern architecture ignores external weather challenges.", "options": ["True", "False", "Not Given", "Implicitly True"], "correct": 1},
            {"q": "9. Skyscraper designs today incorporate which specific structural approach?", "options": ["Ancient Roman arches", "Advanced aerodynamic designs", "Gothic buttresses", "Subterranean foundations"], "correct": 1},
            {"q": "10. What does the term 'smart energy grids' relate to?", "options": ["Power distribution and management", "Water filtration", "Waste management", "Traffic control"], "correct": 0},
            {"q": "11. The passage suggests architectural evolution is a rapid, recent phenomenon only.", "options": ["True", "False", "Not Given", "Unclear"], "correct": 1},
            {"q": "12. Environmental awareness in building design leads to...", "options": ["Higher energy consumption", "Sustainable structural solutions", "Decreased structural safety", "Increased waste production"], "correct": 1},
            {"q": "13. What role do cultural shifts play in architecture?", "options": ["They are completely irrelevant", "They reflect in design evolution", "They hinder engineering progress", "They dictate material prices"], "correct": 1},
            {"q": "14. Extreme weather resilience is achieved through...", "options": ["Lucky placement", "Advanced aerodynamic designs", "Temporary scaffolding", "Thinner glass walls"], "correct": 1},
            {"q": "15. Are traditional materials completely banned in modern engineering?", "options": ["Yes", "No", "Not mentioned in the text", "Only in skyscrapers"], "correct": 2},
            {"q": "16. Interior climate optimization is linked to...", "options": ["Poor insulation", "Smart energy integration", "Natural decay", "External noise"], "correct": 1},
            {"q": "17. Technological breakthroughs over the centuries have...", "options": ["Stagnant development", "Transformed architecture dramatically", "Reduced building heights", "Eliminated urban planning"], "correct": 1},
            {"q": "18. The passage highlights high-rises as examples of...", "options": ["Outdated construction", "Modern architectural adaptation", "Rural housing", "Temporary shelters"], "correct": 1},
            {"q": "19. Urban design elements discussed primarily involve...", "options": ["Aesthetic facade painting", "Structural and environmental engineering", "Interior furniture arrangement", "Real estate marketing"], "correct": 1},
            {"q": "20. Overall, the passage portrays architecture as a dynamic, evolving field.", "options": ["True", "False", "Not Given", "Static"], "correct": 0}
        ]
    },
    2: {
        "passage": "<b>IELTS Academic Reading - Mock 2: Artificial Intelligence in Diagnostic Medicine</b>\n\nAI algorithms are revolutionizing diagnostic medicine. By analyzing millions of medical scans within seconds, machine learning models can detect early signs of complex diseases like oncology and cardiovascular disorders with unprecedented accuracy, minimizing human error in clinical pathways.",
        "questions": [
            {"q": "1. What is revolutionizing diagnostic medicine?", "options": ["Traditional stethoscopes", "AI algorithms", "Hospital administration", "Paper medical records"], "correct": 1},
            {"q": "2. How quickly can machine learning models analyze medical scans?", "options": ["Within hours", "Within days", "Within seconds", "Within weeks"], "correct": 2},
            {"q": "3. What type of disorders are explicitly mentioned as being detected early?", "options": ["Orthopedic fractures", "Oncology and cardiovascular disorders", "Dermatological rashes", "Dental cavities"], "correct": 1},
            {"q": "4. What benefit do these algorithms provide in clinical pathways?", "options": ["Increasing paperwork", "Minimizing human error", "Lengthening diagnosis time", "Raising treatment costs"], "correct": 1},
            {"q": "5. True or False: AI models reduce diagnostic accuracy.", "options": ["True", "False", "Not Given", "Uncertain"], "correct": 1},
            {"q": "6. How many medical scans can be processed simultaneously?", "options": ["Thousands", "Millions", "Tens", "Hundreds"], "correct": 1},
            {"q": "7. The term 'unprecedented accuracy' implies...", "options": ["Lower than before", "Never seen or achieved before", "Average precision", "Inconsistent results"], "correct": 1},
            {"q": "8. Are human doctors completely replaced by AI according to the text?", "options": ["Yes", "No", "Not mentioned", "Only in surgery"], "correct": 2},
            {"q": "9. What core technology powers these diagnostic tools?", "options": ["Mechanical gearboxes", "Machine learning models", "Analog circuits", "Manual data entry"], "correct": 1},
            {"q": "10. Early detection helps in treating...", "options": ["Simple colds", "Complex diseases", "Physical injuries", "Allergies"], "correct": 1},
            {"q": "11. The scope of AI application is limited to rural clinics only.", "options": ["True", "False", "Not Given", "Partially True"], "correct": 2},
            {"q": "12. Clinical pathways benefit from AI through enhanced...", "options": ["Speed and precision", "Bureaucracy", "Cost escalation", "Delay"], "correct": 0},
            {"q": "13. Cardiovascular disorders belong to the conditions analyzed by...", "options": ["Accountants", "Machine learning models", "Patient relatives", "Pharmacists"], "correct": 1},
            {"q": "14. What does 'oncology' refer to in medical contexts?", "options": ["Heart conditions", "Cancer study and treatment", "Bone density", "Eye disorders"], "correct": 1},
            {"q": "15. The speed of AI analysis is measured in...", "options": ["Seconds", "Minutes", "Months", "Years"], "correct": 0},
            {"q": "16. Human error in diagnosis is projected to...", "options": ["Increase", "Minimize", "Stay identical", "Double"], "correct": 1},
            {"q": "17. The passage discusses AI in the context of...", "options": ["Entertainment", "Diagnostic medicine", "Financial trading", "Automotive driving"], "correct": 1},
            {"q": "18. Scan analysis via AI is described as...", "options": ["Slow and inaccurate", "Revolutionary and fast", "Costly and rare", "Ineffective"], "correct": 1},
            {"q": "19. The text states that AI analyzes audio files of patients.", "options": ["True", "False", "Not Given", "Sometimes"], "correct": 1},
            {"q": "20. Overall, machine learning contributes positively to modern healthcare diagnostics.", "options": ["True", "False", "Not Given", "Neutral"], "correct": 0}
        ]
    },
    3: {
        "passage": "<b>IELTS Academic Reading - Mock 3: The Psychology and Neuroscience of Habit Formation</b>\n\nBehavioral psychologists emphasize that forming a new routine requires a clear trigger, a consistent action, and an immediate rewarding feedback loop. Furthermore, neuroplasticity plays a crucial role in rewiring neural pathways during long-term skill acquisition and behavioral changes.",
        "questions": [
            {"q": "1. What elements are required to form a new routine?", "options": ["Random triggers and long breaks", "A clear trigger, consistent action, and rewarding feedback loop", "Strict financial penalties", "Complex psychological therapy"], "correct": 1},
            {"q": "2. What neurological concept is responsible for rewiring pathways?", "options": ["Neuroplasticity", "Blood circulation", "Cardiorespiratory fitness", "Synaptic stagnation"], "correct": 0},
            {"q": "3. The text states that habit formation happens instantaneously without effort.", "options": ["True", "False", "Not Given", "Partially True"], "correct": 1},
            {"q": "4. What is the role of a rewarding feedback loop?", "options": ["To punish bad habits", "To reinforce the routine", "To distract the mind", "To erase memories"], "correct": 1},
            {"q": "5. Long-term skill acquisition depends heavily on...", "options": ["Static neural connections", "Neuroplastic adaptations", "Genetic mutability", "Dietary restrictions"], "correct": 1},
            {"q": "6. Behavioral psychologists focus on...", "options": ["Mechanical engineering", "Human habits and routines", "Planetary orbits", "Marine biology"], "correct": 1},
            {"q": "7. Is a consistent action optional when creating a habit?", "options": ["Yes", "No", "Not mentioned", "Only for children"], "correct": 1},
            {"q": "8. What triggers the start of a routine according to the text?", "options": ["A clear trigger", "Complete exhaustion", "Uncontrolled noise", "Darkness"], "correct": 0},
            {"q": "9. Neural pathways during behavioral modification are described as...", "options": ["Fixed and permanent", "Flexible and rewiring", "Fragile and breaking", "Invisible"], "correct": 1},
            {"q": "10. The passage links habit formation directly with...", "options": ["Neuroscience and psychology", "Economics and banking", "Geology", "Astronomy"], "correct": 0},
            {"q": "11. Feedback loops must be delayed by several weeks to be effective.", "options": ["True", "False", "Not Given", "Unclear"], "correct": 1},
            {"q": "12. Skill acquisition is classified as a...", "options": ["Short-term anomaly", "Long-term process", "Useless endeavor", "Harmful condition"], "correct": 1},
            {"q": "13. Who studies behavioral routines in this context?", "options": ["Behavioral psychologists", "Geophysicists", "Astrophysicists", "Zoologists"], "correct": 0},
            {"q": "14. Rewiring pathways helps in...", "options": ["Forgetting everything", "Acquiring new skills", "Lowering body temperature", "Slowing down reflexes"], "correct": 1},
            {"q": "15. The text explicitly mentions financial incentives for habits.", "options": ["True", "False", "Not Given", "Always required"], "correct": 2},
            {"q": "16. Consistency in action acts as a pillar for...", "options": ["Routine establishment", "Muscle atrophy", "Sleep disorders", "Anxiety"], "correct": 0},
            {"q": "17. Brain adaptation is another term related to...", "options": ["Neuroplasticity", "Bone fracture", "Lung capacity", "Skin aging"], "correct": 0},
            {"q": "18. Habits require zero mental triggers.", "options": ["True", "False", "Not Given", "Sometimes"], "correct": 1},
            {"q": "19. The overall tone of the passage is...", "options": ["Scientific and informative", "Fictional", "Comedic", "Hostile"], "correct": 0},
            {"q": "20. Understanding habit psychology assists in personal development.", "options": ["True", "False", "Not Given", "Irrelevant"], "correct": 0}
        ]
    },
    4: {
        "passage": "<b>IELTS Academic Reading - Mock 4: Marine Ecosystems & Coral Reef Vulnerability</b>\n\nCoral reefs support thousands of marine species through intricate symbiotic relationships. However, rising sea temperatures, coastal pollution, and ocean acidification pose severe existential threats, triggering widespread coral bleaching across tropical environments worldwide.",
        "questions": [
            {"q": "1. What do coral reefs support?", "options": ["Desert mammals", "Thousands of marine species", "Alpine vegetation", "Freshwater fish exclusively"], "correct": 1},
            {"q": "2. What type of relationships exist among reef inhabitants?", "options": ["Competitive rivalry", "Intricate symbiotic relationships", "Isolated existence", "Parasitic domination only"], "correct": 1},
            {"q": "3. Which factor is threatening coral reefs?", "options": ["Rising sea temperatures", "Glacial expansion", "Increased freshwater salinity", "Subterranean volcanic eruptions"], "correct": 0},
            {"q": "4. Ocean acidification has a positive impact on coral health.", "options": ["True", "False", "Not Given", "Neutral"], "correct": 1},
            {"q": "5. What phenomenon is triggered by environmental stress on corals?", "options": ["Coral bleaching", "Rapid fossilization", "Luminescent glowing", "Immediate tectonic shift"], "correct": 0},
            {"q": "6. Where do coral bleaching events predominantly occur?", "options": ["Polar ice caps", "Tropical environments", "Mountain lakes", "Deep trenches"], "correct": 1},
            {"q": "7. Coastal pollution contributes to reef vulnerability.", "options": ["True", "False", "Not Given", "Partially"], "correct": 0},
            {"q": "8. The number of species supported by coral reefs is in the...", "options": ["Tens", "Hundreds", "Thousands", "Millions"], "correct": 2},
            {"q": "9. Symbiotic relationships in reefs are described as...", "options": ["Intricate", "Simple", "Non-existent", "Temporary"], "correct": 0},
            {"q": "10. Sea temperatures are currently...", "options": ["Dropping rapidly", "Rising", "Remaining completely stable", "Fluctuating randomly without trend"], "correct": 1},
            {"q": "11. Coral reefs are immune to global climate changes.", "options": ["True", "False", "Not Given", "Undecided"], "correct": 1},
            {"q": "12. Acidification affects which body of water?", "options": ["Oceans", "Deserts", "Volcanoes", "Atmosphere"], "correct": 0},
            {"q": "13. Existential threats to reefs come from...", "options": ["Human and environmental factors", "Fish migration", "Deep-sea currents", "Coral reproduction"], "correct": 0},
            {"q": "14. Widespread bleaching indicates...", "options": ["Healthy growth", "Severe ecological stress", "Increased fish population", "Abundant food supply"], "correct": 1},
            {"q": "15. Are all marine species affected by coral degradation?", "options": ["Yes, thousands depend on it", "No species are affected", "Only land animals", "Only birds"], "correct": 0},
            {"q": "16. Pollution types mentioned include...", "options": ["Coastal pollution", "Air pollution in space", "Noise pollution in forests", "Soil erosion"], "correct": 0},
            {"q": "17. Tropical environments are known for hosting...", "options": ["Coral reefs", "Tundra moss", "Glaciers", "Desert cacti"], "correct": 0},
            {"q": "18. The passage suggests coral ecosystems are fragile.", "options": ["True", "False", "Not Given", "Indestructible"], "correct": 0},
            {"q": "19. Global warming has no connection to sea temperatures.", "options": ["True", "False", "Not Given", "Obvious"], "correct": 1},
            {"q": "20. Protecting marine habitats requires addressing...", "options": ["Pollution and temperature drivers", "Cloud formations", "Lunar eclipses", "Solar flares"], "correct": 0}
        ]
    },
    5: {
        "passage": "<b>IELTS Academic Reading - Mock 5: The Global Transition to Renewable Energy Systems</b>\n\nTransitioning from fossil fuels to solar, wind, and geothermal power is essential for combating global climate change. Nations worldwide are heavily upgrading electrical grids, implementing smart metering, and deploying next-generation energy storage to ensure grid stability.",
        "questions": [
            {"q": "1. What energy source is being phased out in favor of renewables?", "options": ["Solar power", "Fossil fuels", "Geothermal energy", "Wind power"], "correct": 1},
            {"q": "2. Which power sources are part of the transition?", "options": ["Coal and oil", "Solar, wind, and geothermal", "Nuclear fission only", "Wood burning"], "correct": 1},
            {"q": "3. Why is this transition necessary?", "options": ["To increase oil consumption", "To combat global climate change", "To slow down industrial growth", "To reduce electricity use"], "correct": 1},
            {"q": "4. Nations are upgrading which infrastructure component?", "options": ["Electrical grids", "Highway networks", "Railway tracks", "Water pipelines"], "correct": 0},
            {"q": "5. What metering technology is being implemented?", "options": ["Analog meters", "Smart metering", "Manual counters", "Mechanical dials"], "correct": 1},
            {"q": "6. Next-generation energy storage ensures...", "options": ["Grid stability", "Blackouts", "Higher costs", "Energy waste"], "correct": 0},
            {"q": "7. The transition applies to only one isolated country.", "options": ["True", "False", "Not Given", "Regional only"], "correct": 1},
            {"q": "8. Geothermal power relies on...", "options": ["Earth's internal heat", "Solar radiation", "Wind velocity", "Ocean tides"], "correct": 0},
            {"q": "9. Grid modernization helps manage...", "options": ["Variable renewable inputs", "Traffic jams", "Air traffic", "Postal service"], "correct": 0},
            {"q": "10. Climate change mitigation requires energy shifts.", "options": ["True", "False", "Not Given", "Optional"], "correct": 0},
            {"q": "11. Wind power is categorized as a fossil fuel.", "options": ["True", "False", "Not Given", "Obsolete"], "correct": 1},
            {"q": "12. Energy storage solutions are described as...", "options": ["Next-generation", "Primitive", "Outdated", "Temporary"], "correct": 0},
            {"q": "13. Smart metering helps track...", "options": ["Energy consumption patterns", "Weather forecasts", "Stock market prices", "Ocean depths"], "correct": 0},
            {"q": "14. Fossil fuels are praised for zero emissions in the text.", "options": ["True", "False", "Not Given", "Partially"], "correct": 1},
            {"q": "15. Global participation in renewable transition is...", "options": ["Widespread across nations", "Non-existent", "Restricted to islands", "Banned"], "correct": 0},
            {"q": "16. Stability of electrical grids is...", "options": ["Unimportant", "Ensured by storage and upgrades", "Managed manually", "Declining"], "correct": 1},
            {"q": "17. Solar energy harnesses power from...", "options": ["The sun", "The moon", "Deep oceans", "Coal mines"], "correct": 0},
            {"q": "18. Upgrading grids requires minimal effort.", "options": ["True", "False", "Not Given", "Instantaneous"], "correct": 1},
            {"q": "19. The primary goal of renewable adoption is...", "options": ["Environmental preservation", "Economic collapse", "Energy scarcity", "Increased pollution"], "correct": 0},
            {"q": "20. The transition away from fossil fuels is optional.", "options": ["True", "False", "Not Given", "Essential"], "correct": 1}
        ]
    }
}

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    users_db.add(message.from_user.id)
    user_quiz_state[message.from_user.id] = {"session_id": asyncio.get_event_loop().time()}
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📖 IELTS Reading Mock testlar (1-5)", callback_data="ielts_reading_list"))
    await message.answer("Salom! Botimizga xush kelibsiz. IELTS Reading mock testini boshlash uchun quyidagi tugmani bosing:", reply_markup=builder.as_markup())

@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id
    
    if data == "ielts_reading_list":
        builder = InlineKeyboardBuilder()
        for i in range(1, 6):
            builder.add(types.InlineKeyboardButton(text=f"Mock {i}", callback_data=f"start_mock_ielts_{i}"))
        builder.adjust(2)
        builder.row(types.InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_main"))
        await callback.message.edit_text("📖 IELTS Reading 5 ta mukammal mock testidan birini tanlang:", reply_markup=builder.as_markup())
        await callback.answer()
        
    elif data.startswith("start_mock_ielts_"):
        mock_num = int(data.split("_")[3])
        session_id = asyncio.get_event_loop().time()
        user_quiz_state[user_id] = {
            "session_id": session_id,
            "mode": "reading",
            "mock_num": mock_num,
            "q_index": 0,
            "score": 0
        }
        try:
            await callback.message.delete()
        except Exception:
            pass
        await send_reading_question(callback.message, user_id, session_id)
        await callback.answer()
        
    elif data == "back_to_main":
        user_quiz_state[user_id] = {"session_id": asyncio.get_event_loop().time()}
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="📖 IELTS Reading Mock testlar (1-5)", callback_data="ielts_reading_list"))
        await callback.message.edit_text("Asosiy menyu:", reply_markup=builder.as_markup())
        await callback.answer()
        
    elif data.startswith("ans_"):
        parts = data.split("_")
        selected_option = int(parts[1])
        btn_session = float(parts[2]) if len(parts) > 2 else 0.0
        
        state = user_quiz_state.get(user_id)
        if not state or state.get("session_id") != btn_session:
            await callback.answer("Bu eski tugma yoki boshqa sessiya testi. Iltimos, /start bosing.", show_alert=True)
            return
            
        mock_num = state["mock_num"]
        q_index = state["q_index"]
        mock_data = READING_MOCKS[mock_num]
        questions = mock_data["questions"]
        
        if selected_option == questions[q_index]["correct"]:
            state["score"] += 1
        state["q_index"] += 1
        
        if state["q_index"] < len(questions):
            try:
                await callback.message.delete()
            except Exception:
                pass
            await send_reading_question(callback.message, user_id, state["session_id"])
        else:
            score = state["score"]
            total = len(questions)
            user_quiz_state[user_id] = {"session_id": asyncio.get_event_loop().time()}
            builder = InlineKeyboardBuilder()
            builder.row(types.InlineKeyboardButton(text="🔄 Qaytadan boshlash", callback_data="ielts_reading_list"))
            builder.row(types.InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_main"))
            try:
                await callback.message.delete()
            except Exception:
                pass
            await callback.message.answer(
                f"🎯 <b>IELTS Reading - Mock {mock_num} yakunlandi!</b>\n\n"
                f"📊 Sizning natijangiz: {score} / {total} ta to'g'ri javob.",
                reply_markup=builder.as_markup(), parse_mode="HTML"
            )
        await callback.answer()

async def send_reading_question(message: types.Message, user_id: int, session_id: float):
    state = user_quiz_state[user_id]
    mock_num = state["mock_num"]
    q_index = state["q_index"]
    mock_data = READING_MOCKS[mock_num]
    q_data = mock_data["questions"][q_index]
    builder = InlineKeyboardBuilder()
    for idx, option in enumerate(q_data["options"]):
        builder.row(types.InlineKeyboardButton(text=option, callback_data=f"ans_{idx}_{session_id}"))
    text = f"📖 <b>IELTS Reading - Mock {mock_num}</b>\n\n{mock_data['passage']}\n\n-------------------\n<b>Question ({q_index + 1}/20):</b>\n{q_data['q']}"
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
