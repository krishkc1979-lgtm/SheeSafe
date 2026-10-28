import os
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

BASE = os.path.dirname(os.path.abspath(__file__))

# Static directory mapping
static_dir = os.path.join(BASE, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

CONTACTS = [
    {"name": "Emergency (Police / Ambulance)", "number": "112", "note": "Immediate danger"},
    {"name": "Women Helpline", "number": "181", "note": "24x7, free"},
    {"name": "CHILDLINE", "number": "1098", "note": "For anyone under 18"},
    {"name": "Police", "number": "100", "note": "Report a crime"},
    {"name": "Tele-MANAS (mental health)", "number": "14416", "note": "Free counselling"},
]

LEVEL_RANK = {"low": 1, "medium": 2, "high": 3, "emergency": 4}

RULES = [
    {
        "key": "self_harm", "title": "Feeling very low / unsafe with yourself", "level": "emergency",
        "words": ["suicide", "kill myself", "end my life", "want to die", "hurt myself", "no reason to live", "marna chahti", "jaan de"],
        "reply": "I'm really glad you told me. What you feel matters, and you do not have to carry this alone. Please reach a trusted adult or a helpline right now - they are there to listen.",
        "steps": ["Go to a trusted adult near you (teacher, counsellor, parent) right now", "Call Tele-MANAS 14416 or CHILDLINE 1098 - free and kind", "Stay in a place with other people until help comes"],
    },
    {
        "key": "abuse", "title": "Unsafe touch or abuse", "level": "emergency",
        "words": ["touched me", "touching me", "molest", "rape", "forced me", "sexual", "inappropriate touch", "bad touch", "abused", "abuse", "beats me", "hits me", "beat me", "chhua", "galat tarike se"],
        "reply": "Thank you for trusting me. What happened is NOT your fault, and you deserve to be safe. This needs a real person to help you right away.",
        "steps": ["Move to a safe place with people around you", "Tell a trusted adult - a teacher, counsellor, parent or relative", "Call CHILDLINE 1098 or Women Helpline 181 (free)", "You can call 112 if you are in danger right now"],
    },
    {
        "key": "danger_now", "title": "Danger right now", "level": "emergency",
        "words": ["following me right now", "outside my", "locked me", "trapped", "threatened me", "threatening me", "knife", "he is here", "kidnap", "is chasing me"],
        "reply": "Your safety comes first. Please get to a safe, crowded place and call for help right now.",
        "steps": ["Call 112 immediately", "Go to a shop, guard, teacher or any group of people", "Share your live location with a trusted person"],
    },
    {
        "key": "blackmail", "title": "Blackmail or leaked photos", "level": "high",
        "words": ["blackmail", "morphed", "leaked", "threatens to post", "threatening to share", "fake nude", "viral my photo", "send money or"],
        "reply": "This is not your fault - the person blackmailing is the one doing wrong. Do not pay or send anything. A trusted adult can help stop this safely.",
        "steps": ["Do NOT reply or send anything more", "Take screenshots as proof (do not delete chats)", "Tell a trusted adult and report on cybercrime.gov.in or call 1930", "Block and report the account on the app"],
    },
    {
        "key": "stalking", "title": "Being followed or watched", "level": "high",
        "words": ["following me", "follows me", "stalk", "watching me", "waiting outside", "chases me", "peecha", "pichha"],
        "reply": "Feeling followed is scary, and your feelings are valid. You should not have to handle this alone.",
        "steps": ["Stay in busy, well-lit places and avoid walking alone", "Tell a trusted adult or the school authority today", "Note the time, place and what the person looks like", "Call 112 if you feel in danger"],
    },
    {
        "key": "harassment", "title": "Harassment or uncomfortable behaviour", "level": "high",
        "words": ["harass", "eve teas", "comment on my body", "comments on my body", "staring", "whistle", "uncomfortable around", "makes me uncomfortable", "touch me", "bad comments", "teased me badly"],
        "reply": "I'm sorry this happened. You have every right to feel safe, and what you feel is valid. This is not your fault.",
        "steps": ["Stay near people you trust", "Write down what happened, when and where (only for you)", "Tell a trusted teacher, counsellor or parent", "Women Helpline 181 can guide you if you want to talk first"],
    },
    {
        "key": "cyberbullying", "title": "Online bullying", "level": "medium",
        "words": ["fake account", "online", "instagram", "whatsapp", "snapchat", "group chat", "dm ", "screenshot", "cyber", "trolled", "troll"],
        "reply": "Being targeted online can really hurt. It is not your fault, and you can take your power back step by step.",
        "steps": ["Do not reply - save screenshots as proof", "Block and report the account", "Tell a trusted adult or school counsellor", "For serious cases, report on cybercrime.gov.in"],
    },
    {
        "key": "bullying", "title": "Bullying or exclusion", "level": "medium",
        "words": ["bully", "bullied", "made fun", "mocking", "mock me", "excluded", "nobody talks", "rumour", "rumor", "gang up", "ignored", "body shaming", "teasing", "tease me", "laugh at me"],
        "reply": "That sounds painful, and I'm glad you shared it. Nobody deserves to be treated like that.",
        "steps": ["Stay with friends you feel safe with", "Write down what happened and who was there", "Talk to a teacher or counsellor you trust", "You can ask the school to keep your name private"],
    },
    {
        "key": "emotional", "title": "Feeling anxious or low", "level": "low",
        "words": ["sad", "anxious", "scared", "afraid", "stress", "cry", "lonely", "panic", "tension", "dar lag", "worried", "nervous", "upset", "pressure"],
        "reply": "Thank you for opening up. It is okay to feel this way, and you are not alone.",
        "steps": ["Take 5 slow breaths: in for 4, out for 6", "Talk to a friend or family member you trust", "A school counsellor can help - it is private and kind", "Tele-MANAS 14416 is free if you want to talk"],
    },
]

DEFAULT = {
    "key": "checkin", "title": "Let's understand together", "level": "low",
    "reply": "I'm here and I'm listening. Tell me a little more about what happened - who, where, or how it made you feel. Share only what you are comfortable with.",
    "steps": ["Take your time - there is no rush", "You can describe it in your own words", "Nothing you type here is saved"],
}

def triage(text: str) -> dict:
    t = " " + text.lower() + " "
    best, best_rank = None, 0
    for rule in RULES:
        if any(w in t for w in rule["words"]):
            r = LEVEL_RANK[rule["level"]]
            if r > best_rank:
                best, best_rank = rule, r
    return best or DEFAULT

class ChatIn(BaseModel):
    message: str

@app.get("/")
def serve_home():
    # Dono locations check karega
    p1 = os.path.join(BASE, "index.html")
    p2 = os.path.join(BASE, "static", "index.html")
    if os.path.exists(p1):
        return FileResponse(p1)
    if os.path.exists(p2):
        return FileResponse(p2)
    return HTMLResponse("<h1>SheSafe backend running, HTML missing in root!</h1>")

@app.post("/api/chat")
def chat(payload: ChatIn):
    rule = triage(payload.message)
    level = rule["level"]
    return {
        "category": rule["key"],
        "title": rule["title"],
        "level": level,
        "reply": rule["reply"],
        "steps": rule["steps"],
        "contacts": CONTACTS if LEVEL_RANK[level] >= 3 else [],
        "trusted_adult": LEVEL_RANK[level] >= 2,
        "emergency": level == "emergency",
    }

@app.get("/api/helplines")
def helplines():
    return CONTACTS

# 1. Health check ke liye dedicated route
@app.get("/health")
def health_check():
    return JSONResponse(status_code=200, content={"status": "ok"})

# 2. Replit ke default root health check ke liye instant response
@app.get("/")
def read_root():
    # Agar static HTML serve karna hai:
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    return JSONResponse(status_code=200, content={"status": "online", "app": "SheSafe"})
