# from fastapi import FastAPI
# from schemas import EmailIn, TriageOut, ReplyIn, ReplyOut, ActionsOut
# from agent import agent
# from storage import storage
# from sample import SAMPLE_EMAILS

# app = FastAPI(title="Airia Track 1 Email Agent", version="1.0.0")

# @app.on_event("startup")
# def seed_data():
#     # Seed sample inbox if empty
#     db = storage.read_inbox()
#     if not db.get("emails"):
#         for e in SAMPLE_EMAILS:
#             storage.upsert_email(e)

# @app.get("/inbox")
# def get_inbox():
#     return storage.read_inbox().get("emails", [])

# @app.post("/triage", response_model=TriageOut)
# def triage_email(payload: EmailIn):
#     storage.upsert_email(payload.model_dump())
#     result = agent.triage(payload.email_id, payload.sender, payload.subject, payload.body)
#     storage.save_triage(result)
#     return result

# @app.post("/reply", response_model=ReplyOut)
# def reply_email(payload: ReplyIn):
#     storage.upsert_email({
#         "email_id": payload.email_id,
#         "sender": payload.sender,
#         "subject": payload.subject,
#         "body": payload.body,
#     })
#     result = agent.generate_reply(
#         email_id=payload.email_id,
#         sender=payload.sender,
#         subject=payload.subject,
#         body=payload.body,
#         tone=payload.tone,
#         user_name=payload.user_name,
#         org_name=payload.org_name,
#         extra_context=payload.extra_context,
#     )
#     storage.save_draft(result)
#     return result

# @app.post("/actions", response_model=ActionsOut)
# def actions(payload: EmailIn):
#     tasks = agent.extract_tasks(payload.email_id, payload.subject, payload.body)
#     storage.save_tasks(payload.email_id, tasks)
#     return {"email_id": payload.email_id, "tasks": tasks}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas import EmailIn, TriageOut, ReplyIn, ReplyOut, ActionsOut
from agent import agent
from storage import storage
from sample import SAMPLE_EMAILS

app = FastAPI(title="Airia Track 1 Email Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def seed_data():
    # Seed sample inbox if empty
    db = storage.read_inbox()
    if not db.get("emails"):
        for e in SAMPLE_EMAILS:
            storage.upsert_email(e)

@app.get("/inbox")
def get_inbox():
    return storage.read_inbox().get("emails", [])

@app.post("/triage", response_model=TriageOut)
def triage_email(payload: EmailIn):
    storage.upsert_email(payload.model_dump())
    result = agent.triage(payload.email_id, payload.sender, payload.subject, payload.body)
    storage.save_triage(result)
    return result

@app.post("/reply", response_model=ReplyOut)
def reply_email(payload: ReplyIn):
    storage.upsert_email({
        "email_id": payload.email_id,
        "sender": payload.sender,
        "subject": payload.subject,
        "body": payload.body,
    })
    result = agent.generate_reply(
        email_id=payload.email_id,
        sender=payload.sender,
        subject=payload.subject,
        body=payload.body,
        tone=payload.tone,
        user_name=payload.user_name,
        org_name=payload.org_name,
        extra_context=payload.extra_context,
    )
    storage.save_draft(result)
    return result

@app.post("/actions", response_model=ActionsOut)
def actions(payload: EmailIn):
    tasks = agent.extract_tasks(payload.email_id, payload.subject, payload.body)
    storage.save_tasks(payload.email_id, tasks)
    return {"email_id": payload.email_id, "tasks": tasks}