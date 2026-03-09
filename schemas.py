from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class EmailIn(BaseModel):
    email_id: str
    sender: str
    subject: str
    body: str

class TriageOut(BaseModel):
    email_id: str
    priority: str = Field(..., description="urgent|normal|low")
    category: str = Field(..., description="billing|meeting|support|contract|general")
    summary_bullets: List[str]
    suggested_next_actions: List[str]
    confidence: float = Field(..., ge=0.0, le=1.0)
    tags: List[str] = []

class ReplyIn(BaseModel):
    email_id: str
    sender: str
    subject: str
    body: str
    tone: str = Field(default="professional", description="professional|friendly|direct")
    user_name: str = "Mustapha"
    org_name: str = "My Team"
    extra_context: Optional[str] = None

class ReplyOut(BaseModel):
    email_id: str
    reply_subject: str
    reply_body: str
    notes: List[str] = []

class ActionItem(BaseModel):
    title: str
    due: Optional[str] = None  # ISO date string
    owner: str = "Me"

class ActionsOut(BaseModel):
    email_id: str
    tasks: List[ActionItem]