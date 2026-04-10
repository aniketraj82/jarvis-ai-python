import ast
import datetime
import os
import random
import re
import smtplib
import subprocess
import sys
import tempfile
import time
import webbrowser
from email.message import EmailMessage
from urllib.parse import quote_plus

import pygame
import speech_recognition as sr
import wikipedia
from gtts import gTTS
try:
    import pyautogui
except Exception:
    pyautogui = None

ASSISTANT_NAME = "Jarvis"
TODO_FILE = "todo.txt"
NOTE_FILE = "notes.txt"
SENDER_EMAIL = "rajaniket80906@gmail.com"
DEFAULT_RECIPIENT = "aniketraj2350@gmail.com"
WHATSAPP_PHONE = "+918476057141"
ACTIVE_LANG = "en"

LANG_STT = {"en": "en-IN", "hi": "hi-IN", "te": "te-IN"}
LANGS = ("en", "hi", "te")
WAKE_WORDS = ("hello jarvis", "hey jarvis", "hi jarvis", "hlo jara", "जार्विस", "జార్విస్")
SLEEP_WORDS = ("go to sleep", "sleep mode", "standby", "स्लीप", "పడుకో")
EXIT_WORDS = ("exit", "quit", "stop", "bye", "goodbye", "close", "बंद", "ముగించు")

