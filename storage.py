import json
import os
from typing import Any, Dict, List
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

INBOX_PATH = os.path.join(DATA_DIR, "inbox.json")
MEMORY_PATH = os.path.join(DATA_DIR, "memory.json")

def _ensure_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(INBOX_PATH):
        with open(INBOX_PATH, "w", encoding="utf-8") as f:
            json.dump({"emails": [], "drafts": [], "triage": [], "tasks": []}, f, indent=2)
    if not os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump({"sender_preferences": {}}, f, indent=2)

def read_inbox() -> Dict[str, Any]:
    _ensure_files()
    with open(INBOX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def write_inbox(payload: Dict[str, Any]) -> None:
    _ensure_files()
    with open(INBOX_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

def read_memory() -> Dict[str, Any]:
    _ensure_files()
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def write_memory(payload: Dict[str, Any]) -> None:
    _ensure_files()
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

def upsert_email(email: Dict[str, Any]) -> None:
    db = read_inbox()
    emails = db.get("emails", [])
    existing = next((e for e in emails if e["email_id"] == email["email_id"]), None)
    if existing:
        existing.update(email)
    else:
        emails.append(email)
    db["emails"] = emails
    write_inbox(db)

def save_triage(triage: Dict[str, Any]) -> None:
    db = read_inbox()
    triages = db.get("triage", [])
    triages = [t for t in triages if t.get("email_id") != triage.get("email_id")]
    triage["created_at"] = datetime.utcnow().isoformat()
    triages.append(triage)
    db["triage"] = triages
    write_inbox(db)

def save_draft(draft: Dict[str, Any]) -> None:
    db = read_inbox()
    drafts = db.get("drafts", [])
    draft["created_at"] = datetime.utcnow().isoformat()
    drafts.append(draft)
    db["drafts"] = drafts
    write_inbox(db)

def save_tasks(email_id: str, tasks: List[Dict[str, Any]]) -> None:
    db = read_inbox()
    all_tasks = db.get("tasks", [])
    for t in tasks:
        t["email_id"] = email_id
        t["created_at"] = datetime.utcnow().isoformat()
        all_tasks.append(t)
    db["tasks"] = all_tasks
    write_inbox(db)

class storage:
    read_inbox = staticmethod(read_inbox)
    write_inbox = staticmethod(write_inbox)
    read_memory = staticmethod(read_memory)
    write_memory = staticmethod(write_memory)
    upsert_email = staticmethod(upsert_email)
    save_triage = staticmethod(save_triage)
    save_draft = staticmethod(save_draft)
    save_tasks = staticmethod(save_tasks)