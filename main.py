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

# 20 ta to'liq Grammar savollari bazasi
A1_QUESTIONS = [
    {"q": "1. I ... a student.", "options": ["is", "am", "are", "be"], "correct": 1},
    {"q": "2. She ... tennis every weekend.", "options": ["play", "plays", "playing", "is play"], "correct": 1},
    {"q": "3. They ... in Tashkent now.", "options": ["lives", "living", "live", "are live"], "correct": 2},
    {"q": "4. Where ... you yesterday?", "options": ["were", "was", "did", "are"], "correct": 0},
    {"q": "5. He has ... car.", "options": ["a", "an", "the", "some"], "correct": 0},
    {"q": "6. There ... some milk in the fridge.", "options": ["are", "is", "be", "am"], "correct": 1},
    {"q": "7. My brother can ... English well.", "options": ["speaks", "speak", "speaking", "to speak"], "correct": 1},
    {"q": "8. Look! The sun ...", "options": ["shines", "is shining", "shine", "shining"], "correct": 1},
    {"q": "9. We ... to London last year.", "options": ["go", "goed", "went", "gone"], "correct": 2},
    {"q": "10. Whose book is this? It is ...", "options": ["my", "mine", "me", "I"], "correct": 1},
    {"q": "11. How ... apples do you want?", "options": ["much", "many", "a lot", "any"], "correct": 1},
    {"q": "12. She doesn't like ... coffee.", "options": ["drink", "drinking", "drank", "drinks"], "correct": 1},
    {"q": "13. Today is ... than yesterday.", "options": ["hot", "hottest", "hotter", "more hot"], "correct": 2},
    {"q": "14. He is ... tallest boy in the class.", "options": ["a", "an", "the", "-"], "correct": 2},
    {"q": "15. What ... you doing at 5 PM yesterday?", "options": ["were", "was", "did", "are"], "correct": 0},
    {"q": "16. I have ... finished my homework.", "options": ["yet", "just", "ever", "never"], "correct": 1},
    {"q": "17. She has lived here ... 2020.", "options": ["for", "since", "in", "at"], "correct": 1},
    {"q": "18. You ... smoke in the hospital.", "options": ["must", "mustn't", "should", "can"], "correct": 1},
    {"q": "19. If it is sunny, we ... go for a walk.", "options": ["will", "would", "did", "do"], "correct": 0},
    {"q": "20. Thank you very ...", "options": ["many", "much", "lot", "good"], "correct": 1},
]

A2_QUESTIONS = [
    {"q": "1. If it rains, I ... at home.", "options": ["stay", "will stay", "stayed", "staying"], "correct": 1},
    {"q": "2. She is interested ... learning languages.", "options": ["on", "in", "at", "with"], "correct": 1},
    {"q": "3. English is spoken ... the world.", "options": ["all over", "on", "in", "at"], "correct": 0},
    {"q": "4. I have never ... to Paris.", "options": ["be", "was", "been", "went"], "correct": 2},
    {"q": "5. He drives ... than his brother.", "options": ["careful", "more carefully", "carefully", "most careful"], "correct": 1},
    {"q": "6. This is the house ... I was born.", "options": ["which", "where", "who", "when"], "correct": 1},
    {"q": "7. While I was reading, the phone ...", "options": ["ring", "rang", "was ringing", "rung"], "correct": 1},
    {"q": "8. You look tired. You ... go to bed.", "options": ["should", "mustn't", "can", "might"], "correct": 0},
    {"q": "9. How ... have you lived here?", "options": ["long", "much", "many", "often"], "correct": 0},
    {"q": "10. I am looking forward ... you.", "options": ["to see", "seeing", "to seeing", "see"], "correct": 2},
    {"q": "11. She sings better ... her sister.", "options": ["that", "than", "as", "then"], "correct": 1},
    {"q": "12. He is not old ... to drive a car.", "options": ["too", "enough", "very", "such"], "correct": 1},
    {"q": "13. Namangan is famous ... its apples.", "options": ["of", "for", "with", "in"], "correct": 1},
    {"q": "14. Nobody ... knows the answer.", "options": ["dont", "doesn't", "-", "isn't"], "correct": 2},
    {"q": "15. I'd like ... cup of tea, please.", "options": ["other", "another", "more", "others"], "correct": 1},
    {"q": "16. She asked me where ...", "options": ["do I live", "I live", "live I", "did I live"], "correct": 1},
    {"q": "17. Bread ... from wheat.", "options": ["is made", "made", "makes", "is making"], "correct": 0},
    {"q": "18. He was tired, ... he went to sleep early.", "options": ["because", "so", "but", "although"], "correct": 1},
    {"q": "19. I have ... friends at school.", "options": ["a little", "much", "a few", "any"], "correct": 2},
    {"q": "20. She sings ... beautifully.", "options": ["extreme", "extremly", "extremely", "more"], "correct": 2},
]

