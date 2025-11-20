# storage.py
import json
import os
from datetime import datetime

USERS_FILE = "users.json"
DATA_FILE = "data.json"

# ---------- USER STORAGE ----------

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("users", [])
    except Exception:
        return []

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump({"users": users}, f, ensure_ascii=False, indent=2)

def get_user(email: str):
    email = email.lower().strip()
    for u in load_users():
        if u["email"] == email:
            return u
    return None

def create_user(email: str, password_hash: str) -> bool:
    """
    Create a new user. Returns False if email already exists.
    """
    email = email.lower().strip()
    users = load_users()
    if any(u["email"] == email for u in users):
        return False
    users.append({"email": email, "password_hash": password_hash})
    save_users(users)
    return True

# ---------- PER-USER DATA STORAGE ----------

def _default_data():
    # Structure: { "users": { "email": { listing_details: str, conversations: [] } } }
    return {"users": {}}

def load_data():
    if not os.path.exists(DATA_FILE):
        return _default_data()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return _default_data()

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _ensure_user_data(data, email: str):
    email = email.lower().strip()
    if "users" not in data:
        data["users"] = {}
    if email not in data["users"]:
        data["users"][email] = {"listing_details": "", "conversations": []}
    return data["users"][email]

def save_listing_details(email: str, text: str):
    email = email.lower().strip()
    data = load_data()
    udata = _ensure_user_data(data, email)
    udata["listing_details"] = text
    save_data(data)

def get_listing_details(email: str) -> str:
    email = email.lower().strip()
    data = load_data()
    if "users" not in data or email not in data["users"]:
        return ""
    return data["users"][email].get("listing_details", "")

def add_conversation(email: str, guest_message: str, reply: str, tone: str, template_type: str):
    email = email.lower().strip()
    data = load_data()
    udata = _ensure_user_data(data, email)
    convo = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "guest_message": guest_message,
        "reply": reply,
        "tone": tone,
        "template_type": template_type,
    }
    udata["conversations"].insert(0, convo)  # newest first
    # Keep only the last 10 per user
    udata["conversations"] = udata["conversations"][:10]
    save_data(data)

def get_recent_conversations(email: str, limit: int = 3):
    email = email.lower().strip()
    data = load_data()
    if "users" not in data or email not in data["users"]:
        return []
    return data["users"][email].get("conversations", [])[:limit]