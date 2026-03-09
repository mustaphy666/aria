🤖 AIRIA
Track
Track 1 — Airia Everywhere	AI Engine
Google Gemini 2.5 Flash	Backend
FastAPI + Python	Extension
Chrome (Gmail)

Overview
Airia is an AI-powered email intelligence platform that meets users where they already work. Instead of switching to a separate tool, Airia embeds directly inside Gmail via a Chrome extension — providing real-time triage, AI-drafted replies, and automated task extraction without leaving your inbox.
Powered by Google Gemini 2.5 Flash and a two-agent pipeline, Airia analyses incoming emails and delivers actionable intelligence in seconds.

Key Features
🔍  Two-Agent AI Pipeline
Agent 1 — Email Analyzer: Classifies each email by priority (urgent/normal/low), category (billing/meeting/support/contract/general), extracts summary bullets, and suggests next actions with a confidence score.
Agent 2 — Reply Writer: Uses the analysis output to generate a contextually aware, tone-matched draft reply ready to send.
✨  One-Click "Draft with Airia" in Gmail
A button appears directly in the Gmail reply toolbar. One click grabs the email thread, calls the AI, and auto-fills the Gmail compose box with a ready-to-send draft.
🟥  Live Triage Labels
After analysis, colour-coded labels appear inline on the email — Priority, Category, and Confidence score — making urgency instantly visible without opening any panel.
✅  Auto Task Panel
Extracts actionable tasks from any email with due dates and owners. Integration buttons for Notion and Google Tasks are included for future workflow automation.
🔒  Privacy Guardrail
Before any AI call, the extension scans for sensitive content — passwords, OTPs, credit card numbers, banking details. If detected, draft generation is blocked and a warning is displayed, protecting user privacy.
📊  Live Dashboard
A real-time monitoring dashboard shows emails processed, priority breakdown, category stats, and a live activity feed — simulating a Slack #email-triage channel for demo purposes.

Architecture
Project Structure
File	Purpose
api.py	FastAPI backend — REST endpoints for triage, reply, tasks
agent.py	Gemini-powered AI agent — two-agent pipeline
schemas.py	Pydantic request/response models
storage.py	JSON file storage for inbox, drafts, triage results
sample.py	Sample email data for seeding the inbox
index.html	Clean HTML/JS frontend dashboard
ui.py	Streamlit UI (alternative interface)
airia-extension/	Chrome extension — Gmail integration

Chrome Extension Files
File	Purpose
manifest.json	Extension config — permissions, content scripts
content.js	Gmail DOM injection — Airia bar, buttons, results
content.css	Extension styling — dark theme UI
popup.html	Extension popup — API status indicator
popup.js	Popup logic — API health check

Setup & Installation
1. Prerequisites
•	Python 3.10+
•	Google Chrome browser
•	Google Gemini API key (free at aistudio.google.com)
2. Install Dependencies
pip install fastapi uvicorn langchain-google-genai langchain-core python-dateutil
3. Set Your API Key
Create a .env file in the project root:
GOOGLE_API_KEY=your-gemini-api-key-here
Or set it directly in your terminal (Windows):
set GOOGLE_API_KEY=your-gemini-api-key-here
4. Start the API Server
cd C:\Users\Administrator\aria
uvicorn api:app --reload
The API will be available at http://127.0.0.1:8000
5. Open the Dashboard
Open index.html in Chrome directly, or serve it with Python:
python -m http.server 5500
Then visit http://127.0.0.1:5500/index.html
6. Install the Chrome Extension
1.	Open Chrome and go to chrome://extensions
2.	Enable Developer Mode (top-right toggle)
3.	Click Load unpacked
4.	Select the airia-extension/ folder
5.	Open Gmail — the Airia bar appears inside any open email

API Endpoints
Method	Endpoint	Description
GET	/inbox	Returns all emails in the inbox
POST	/triage	Agent 1 — Analyse email: priority, category, summary, actions
POST	/reply	Agent 2 — Generate tone-matched draft reply
POST	/actions	Extract actionable tasks with due dates and owners

Demo Script (3 Minutes)
Follow this exact sequence for maximum impact with judges:
6.	Open Gmail in Chrome — point out the Airia bar already embedded at the top of the email
7.	Click "Analyse Email" — watch Step 1 light up, triage labels appear inline on the email in real time
8.	Click "Draft with Airia" — watch Step 2 light up, AI-generated reply appears
9.	Click "Open in Gmail Compose" — compose box auto-fills. Say: "ready to send in one click"
10.	Click "Extract Tasks" — show the task panel with Notion/Google Tasks buttons
11.	Open the Live Dashboard tab — show real-time stats and activity feed updating as you triage
12.	Bonus: open an email mentioning "password" or "OTP" — show the privacy guardrail blocking AI generation

Track 1 Alignment — Airia Everywhere
This project directly addresses the Track 1 theme of meeting users where they already are:
•	Gmail (live) — Chrome extension injects AI directly into the inbox UI
•	Web Dashboard — Real-time monitoring across all email activity
•	REST API — Custom API for integration into any workflow or platform
•	Roadmap — Outlook extension, Slack bot, WhatsApp agent (architecture is platform-agnostic)