MESSAGES = {
    "en": {
        "ready": "System ready. Say hello Jarvis to activate me.",
        "wake": "Hello sir, what can I do for you?",
        "sleep": "Okay sir. I am waiting in standby mode.",
        "unknown": "I did not understand. Say help to see commands.",
        "recognition_error": "Speech recognition service is not available right now.",
        "email_cfg": "Email is not configured. Add gmail_password in user_config.py",
        "ask_recipient": "Tell recipient name or email.",
        "ask_subject": "Tell subject.",
        "ask_message": "Tell message.",
        "sent": "Email sent to {x}",
        "email_fail": "Could not send email.",
        "task_added": "Task added: {x}",
        
        "task_cancel": "Task cancelled.",
        "ask_task": "What task should I add?",
        "no_task": "No tasks found.",
        "count_task": "You have {x} tasks.",
        "clear_ask": "Say yes to clear all tasks.",
        "cleared": "All tasks cleared.",
        "ask_google": "What should I search on Google?",
        "ask_youtube": "What should I search on YouTube?",
        "search_google": "Searching Google for {x}",
        "search_youtube": "Searching YouTube for {x}",
        "search_wiki": "According to Wikipedia.",
        "open": "Opening {x}",
        "ask_whatsapp_msg": "Tell the WhatsApp message.",
        "ask_whatsapp_num": "Tell the phone number or say default.",
        "whatsapp_ready": "I opened WhatsApp with your message. Press Enter to send.",
        "shot_saved": "Screenshot saved: {x}",
        "shot_fail": "Screenshot feature is unavailable. Install pyautogui and pillow.",
        "note_ask": "Tell me the note.",
        "note_saved": "Note saved.",
        "no_note": "No saved notes.",
        "calc_ask": "Tell the expression to calculate.",
        "calc_ans": "The answer is {x}",
        "calc_err": "I could not calculate that.",
        "goodbye": "Goodbye sir.",
    },
    "hi": {
        "ready": "सिस्टम तैयार है। हेलो जार्विस बोलकर शुरू करें।",
        "wake": "हेलो सर, मैं आपकी क्या मदद कर सकता हूं?",
        "sleep": "ठीक है सर, मैं स्टैंडबाय मोड में हूं।",
        "unknown": "मैं समझ नहीं पाया। कमांड देखने के लिए हेल्प बोलिए।",
        "recognition_error": "अभी स्पीच सेवा उपलब्ध नहीं है।",
        "email_cfg": "ईमेल कॉन्फ़िगर नहीं है। user_config.py में gmail_password जोड़ें।",
        "ask_recipient": "रिसीवर नाम या ईमेल बताइए।",
        "ask_subject": "सब्जेक्ट बताइए।",
        "ask_message": "मैसेज बताइए।",
        "sent": "{x} को ईमेल भेज दिया।",
        "email_fail": "ईमेल भेज नहीं पाया।",
        "task_added": "टास्क जोड़ दिया: {x}",
        "task_cancel": "टास्क रद्द किया गया।",
        "ask_task": "कौन सा टास्क जोड़ना है?",
        "no_task": "कोई टास्क नहीं मिला।",
        "count_task": "आपके पास {x} टास्क हैं।",
        "clear_ask": "सभी टास्क हटाने के लिए yes बोलिए।",
        "cleared": "सभी टास्क हट गए।",
        "ask_google": "गूगल पर क्या खोजूं?",
        "ask_youtube": "यूट्यूब पर क्या खोजूं?",
        "search_google": "गूगल पर {x} खोज रहा हूं।",
        "search_youtube": "यूट्यूब पर {x} खोज रहा हूं।",
        "search_wiki": "विकिपीडिया के अनुसार।",
        "open": "{x} खोल रहा हूं।",
        "ask_whatsapp_msg": "व्हाट्सऐप मैसेज बताइए।",
        "ask_whatsapp_num": "फोन नंबर बताइए या default बोलिए।",
        "whatsapp_ready": "मैंने मैसेज के साथ व्हाट्सऐप खोल दिया है। भेजने के लिए Enter दबाएं।",
        "shot_saved": "स्क्रीनशॉट सेव हो गया: {x}",
        "shot_fail": "स्क्रीनशॉट फीचर उपलब्ध नहीं है। pyautogui और pillow इंस्टॉल करें।",
        "note_ask": "नोट बताइए।",
        "note_saved": "नोट सेव हो गया।",
        "no_note": "कोई सेव नोट नहीं है।",
        "calc_ask": "कैल्कुलेशन बोलिए।",
        "calc_ans": "उत्तर है {x}",
        "calc_err": "यह कैलकुलेट नहीं कर पाया।",
        "goodbye": "गुडबाय सर।",
    },
    "te": {
        "ready": "సిస్టమ్ రెడీ. హలో జార్విస్ అని చెప్పండి.",
        "wake": "హలో సర్, మీకు నేను ఏమి చేయాలి?",
        "sleep": "సరే సర్, నేను స్టాండ్బైలో ఉంటాను.",
        "unknown": "నాకు అర్థం కాలేదు. హెల్ప్ అనండి.",
        "recognition_error": "స్పీచ్ సర్వీస్ ఇప్పుడు అందుబాటులో లేదు.",
        "email_cfg": "ఈమెయిల్ సెటప్ కాలేదు. user_config.py లో gmail_password జోడించండి.",
        "ask_recipient": "రిసీవర్ పేరు లేదా ఈమెయిల్ చెప్పండి.",
        "ask_subject": "సబ్జెక్ట్ చెప్పండి.",
        "ask_message": "మెసేజ్ చెప్పండి.",
        "sent": "{x} కు ఈమెయిల్ పంపించాను.",
        "email_fail": "ఈమెయిల్ పంపలేకపోయాను.",
        "task_added": "టాస్క్ జోడించాను: {x}",
        "task_cancel": "టాస్క్ రద్దు చేసాను.",
        "ask_task": "ఏ టాస్క్ జోడించాలి?",
        "no_task": "టాస్క్‌లు లేవు.",
        "count_task": "మీ వద్ద {x} టాస్క్‌లు ఉన్నాయి.",
        "clear_ask": "అన్ని టాస్క్‌లు తొలగించడానికి yes అనండి.",
        "cleared": "అన్ని టాస్క్‌లు తొలగించాను.",
        "ask_google": "గూగుల్‌లో ఏమి వెతకాలి?",
        "ask_youtube": "యూట్యూబ్‌లో ఏమి వెతకాలి?",
        "search_google": "గూగుల్‌లో {x} వెతుకుతున్నాను.",
        "search_youtube": "యూట్యూబ్‌లో {x} వెతుకుతున్నాను.",
        "search_wiki": "వికీపీడియా ప్రకారం.",
        "open": "{x} ఓపెన్ చేస్తున్నాను.",
        "ask_whatsapp_msg": "వాట్సాప్ మెసేజ్ చెప్పండి.",
        "ask_whatsapp_num": "ఫోన్ నంబర్ చెప్పండి లేదా default అనండి.",
        "whatsapp_ready": "మీ మెసేజ్‌తో వాట్సాప్ ఓపెన్ చేశాను. పంపడానికి Enter నొక్కండి.",
        "shot_saved": "స్క్రీన్‌షాట్ సేవ్ అయింది: {x}",
        "shot_fail": "స్క్రీన్‌షాట్ ఫీచర్ లేదు. pyautogui మరియు pillow ఇన్‌స్టాల్ చేయండి.",
        "note_ask": "నోట్ చెప్పండి.",
        "note_saved": "నోట్ సేవ్ అయ్యింది.",
        "no_note": "సేవ్ చేసిన నోట్లు లేవు.",
        "calc_ask": "లెక్క చెప్పండి.",
        "calc_ans": "జవాబు {x}",
        "calc_err": "లెక్క చేయలేకపోయాను.",
        "goodbye": "గుడ్‌బై సర్.",
    },
}