B1_QUESTIONS = [
    {"q": "1. By this time next year, I ... my studies.", "options": ["will finish", "will have finished", "finish", "finished"], "correct": 1},
    {"q": "2. If I had more money, I ... a new car.", "options": ["buy", "will buy", "would buy", "bought"], "correct": 2},
    {"q": "3. She managed ... the exam successfully.", "options": ["pass", "passing", "to pass", "passed"], "correct": 2},
    {"q": "4. I wish I ... speak French fluently.", "options": ["can", "could", "will", "have"], "correct": 1},
    {"q": "5. The book ... by Mark Twain is fascinating.", "options": ["writing", "written", "wrote", "write"], "correct": 1},
    {"q": "6. Unless you study hard, you ... pass.", "options": ["will", "won't", "would", "wouldn't"], "correct": 1},
    {"q": "7. He is used ... up early in the morning.", "options": ["get", "to get", "getting", "to getting"], "correct": 3},
    {"q": "8. Neither John nor his friends ... coming.", "options": ["is", "are", "was", "has"], "correct": 1},
    {"q": "9. I would rather ... at home today.", "options": ["stay", "to stay", "staying", "stayed"], "correct": 0},
    {"q": "10. It's high time you ... studying.", "options": ["start", "started", "starting", "starts"], "correct": 1},
    {"q": "11. Hard ... he tried, he couldn't win.", "options": ["although", "as", "however", "despite"], "correct": 1},
    {"q": "12. She suggested ... to the cinema.", "options": ["go", "to go", "going", "gone"], "correct": 2},
    {"q": "13. This time tomorrow, we ... over the ocean.", "options": ["will fly", "will be flying", "fly", "flown"], "correct": 1},
    {"q": "14. I regret ... you that the position is filled.", "options": ["tell", "telling", "to tell", "told"], "correct": 2},
    {"q": "15. He didn't remember ... the door.", "options": ["lock", "locking", "to lock", "locked"], "correct": 1},
    {"q": "16. The test was ... difficult that nobody passed.", "options": ["so", "such", "too", "very"], "correct": 0},
    {"q": "17. Inspite of ... late, we missed the start.", "options": ["arrive", "arriving", "arrived", "to arrive"], "correct": 1},
    {"q": "18. She is said ... one of the best singers.", "options": ["to be", "being", "be", "been"], "correct": 0},
    {"q": "19. If she had left earlier, she ... the train.", "options": ["would catch", "would have caught", "caught", "had caught"], "correct": 1},
    {"q": "20. Let's start working, ...?", "options": ["shall we", "will you", "don't we", "let us"], "correct": 0},
]

B2_QUESTIONS = [
    {"q": "1. Much ... known about the ancient civilization.", "options": ["are", "is", "have", "were"], "correct": 1},
    {"q": "2. Hardly had I entered the room ... the phone rang.", "options": ["when", "than", "then", "scarcely"], "correct": 0},
    {"q": "3. Not only ... late, but he also forgot his homework.", "options": ["he was", "was he", "did he be", "he is"], "correct": 1},
    {"q": "4. It is essential that every student ... present.", "options": ["is", "be", "are", "were"], "correct": 1},
    {"q": "5. Little ... that the decision would change everything.", "options": ["I knew", "did I know", "knew I", "do I know"], "correct": 1},
    {"q": "6. Had I known the truth, I ... differently.", "options": ["would act", "would have acted", "acted", "had acted"], "correct": 1},
    {"q": "7. Supposing you ... a million dollars, what would you do?", "options": ["win", "won", "had won", "winning"], "correct": 1},
    {"q": "8. The project is ... completion.", "options": ["on the verge of", "about", "due to", "near"], "correct": 0},
    {"q": "9. She acted as though she ... everything.", "options": ["knows", "knew", "had known", "has known"], "correct": 1},
    {"q": "10. There's no point ... arguing about it.", "options": ["to", "in", "at", "for"], "correct": 1},
    {"q": "11. He is believed ... the company last year.", "options": ["to leave", "to have left", "leaving", "left"], "correct": 1},
    {"q": "12. Scarcely had we arrived ... it started to rain.", "options": ["than", "when", "then", "after"], "correct": 1},
    {"q": "13. I'd sooner you ... smoke in here.", "options": ["don't", "didn't", "won't", "haven't"], "correct": 1},
    {"q": "14. The more you practice, ... you become.", "options": ["the better", "better", "best", "the best"], "correct": 0},
    {"q": "15. Such ... the demand that prices rose instantly.", "options": ["was", "were", "did", "is"], "correct": 0},
    {"q": "16. He was on the ... of resigning when promotion came.", "options": ["edge", "verge", "brink", "point"], "correct": 3},
    {"q": "17. No sooner had I opened the door ... a cat jumped out.", "options": ["when", "than", "then", "after"], "correct": 1},
    {"q": "18. Try as he might, he ... solve the puzzle.", "options": ["couldn't", "can", "will", "managed to"], "correct": 0},
    {"q": "19. It's high time something ... about this issue.", "options": ["is done", "was done", "did", "has done"], "correct": 1},
    {"q": "20. She is second to ... in mathematics.", "options": ["none", "nothing", "anyone", "someone"], "correct": 0},
]

