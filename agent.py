import os
import json
from typing import Dict, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
load_dotenv()


api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY is missing")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=api_key,
)
SYSTEM_PROMPT = """You are Airia, an expert email intelligence agent. You analyse emails and respond in strict JSON only — no markdown, no explanation, just the JSON object requested.

You are precise, professional, and always output valid JSON."""


def triage(email_id: str, sender: str, subject: str, body: str) -> Dict:
    prompt = f"""Analyse this email and return a JSON object with exactly these fields:
{{
  "email_id": "{email_id}",
  "priority": "urgent" | "normal" | "low",
  "category": "billing" | "meeting" | "support" | "contract" | "general",
  "summary_bullets": ["bullet 1", "bullet 2", "bullet 3"],
  "suggested_next_actions": ["action 1", "action 2"],
  "confidence": 0.0 to 1.0,
  "tags": ["tag1", "tag2"]
}}

Email:
From: {sender}
Subject: {subject}
Body: {body}

Return ONLY the JSON object."""

    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
    text = response.content.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)


def generate_reply(
    email_id: str,
    sender: str,
    subject: str,
    body: str,
    tone: str,
    user_name: str,
    org_name: str,
    extra_context: Optional[str] = None,
) -> Dict:
    context_line = f"\nExtra context: {extra_context}" if extra_context else ""
    prompt = f"""Write a {tone} email reply and return a JSON object with exactly these fields:
{{
  "email_id": "{email_id}",
  "reply_subject": "Re: ...",
  "reply_body": "full reply text here",
  "notes": ["optional note 1"]
}}

Original email:
From: {sender}
Subject: {subject}
Body: {body}
{context_line}

Sign off as {user_name} from {org_name}.
Tone: {tone}
Return ONLY the JSON object."""

    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
    text = response.content.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)


def extract_tasks(email_id: str, subject: str, body: str) -> List[Dict]:
    prompt = f"""Extract actionable tasks from this email and return a JSON object:
{{
  "tasks": [
    {{"title": "task description", "due": "YYYY-MM-DD or null", "owner": "Me"}}
  ]
}}

Email subject: {subject}
Email body: {body}

Return ONLY the JSON object."""

    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
    text = response.content.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text).get("tasks", [])


class agent:
    triage = staticmethod(triage)
    generate_reply = staticmethod(generate_reply)
    extract_tasks = staticmethod(extract_tasks)