try:
    import user_config
    GMAIL_APP_PASSWORD = user_config.gmail_password
except ImportError:
    GMAIL_APP_PASSWORD = None

try:
    pygame.mixer.init()
except Exception:
    pass


def msg(key, **kwargs):
    text = MESSAGES.get(ACTIVE_LANG, MESSAGES["en"]).get(key, MESSAGES["en"][key])
    return text.format(**kwargs)


def detect_lang(text):
    if re.search(r"[\u0c00-\u0c7f]", text):
        return "te"
    if re.search(r"[\u0900-\u097f]", text):
        return "hi"
    return "en"


def speak(text):
    if not text:
        return
    print(f"\n{ASSISTANT_NAME}: {text}")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            path = fp.name
        tts = gTTS(text=text, lang=ACTIVE_LANG if ACTIVE_LANG in LANGS else "en", slow=False)
        tts.save(path)
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        os.unlink(path)
    except Exception as e:
        print(f"[Speech Error: {e}]")


def listen(timeout=8, phrase_time_limit=None):
    r = sr.Recognizer()
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.8
    try:
        with sr.Microphone() as source:
            print("\nListening...")
            r.adjust_for_ambient_noise(source, duration=0.6)
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        print("Recognizing...")
        for code in (LANG_STT.get(ACTIVE_LANG), "en-IN", "hi-IN", "te-IN"):
            if not code:
                continue
            try:
                q = r.recognize_google(audio, language=code).strip().lower()
                q = re.sub(r"\s+", " ", q)
                print(f"You: {q}")
                return q, detect_lang(q)
            except sr.UnknownValueError:
                pass
        return None, None
    except sr.WaitTimeoutError:
        return None, None
    except sr.RequestError:
        speak(msg("recognition_error"))
        return None, None
    except Exception:
        return None, None


def ask(key, timeout=10):
    speak(msg(key))
    return listen(timeout=timeout)[0]


def resolve_email(text):
    mapping = {"aniket": DEFAULT_RECIPIENT, "me": DEFAULT_RECIPIENT, "myself": DEFAULT_RECIPIENT}
    if not text:
        return DEFAULT_RECIPIENT
    for k, v in mapping.items():
        if k in text:
            return v
    clean = text.replace(" at ", "@").replace(" dot ", ".").replace(" ", "")
    clean = re.sub(r"[^a-z0-9@._+-]", "", clean)
    return clean if "@" in clean and "." in clean else DEFAULT_RECIPIENT


def send_email():
    if not GMAIL_APP_PASSWORD:
        speak(msg("email_cfg"))
        return
    try:
        to_email = resolve_email(ask("ask_recipient", 10))
        subject = ask("ask_subject", 12)
        body = ask("ask_message", 18)
        if not subject or not body:
            speak(msg("task_cancel"))
            return
        mail = EmailMessage()
        mail["From"] = SENDER_EMAIL
        mail["To"] = to_email
        mail["Subject"] = subject
        mail.set_content(body)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
            server.send_message(mail)
        speak(msg("sent", x=to_email))
    except Exception as e:
        print(f"Email Error: {e}")
        speak(msg("email_fail"))