C1_QUESTIONS = [
    {"q": "1. ... be that as it may, we must proceed with the plan.", "options": ["Let", "May", "Should", "Would"], "correct": 0},
    {"q": "2. So abrupt ... that nobody understood his point.", "options": ["was his speech", "his speech was", "did his speech", "speech was"], "correct": 0},
    {"q": "3. Were ... to offer you the job, would you take it?", "options": ["they", "them", "their", "theirs"], "correct": 0},
    {"q": "4. Not until years later ... the full story.", "options": ["did I learn", "I learned", "I did learn", "learned I"], "correct": 0},
    {"q": "5. He spoke as if he ... an expert in quantum physics.", "options": ["is", "were", "has been", "had been"], "correct": 1},
    {"q": "6. ... intelligent as she is, she failed the interview.", "options": ["Although", "Much", "However", "As"], "correct": 2},
    {"q": "7. Seldom ... a more breathtaking view.", "options": ["I have seen", "have I seen", "did I saw", "saw I"], "correct": 1},
    {"q": "8. By no means ... this to be taken lightly.", "options": ["this is", "is this", "does this", "this does"], "correct": 1},
    {"q": "9. On no account ... the laboratory unattended.", "options": ["you should leave", "should you leave", "leave you", "you leave"], "correct": 1},
    {"q": "10. Only by working together ... overcome the crisis.", "options": ["we can", "can we", "we could", "do we"], "correct": 1},
    {"q": "11. Had it not been for your help, we ... succeeded.", "options": ["won't have", "wouldn't have", "hadn't", "haven't"], "correct": 1},
    {"q": "12. However ... you analyze it, the risk remains high.", "options": ["much", "many", "well", "closely"], "correct": 3},
    {"q": "13. ... being wealthy, he lived a modest life.", "options": ["Despite", "Although", "In spite", "However"], "correct": 0},
    {"q": "14. It is imperative that the contract ... signed immediately.", "options": ["is", "be", "was", "will be"], "correct": 1},
    {"q": "15. Try ... he might, success eluded him.", "options": ["as", "though", "however", "that"], "correct": 0},
    {"q": "16. Scarcely had the meeting commenced ... objections were raised.", "options": ["than", "when", "then", "after"], "correct": 1},
    {"q": "17. Such ... the magnitude of the problem that swift action was taken.", "options": ["is", "was", "were", "did"], "correct": 1},
    {"q": "18. Nowhere ... a more dedicated team.", "options": ["you will find", "will you find", "find you", "you find"], "correct": 1},
    {"q": "19. The proposal was rejected, ... to say, due to budget cuts.", "options": ["needless", "needlessly", "need", "necessary"], "correct": 0},
    {"q": "20. Be that as it ..., we must accept the outcome.", "options": ["is", "may", "was", "were"], "correct": 1},
]

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
},
6: {
"passage": "<b>IELTS Academic Reading - Mock 6: Socioeconomic Impacts of Modern Globalization</b>\n\nGlobalization has deeply integrated international markets, accelerating cross-border trade and cultural exchange networks. While it drives unprecedented economic growth, it also sparks significant debates regarding wealth distribution disparities and the potential erosion of localized cultural heritages.",
"questions": [
{"q": "1. What has globalization integrated deeply?", "options": ["Isolated mountain villages", "International markets", "Subterranean ecosystems", "Planetary orbits"], "correct": 1},
{"q": "2. Which aspects have been accelerated by global connectivity?", "options": ["Cross-border trade and cultural exchange", "Bureaucratic delays", "Manual agricultural labor", "Geological drifting"], "correct": 0},
{"q": "3. What positive outcome is associated with globalization in the text?", "options": ["Unprecedented economic growth", "Universal poverty eradication", "Complete cultural uniformity", "Total industrial cessation"], "correct": 0},
{"q": "4. What major debate is sparked by global economic integration?", "options": ["Wealth distribution disparities", "The shape of the Earth", "Interstellar travel routes", "Subatomic particle speeds"], "correct": 0},
{"q": "5. Does globalization pose a concern for local heritages?", "options": ["Yes, potential erosion of local heritage", "No, it reinforces ancient traditions exclusively", "Not mentioned", "Local heritages expand rapidly"], "correct": 0},
{"q": "6. International markets under globalization are described as...", "options": ["Completely disconnected", "Deeply integrated", "Permanently frozen", "Restricted to local trade"], "correct": 1},
{"q": "7. Cultural exchange networks are...", "options": ["Slowed down", "Accelerated", "Eliminated", "Banned"], "correct": 1},
{"q": "8. True or False: Globalization impacts only financial structures without cultural effects.", "options": ["True", "False", "Not Given", "Partially True"], "correct": 1},
{"q": "9. Economic growth driven by globalization is characterized as...", "options": ["Unprecedented", "Inconsequential", "Negligible", "Declining"], "correct": 0},
{"q": "10. Wealth distribution disparities refer to...", "options": ["Equal sharing of all global income", "Gaps in wealth spread", "Identical salaries worldwide", "State-mandated rationing"], "correct": 1},
{"q": "11. The passage views globalization as a purely beneficial phenomenon.", "options": ["True", "False", "Not Given", "Flawless"], "correct": 1},
{"q": "12. Cross-border trade involves...", "options": ["Trading strictly within a single town", "Commerce across national borders", "Barter systems only", "Illegal smuggling exclusively"], "correct": 1},
{"q": "13. Localized cultural heritages face risks of...", "options": ["Enhancement", "Erosion", "Stagnation", "Fossilization"], "correct": 1},
{"q": "14. Debates surrounding globalization involve...", "options": ["Socioeconomic impacts", "Meteorological forecasts", "Deep sea diving", "Agricultural crop rotation"], "correct": 0},
{"q": "15. Market integration isolates countries from one another.", "options": ["True", "False", "Not Given", "Paradoxically"], "correct": 1},
{"q": "16. Economic progress globally is linked to...", "options": ["Market integration", "Isolationism", "Feudalism", "Manual craftsmanship"], "correct": 0},
{"q": "17. The text mentions networks of...", "options": ["Cultural exchange", "Fishing routes", "Railway systems", "Underground cabling"], "correct": 0},
{"q": "18. Disparities in wealth are considered...", "options": ["A subject of debate", "Non-existent", "Beneficial to all", "Legally forbidden"], "correct": 0},
{"q": "19. Globalization affects which major domains?", "options": ["Economics and culture", "Space exploration only", "Deep oceanography", "Internal medicine"], "correct": 0},
{"q": "20. Overall, globalization presents a complex mix of growth and challenges.", "options": ["True", "False", "Not Given", "Simple"], "correct": 0}
]
},
7: {
"passage": "<b>IELTS Academic Reading - Mock 7: Space Exploration & Astrobiological Research</b>\n\nRecent advancements in astrobiological research have shifted focus toward Mars rovers and icy moons like Europa and Enceladus. Advanced spectroscopic biosignature analysis allows scientists to detect organic molecules and potential atmospheric gases indicative of past or present extraterrestrial microbial life.",
"questions": [
{"q": "1. What has recently shifted focus in astrobiology?", "options": ["Deep ocean trench mapping", "Mars rovers and icy moons", "Terrestrial desert mining", "Volcanic eruption tracking"], "correct": 1},
{"q": "2. Which specific icy moons are highlighted in the text?", "options": ["Titan and Ganymede", "Europa and Enceladus", "Io and Callisto", "Phobos and Deimos"], "correct": 1},
{"q": "3. What technology enables the detection of organic molecules?", "options": ["Spectroscopic biosignature analysis", "Radar echolocation", "Magnetic resonance imaging", "Optical telescope magnification"], "correct": 0},
{"q": "4. What are scientists searching for using atmospheric gases?", "options": ["Extraterrestrial microbial life", "Interstellar trade routes", "Cosmic background radiation sources", "Asteroid collision trajectories"], "correct": 0},
{"q": "5. True or False: Astrobiology focuses exclusively on Earth's core.", "options": ["True", "False", "Not Given", "Partial"], "correct": 1},
{"q": "6. Organic molecules indicate...", "options": ["Potential life signatures", "Pure metallic deposits", "Radioactive decay", "Solar flare activity"], "correct": 0},
{"q": "7. Mars exploration involves the use of...", "options": ["Rovers", "Submarines", "Hot air balloons", "Trench excavators"], "correct": 0},
{"q": "8. Icy moons are studied because they may harbor...", "options": ["Subsurface liquid oceans", "Volcanic magma rivers", "Dense tropical forests", "Extensive desert dunes"], "correct": 0},
{"q": "9. Spectroscopic analysis examines...", "options": ["Light and chemical signatures", "Acoustic frequencies", "Gravitational waves", "Thermal plate shifts"], "correct": 0},
{"q": "10. The search for life includes both...", "options": ["Past and present indicators", "Future and hypothetical eras", "Ancient mythology", "Medieval astronomy"], "correct": 0},
{"q": "11. Enceladus is classified as an icy moon in the text.", "options": ["True", "False", "Not Given", "Doubtful"], "correct": 0},
{"q": "12. Atmospheric gases can reveal clues about...", "options": ["Biological activity", "Financial market trends", "Ocean salinity", "Tectonic plate velocity"], "correct": 0},
{"q": "13. Recent advancements in astrobiology are described as...", "options": ["Stagnant", "Significant", "Non-existent", "Decreasing"], "correct": 1},
{"q": "14. Microbial life refers to...", "options": ["Complex multi-cellular animals", "Microscopic organisms", "Plant root systems", "Avian species"], "correct": 1},
{"q": "15. Europa's surface features are made primarily of...", "options": ["Solid rock", "Ice", "Liquid lava", "Compressed gas"], "correct": 1},
{"q": "16. Biosignature analysis is used in...", "options": ["Astrobiological research", "Marine biology", "Meteorology", "Civil engineering"], "correct": 0},
{"q": "17. The text mentions rovers operating on...", "options": ["Mars", "Venus", "Mercury", "Saturn"], "correct": 0},
{"q": "18. Finding life beyond Earth is a primary goal of...", "options": ["Astrobiologists", "Economists", "Botanists", "Geologists"], "correct": 0},
{"q": "19. Spectroscopic tools analyze chemical compositions remotely.", "options": ["True", "False", "Not Given", "Theoretically"], "correct": 0},
{"q": "20. The exploration of icy moons represents a frontier in modern science.", "options": ["True", "False", "Not Given", "Irrelevant"], "correct": 0}
]
},
8: {
"passage": "<b>IELTS Academic Reading - Mock 8: Linguistic Diversity & Endangered Languages</b>\n\nRapid urbanization and the dominance of global media languages are accelerating the extinction of indigenous tongues worldwide. Preserving endangered languages is crucial not only for cultural heritage protection but also for safeguarding unique cognitive frameworks encoded in grammar systems.",
"questions": [
{"q": "1. What is accelerating the extinction of indigenous tongues?", "options": ["Agricultural expansion", "Rapid urbanization and global media languages", "Deep-sea exploration", "Renewable energy shifts"], "correct": 1},
{"q": "2. Why is preserving endangered languages crucial?", "options": ["For military strategy", "For cultural heritage and unique cognitive frameworks", "To standardize global taxation", "To simplify computer programming"], "correct": 1},
{"q": "3. What do grammar systems encode according to the text?", "options": ["Unique cognitive frameworks", "Mathematical equations", "Financial ledgers", "Architectural blueprints"], "correct": 0},
{"q": "4. True or False: Linguistic diversity is expanding rapidly without threat.", "options": ["True", "False", "Not Given", "Uncertain"], "correct": 1},
{"q": "5. Global media languages contribute to...", "options": ["Indigenous language preservation", "Indigenous language extinction pressure", "Universal bilingualism instantly", "Grammar simplification only"], "correct": 1},
{"q": "6. Urbanization affects linguistic diversity by...", "options": ["Promoting local dialects", "Spreading dominant languages", "Isolating tribes further", "Creating new sign languages"], "correct": 1},
{"q": "7. Cultural heritage protection relies partly on...", "options": ["Language preservation", "Monetary inflation control", "Highway construction", "Industrial automation"], "correct": 0},
{"q": "8. Endangered languages are facing...", "options": ["Revival surges", "Extinction risks", "Mandatory global teaching", "No changes"], "correct": 1},
{"q": "9. Cognitive frameworks are linked to...", "options": ["Grammar systems", "Physical athletic training", "Dietary habits", "Meteorological conditions"], "correct": 0},
{"q": "10. The number of active languages globally is...", "options": ["Increasing", "Facing widespread threats and decline", "Constant and unchanging", "Irrelevant to researchers"], "correct": 1},
{"q": "11. Media languages are described as...", "options": ["Global", "Obsolete", "Unspoken", "Subterranean"], "correct": 0},
{"q": "12. The text treats linguistic loss as a trivial matter.", "options": ["True", "False", "Not Given", "Amusing"], "correct": 1},
{"q": "13. Indigenous tongues belong to...", "options": ["Local and native communities", "Space agencies", "Corporate boardrooms", "Silicon Valley tech firms"], "correct": 0},
{"q": "14. Grammar systems encode...", "options": ["Cognitive frameworks", "Musical notes", "Chemical formulas", "Weather patterns"], "correct": 0},
{"q": "15. Rapid urbanization is a factor in...", "options": ["Linguistic shifts", "Coral reef bleaching", "Stellar formation", "Tectonic plate movement"], "correct": 0},
{"q": "16. Preserving languages protects...", "options": ["Cultural heritage", "Fossil fuels", "Engine performance", "Stock market portfolios"], "correct": 0},
{"q": "17. Dominant languages overshadow...", "options": ["Indigenous tongues", "Global trade", "Computer networks", "Ocean currents"], "correct": 0},
{"q": "18. Linguistic extinction is characterized as...", "options": ["Accelerating", "Halting", "Reversing naturally", "Beneficial"], "correct": 0},
{"q": "19. Protecting heritage requires saving...", "options": ["Endangered languages", "Plastic waste", "Old buildings only", "Ancient coins"], "correct": 0},
{"q": "20. Language is more than communication; it holds cognitive structures.", "options": ["True", "False", "Not Given", "Superficial"], "correct": 0}
]
},
9: {
"passage": "<b>IELTS Academic Reading - Mock 9: The Microeconomics of Global E-Commerce</b>\n\nDigital marketplaces have transformed retail through automated warehousing, drone delivery networks, and sophisticated AI personalization algorithms. These innovations reduce operational overheads while altering consumer purchasing habits on a global scale.",
"questions": [
{"q": "1. What has transformed retail operations globally?", "options": ["Digital marketplaces", "Traditional street bazaars", "Door-to-door salesmen", "Postal mail catalogs"], "correct": 0},
{"q": "2. Which technological innovations are utilized in modern warehousing?", "options": ["Automated warehousing and drones", "Manual sorting tables", "Animal transport", "Paper ledger tracking"], "correct": 0},
{"q": "3. What role do AI algorithms play in digital retail?", "options": ["Personalization", "Weather forecasting", "Medical diagnosis", "Structural engineering"], "correct": 0},
{"q": "4. How do these innovations affect operational overheads?", "options": ["They reduce them", "They increase them dramatically", "They eliminate all sales", "They have no effect"], "correct": 0},
{"q": "5. Consumer purchasing habits are...", "options": ["Altered significantly", "Completely frozen", "Unchanged for centuries", "Regulated by governments"], "correct": 0},
{"q": "6. Drone delivery networks represent...", "options": ["Next-generation logistics", "Ancient transport", "Obsolete shipping", "Subterranean mining"], "correct": 0},
{"q": "7. Digital marketplaces operate primarily in...", "options": ["Virtual online spaces", "Physical flea markets", "Remote forests", "Deep oceans"], "correct": 0},
{"q": "8. Personalization algorithms target...", "options": ["Consumer preferences", "Global seismic activity", "Solar radiation levels", "Ocean tides"], "correct": 0},
{"q": "9. Retail transformation is driven by...", "options": ["E-commerce technologies", "Agricultural reforms", "Feudal taxation", "Maritime shipping laws"], "correct": 0},
{"q": "10. True or False: E-commerce increases operational overhead costs.", "options": ["True", "False", "Not Given", "Partially"], "correct": 1},
{"q": "11. Warehousing automation increases...", "options": ["Efficiency and speed", "Human error rates", "Storage delays", "Paperwork volume"], "correct": 0},
{"q": "12. The scope of e-commerce impact is...", "options": ["Global", "Strictly local", "Confined to villages", "Irrelevant"], "correct": 0},
{"q": "13. AI personalization enhances...", "options": ["Shopping user experience", "Airplane autopilot", "Agricultural irrigation", "Musical composition"], "correct": 0},
{"q": "14. Operational overheads are costs related to...", "options": ["Running a business", "Personal entertainment", "Space travel", "Wildlife conservation"], "correct": 0},
{"q": "15. Delivery networks now incorporate...", "options": ["Drones", "Horse carriages", "Carrier pigeons", "Rowboats"], "correct": 0},
{"q": "16. Consumer habits are being...", "options": ["Altered", "Preserved strictly", "Ignored", "Banned"], "correct": 0},
{"q": "17. Digital marketplaces rely on...", "options": ["Internet infrastructure", "Coal power", "Manual telegraphs", "Parchment scrolls"], "correct": 0},
{"q": "18. The passage focuses on microeconomics of...", "options": ["Global e-commerce", "Ancient agriculture", "Feudal monarchies", "Wild forestry"], "correct": 0},
{"q": "19. Automation in warehouses is described as...", "options": ["Automated", "Manual", "Non-existent", "Inefficient"], "correct": 0},
{"q": "20. Overall, e-commerce redefines modern commercial mechanics.", "options": ["True", "False", "Not Given", "Marginal"], "correct": 0}
]
},
10: {
"passage": "<b>IELTS Academic Reading - Mock 10: The Science of Sleep Cycles & Human Cognition</b>\n\nQuality sleep, particularly deep sleep and REM phases, is vital for memory consolidation, cellular repair, and metabolic health. Chronic sleep deprivation impairs cognitive performance, weakens immunological defenses, and elevates long-term risks for neurodegenerative diseases.",
"questions": [
{"q": "1. Which sleep phases are highlighted as vital for memory?", "options": ["Light resting only", "Deep sleep and REM phases", "Daydreaming intervals", "Fatigue states"], "correct": 1},
{"q": "2. What biological function occurs during quality sleep?", "options": ["Cellular repair and memory consolidation", "Muscle atrophy", "Bone fractures", "Rapid hair loss"], "correct": 0},
{"q": "3. Metabolic health is closely linked to...", "options": ["Quality sleep", "High sugar diets exclusively", "Strenuous marathon running", "Constant noise exposure"], "correct": 0},
{"q": "4. What are the effects of chronic sleep deprivation?", "options": ["Impaired cognition and weakened immunity", "Superhuman strength", "Enhanced focus", "Immunity boost"], "correct": 0},
{"q": "5. Sleep deprivation elevates risks for...", "options": ["Neurodegenerative diseases", "Instantaneous athletic growth", "Perfect memory retention", "Higher metabolic speed"], "correct": 0},
{"q": "6. True or False: Sleep has no impact on immune defenses.", "options": ["True", "False", "Not Given", "Uncertain"], "correct": 1},
{"q": "7. Memory consolidation happens primarily during...", "options": ["Deep and REM sleep", "High-stress exams", "Intense physical workouts", "Loud concerts"], "correct": 0},
{"q": "8. Cellular repair is classified as a...", "options": ["Restorative sleep benefit", "Harmful condition", "Useless process", "Temporary anomaly"], "correct": 0},
{"q": "9. Cognitive performance is impaired by...", "options": ["Sleep deprivation", "Balanced nutrition", "Hydration", "Fresh air"], "correct": 0},
{"q": "10. Immunological defenses are weakened by...", "options": ["Lack of sleep", "Vitamin intake", "Regular exercise", "Meditation"], "correct": 0},
{"q": "11. REM stands for a specific phase of...", "options": ["Sleep", "Digestion", "Respiration", "Blood circulation"], "correct": 0},
{"q": "12. Chronic sleep deprivation is described as...", "options": ["Harmless", "Risky for health", "Beneficial", "Recommended"], "correct": 1},
{"q": "13. Neurodegenerative diseases are linked to...", "options": ["Long-term sleep deprivation", "Good sleeping habits", "Excessive resting", "Hydration"], "correct": 0},
{"q": "14. Sleep quality directly affects...", "options": ["Cognition and health", "Stock market rates", "Automotive aerodynamics", "Weather changes"], "correct": 0},
{"q": "15. The text emphasizes sleep as...", "options": ["Vital for the human body", "A waste of time", "Optional for survival", "Harmful"], "correct": 0},
{"q": "16. Deep sleep contributes to...", "options": ["Restoration and repair", "Physical exhaustion", "Mental fatigue", "Stress elevation"], "correct": 0},
{"q": "17. Sleep cycles involve distinct phases such as...", "options": ["REM and deep sleep", "Running and jumping", "Eating and drinking", "Reading and writing"], "correct": 0},
{"q": "18. Deprivation affects performance in a...", "options": ["Negative way", "Positive way", "Neutral way", "Beneficial way"], "correct": 0},
{"q": "19. The passage studies sleep from a...", "options": ["Scientific perspective", "Fictional angle", "Political viewpoint", "Financial stance"], "correct": 0},
{"q": "20. Overall, getting adequate sleep is essential for human well-being.", "options": ["True", "False", "Not Given", "Optional"], "correct": 0}
]
}
}

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    users_db.add(message.from_user.id)
    if message.from_user.id in user_quiz_state:
        del user_quiz_state[message.from_user.id]
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📚 Mock testlar (For practice)", callback_data="mock_tests"))
    builder.row(types.InlineKeyboardButton(text="🎓 Darajalar bo'yicha (Grammar)", callback_data="levels_menu"))
    builder.row(
        types.InlineKeyboardButton(text="🚀 Coming Soon 1", callback_data="soon_1"),
        types.InlineKeyboardButton(text="⏳ Coming Soon 2", callback_data="soon_2")
    )
    await message.answer("Salom! O'quv botimizga xush kelibsiz. Kerakli bo'limni tanlang:", reply_markup=builder.as_markup())

@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id
    
    if data == "mock_tests":
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="📖 IELTS Reading (10 ta mock)", callback_data="ielts_reading_list"))
        builder.row(types.InlineKeyboardButton(text="🎧 Listening", callback_data="mock_listening"))
        builder.row(
            types.InlineKeyboardButton(text="⏳ Coming Soon 3", callback_data="soon_3"),
            types.InlineKeyboardButton(text="⏳ Coming Soon 4", callback_data="soon_4")
        )
        builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main"))
        await callback.message.edit_text("📚 Mock testlar (For practice) bo'limini tanlang:", reply_markup=builder.as_markup())
        await callback.answer()
        
    elif data == "ielts_reading_list":
        builder = InlineKeyboardBuilder()
        for i in range(1, 11):
            builder.add(types.InlineKeyboardButton(text=f"Mock {i}", callback_data=f"start_mock_ielts_{i}"))
        builder.adjust(2)
        builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="mock_tests"))
        await callback.message.edit_text("📖 IELTS Reading mock testlaridan birini tanlang (1-10):", reply_markup=builder.as_markup())
        await callback.answer()
        
    elif data.startswith("start_mock_ielts_"):
        mock_num = int(data.split("_")[3])
        user_quiz_state[user_id] = {
            "mode": "reading",
            "mock_num": mock_num,
            "q_index": 0,
            "score": 0
        }
        try:
            await callback.message.delete()
        except Exception:
            pass
        await send_reading_question(callback.message, user_id)
        await callback.answer()
        
    elif data in ["mock_listening", "soon_3", "soon_4", "soon_1", "soon_2", "analysis_soon"]:
        await callback.message.answer("⏳ Bu funksiya tez kunda ishga tushadi (Coming soon)...")
        await callback.answer()
        
    elif data == "levels_menu":
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="🟢 A1 darajasi (20 ta test)", callback_data="start_A1"))
        builder.row(types.InlineKeyboardButton(text="🟡 A2 darajasi (20 ta test)", callback_data="start_A2"))
        builder.row(types.InlineKeyboardButton(text="🟠 B1 darajasi (20 ta test)", callback_data="start_B1"))
        builder.row(types.InlineKeyboardButton(text="🔵 B2 darajasi (20 ta test)", callback_data="start_B2"))
        builder.row(types.InlineKeyboardButton(text="🟣 C1 darajasi (20 ta test)", callback_data="start_C1"))
        builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main"))
        await callback.message.edit_text("Darajani tanlang:", reply_markup=builder.as_markup())
        await callback.answer()
        
    elif data == "back_to_main":
        if user_id in user_quiz_state:
            del user_quiz_state[user_id]
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="📚 Mock testlar (For practice)", callback_data="mock_tests"))
        builder.row(types.InlineKeyboardButton(text="🎓 Darajalar bo'yicha (Grammar)", callback_data="levels_menu"))
        builder.row(
            types.InlineKeyboardButton(text="🚀 Coming Soon 1", callback_data="soon_1"),
            types.InlineKeyboardButton(text="⏳ Coming Soon 2", callback_data="soon_2")
        )
        await callback.message.edit_text("Asosiy menyu:", reply_markup=builder.as_markup())
        await callback.answer()
        
    elif data.startswith("start_") and not data.startswith("start_mock_"):
        level = data.split("_")[1]
        user_quiz_state[user_id] = {"mode": "grammar", "level": level, "q_index": 0, "score": 0}
        try:
            await callback.message.delete()
        except Exception:
            pass
        await send_grammar_question(callback.message, user_id)
        await callback.answer()
        
    elif data.startswith("ans_"):
        if user_id not in user_quiz_state:
            await callback.message.answer("Test allaqachon tugagan yoki /start ni bosing.")
            await callback.answer()
            return
            
        selected_option = int(data.split("_")[1])
        state = user_quiz_state[user_id]
        
        if state["mode"] == "grammar":
            level = state["level"]
            q_index = state["q_index"]
            questions = A1_QUESTIONS if level == "A1" else (A2_QUESTIONS if level == "A2" else (B1_QUESTIONS if level == "B1" else (B2_QUESTIONS if level == "B2" else C1_QUESTIONS)))
            correct_option = questions[q_index]["correct"]
            if selected_option == correct_option:
                state["score"] += 1
            state["q_index"] += 1
            
            if state["q_index"] < len(questions):
                try:
                    await callback.message.delete()
                except Exception:
                    pass
                await send_grammar_question(callback.message, user_id)
            else:
                score = state["score"]
                total = len(questions)
                del user_quiz_state[user_id]
                try:
                    await callback.message.delete()
                except Exception:
                    pass
                await callback.message.answer(f"🎉 Test yakunlandi!\n\n✅ To'g'ri javoblar: {score} / {total}")
                
        elif state["mode"] == "reading":
            mock_num = state["mock_num"]
            q_index = state["q_index"]
            mock_data = READING_MOCKS[mock_num]
            questions = mock_data["questions"]
            correct_option = questions[q_index]["correct"]
            if selected_option == correct_option:
                state["score"] += 1
            state["q_index"] += 1
            
            if state["q_index"] < len(questions):
                try:
                    await callback.message.delete()
                except Exception:
                    pass
                await send_reading_question(callback.message, user_id)
            else:
                score = state["score"]
                total = len(questions)
                del user_quiz_state[user_id]
                builder = InlineKeyboardBuilder()
                builder.row(types.InlineKeyboardButton(text="📊 Tahlil qilish (Coming Soon)", callback_data="analysis_soon"))
                builder.row(types.InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_main"))
                try:
                    await callback.message.delete()
                except Exception:
                    pass
                await callback.message.answer(
                    f"🎯 <b>IELTS Reading - Mock {mock_num} yakunlandi!</b>\n\n"
                    f"📊 Sizning natijangiz: {score} / {total} ta to'g'ri javob."
                    , reply_markup=builder.as_markup(), parse_mode="HTML")
        await callback.answer()

async def send_grammar_question(message: types.Message, user_id: int):
    state = user_quiz_state[user_id]
    level = state["level"]
    q_index = state["q_index"]
    questions = A1_QUESTIONS if level == "A1" else (A2_QUESTIONS if level == "A2" else (B1_QUESTIONS if level == "B1" else (B2_QUESTIONS if level == "B2" else C1_QUESTIONS)))
    q_data = questions[q_index]
    builder = InlineKeyboardBuilder()
    for idx, option in enumerate(q_data["options"]):
        builder.row(types.InlineKeyboardButton(text=option, callback_data=f"ans_{idx}"))
    await message.answer(f"<b>{level} Daraja testi ({q_index + 1}/20)</b>\n\n{q_data['q']}", reply_markup=builder.as_markup(), parse_mode="HTML")

async def send_reading_question(message: types.Message, user_id: int):
    state = user_quiz_state[user_id]
    mock_num = state["mock_num"]
    q_index = state["q_index"]
    mock_data = READING_MOCKS[mock_num]
    q_data = mock_data["questions"][q_index]
    builder = InlineKeyboardBuilder()
    for idx, option in enumerate(q_data["options"]):
        builder.row(types.InlineKeyboardButton(text=option, callback_data=f"ans_{idx}"))
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