def add_task(req):
    text = req.replace("add task", "").replace("new task", "").replace("create task", "").strip()
    if not text:
        text = ask("ask_task", 10)
    if not text:
        speak(msg("task_cancel"))
        return
    with open(TODO_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")
    speak(msg("task_added", x=text))


def list_tasks():
    if not os.path.exists(TODO_FILE):
        speak(msg("no_task"))
        return
    with open(TODO_FILE, "r", encoding="utf-8") as f:
        rows = [x.strip() for x in f if x.strip()]
    if not rows:
        speak(msg("no_task"))
        return
    speak(msg("count_task", x=len(rows)))
    for i, item in enumerate(rows, 1):
        speak(f"{i}. {item}")


def clear_tasks():
    if not os.path.exists(TODO_FILE):
        speak(msg("no_task"))
        return
    speak(msg("clear_ask"))
    ans = listen(timeout=8)[0]
    if ans and ("yes" in ans or "haan" in ans or "avunu" in ans):
        os.remove(TODO_FILE)
        speak(msg("cleared"))


def add_note(req):
    note = req.replace("add note", "").replace("remember this", "").strip()
    if not note:
        note = ask("note_ask", 10)
    if not note:
        speak(msg("task_cancel"))
        return
    with open(NOTE_FILE, "a", encoding="utf-8") as f:
        f.write(note + "\n")
    speak(msg("note_saved"))


def read_notes():
    if not os.path.exists(NOTE_FILE):
        speak(msg("no_note"))
        return
    with open(NOTE_FILE, "r", encoding="utf-8") as f:
        notes = [x.strip() for x in f if x.strip()]
    if not notes:
        speak(msg("no_note"))
        return
    for i, note in enumerate(notes, 1):
        speak(f"{i}. {note}")


def safe_eval(expr):
    ops = {
        ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b, ast.Div: lambda a, b: a / b,
        ast.Pow: lambda a, b: a**b, ast.Mod: lambda a, b: a % b,
        ast.USub: lambda a: -a, ast.UAdd: lambda a: +a
    }
    def run(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in ops:
            return ops[type(node.op)](run(node.left), run(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in ops:
            return ops[type(node.op)](run(node.operand))
        raise ValueError("bad")
    return run(ast.parse(expr, mode="eval").body)


def calculate(req):
    expr = req.replace("calculate", "").replace("what is", "").replace("solve", "").strip()
    if not expr:
        expr = ask("calc_ask", 10)
    if not expr:
        speak(msg("calc_err"))
        return
    expr = expr.replace("plus", "+").replace("minus", "-").replace("into", "*").replace("x", "*").replace("divided by", "/")
    expr = re.sub(r"[^0-9+\-*/().% ]", "", expr).strip()
    try:
        speak(msg("calc_ans", x=safe_eval(expr)))
    except Exception:
        speak(msg("calc_err"))


def search_google(req):
    q = req.replace("google search", "").replace("search", "").replace("google", "").strip()
    if not q:
        q = ask("ask_google", 10)
    if q:
        webbrowser.open(f"https://www.google.com/search?q={quote_plus(q)}")
        speak(msg("search_google", x=q))


def search_youtube(req):
    q = req.replace("youtube search", "").replace("search", "").replace("youtube", "").strip()
    if not q:
        q = ask("ask_youtube", 10)
    if q:
        webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(q)}")
        speak(msg("search_youtube", x=q))


def search_wikipedia(req):
    q = req.replace("wikipedia", "").replace("search", "").strip()
    if not q:
        q = ask("search_wiki", 10)
    if not q:
        return
    try:
        speak(msg("search_wiki"))
        speak(wikipedia.summary(q, sentences=3))
    except Exception:
        speak(msg("unknown"))


def normalize_phone(text):
    if not text:
        return re.sub(r"\D", "", WHATSAPP_PHONE)
    low = text.lower().strip()
    if "default" in low or "my number" in low or "mera" in low:
        return re.sub(r"\D", "", WHATSAPP_PHONE)
    digits = re.sub(r"\D", "", text)
    if not digits:
        return re.sub(r"\D", "", WHATSAPP_PHONE)
    if digits.startswith("0"):
        digits = digits.lstrip("0")
    if len(digits) == 10:
        digits = "91" + digits
    if text.strip().startswith("+"):
        return digits
    if len(digits) > 10 and not digits.startswith("91"):
        return digits
    return digits


def send_whatsapp_message():
    number_text = ask("ask_whatsapp_num", 10)
    message_text = ask("ask_whatsapp_msg", 18)
    if not message_text:
        speak(msg("task_cancel"))
        return
    number = normalize_phone(number_text)
    encoded = quote_plus(message_text)
    webbrowser.open(f"https://wa.me/{number}?text={encoded}")
    speak(msg("whatsapp_ready"))


def take_screenshot():
    if pyautogui is None:
        speak(msg("shot_fail"))
        return
    try:
        folder = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(folder, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(folder, f"screenshot_{stamp}.png")
        image = pyautogui.screenshot()
        image.save(path)
        speak(msg("shot_saved", x=path))
    except Exception:
        speak(msg("shot_fail"))


def open_targets(req):
    sites = {
        "youtube": "https://www.youtube.com",
        "facebook": "https://www.facebook.com",
        "instagram": "https://www.instagram.com",
        "google": "https://www.google.com",
        "github": "https://www.github.com",
        "twitter": "https://www.twitter.com",
        "linkedin": "https://www.linkedin.com",
    }
    apps = {"notepad": "notepad", "calculator": "calc", "paint": "mspaint", "cmd": "cmd"}
    if "whatsapp" in req:
        webbrowser.open(f"https://wa.me/{re.sub(r'\\D', '', WHATSAPP_PHONE)}")
        speak(msg("open", x="WhatsApp"))
        return True
    for k, u in sites.items():
        if k in req:
            webbrowser.open(u)
            speak(msg("open", x=k.title()))
            return True
    for k, app in apps.items():
        if k in req:
            subprocess.Popen(app)
            speak(msg("open", x=k.title()))
            return True
    return False


def tell_time_date_day(req):
    now = datetime.datetime.now()
    if "time" in req or "समय" in req or "సమయం" in req:
        speak(f"{now.strftime('%I:%M %p')}")
    elif "date" in req or "तारीख" in req or "తేదీ" in req:
        speak(f"{now.strftime('%d %B %Y')}")
    else:
        speak(f"{now.strftime('%A')}")


def tell_joke():
    speak(random.choice([
        "Why do programmers prefer dark mode? Because light attracts bugs.",
        "Why did the computer go to the doctor? It had a virus.",
        "Why was the math book sad? It had too many problems.",
    ]))


def show_help():
    print(
        "\nCOMMANDS:\n"
        "- hello jarvis / हेलो जार्विस / హలో జార్విస్\n"
        "- time/date/day\n"
        "- add task, read task, count task, clear task\n"
        "- add note, read notes\n"
        "- calculate 5 plus 8\n"
        "- send email\n"
        "- wikipedia, google search, youtube search\n"
        "- take screenshot\n"
        "- open youtube/github/whatsapp/notepad/calculator/paint/cmd\n"
        "- tell joke, play music\n"
        "- go to sleep, exit\n"
    )


def wake_mode():
    global ACTIVE_LANG
    while True:
        req, lang = listen(timeout=8, phrase_time_limit=4)
        if not req:
            continue
        ACTIVE_LANG = lang or ACTIVE_LANG
        if any(w in req for w in WAKE_WORDS):
            speak(msg("wake"))
            return


def handle(req):
    if "wikipedia" in req:
        search_wikipedia(req)
    elif "youtube search" in req or "search youtube" in req:
        search_youtube(req)
    elif "search" in req or "google search" in req:
        search_google(req)
    elif any(x in req for x in ("time", "date", "day", "समय", "तारीख", "సమయం", "తేదీ")):
        tell_time_date_day(req)
    elif any(x in req for x in ("add task", "new task", "create task", "टास्क", "టాస్క్")):
        add_task(req)
    elif any(x in req for x in ("read task", "list task", "show task")):
        list_tasks()
    elif "count task" in req or "how many task" in req:
        list_tasks()
    elif "clear task" in req:
        clear_tasks()
    elif any(x in req for x in ("add note", "remember this", "नोट", "నోట్")):
        add_note(req)
    elif any(x in req for x in ("read notes", "show notes", "नोट पढ़", "నోట్లు")):
        read_notes()
    elif any(x in req for x in ("calculate", "what is", "solve", "गणना", "లెక్క")):
        calculate(req)
    elif any(x in req for x in ("send email", "email", "mail", "ईमेल", "మెయిల్")):
        send_email()
    elif any(x in req for x in ("send whatsapp", "whatsapp message", "send message on whatsapp", "व्हाट्सऐप भेजो", "వాట్సాప్ మెసేజ్ పంపు")):
        send_whatsapp_message()
    elif any(x in req for x in ("take screenshot", "take a screenshot", "capture screen", "screen shot", "स्क्रीनशॉट", "స్క్రీన్‌షాట్")):
        take_screenshot()
    elif any(x in req for x in ("play music", "play song", "song", "गाना", "పాట")):
        webbrowser.open("https://www.youtube.com/watch?v=-IietMBSwiM")
    elif any(x in req for x in ("tell joke", "joke", "चुटकुला", "జోక్")):
        tell_joke()
    elif req.startswith("open"):
        if not open_targets(req):
            speak(msg("unknown"))
    elif "help" in req or "command" in req:
        show_help()
        speak("Help shown on screen.")
    elif any(x in req for x in SLEEP_WORDS):
        speak(msg("sleep"))
        return "sleep"
    elif any(x in req for x in EXIT_WORDS):
        speak(msg("goodbye"))
        return "exit"
    else:
        speak(msg("unknown"))
    return "ok"


def safe_quit():
    try:
        pygame.mixer.quit()
    except Exception:
        pass


def main_process():
    global ACTIVE_LANG
    print("JARVIS Voice Assistant started")
    speak(msg("ready"))
    while True:
        wake_mode()
        while True:
            req, lang = listen(timeout=10)
            if not req:
                continue
            ACTIVE_LANG = lang or ACTIVE_LANG
            status = handle(req)
            if status == "sleep":
                break
            if status == "exit":
                safe_quit()
                sys.exit(0)


if __name__ == "__main__":
    try:
        main_process()
    except KeyboardInterrupt:
        safe_quit()
        sys.exit(0)
    except Exception as e:
        print(f"Fatal Error: {e}")
        safe_quit()
        sys.exit(1)
