from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.db.database import get_db
from app.models import User, Role
from app.auth import get_current_user, RoleChecker
from app.services.ai import get_ai_chat_response, generate_seo_tags, generate_faq_list

router = APIRouter(prefix="/ai", tags=["AI Assistants"])

class ChatMessage(BaseModel):
    role: str # 'user' or 'assistant'
    content: str

class ChatPayload(BaseModel):
    messages: List[ChatMessage]

class SEOPayload(BaseModel):
    title: str
    body_content: str

class FAQPayload(BaseModel):
    service_name: str

@router.post("/chat")
def post_chat_response(
    payload: ChatPayload,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Get interactive AI styling or concierge guidance responsive to your role.
    """
    role_name = "Client"
    if current_user:
        # Resolve role
        db = next(get_db()) # inline resolve
        user_role = db.query(Role).filter(Role.id == current_user.role_id).first()
        if user_role:
            role_name = user_role.name

    serialized_msgs = [{"role": msg.role, "content": msg.content} for msg in payload.messages]
    response_text = get_ai_chat_response(serialized_msgs, role=role_name)
    return {"response": response_text}

@router.post("/chat-anonymous")
def post_chat_anonymous(payload: ChatPayload):
    """
    Public website visitor chatbot endpoint.
    """
    serialized_msgs = [{"role": msg.role, "content": msg.content} for msg in payload.messages]
    response_text = get_ai_chat_response(serialized_msgs, role="Client")
    return {"response": response_text}

@router.post("/seo-generator")
def post_seo_generator(
    payload: SEOPayload,
    current_user: User = Depends(RoleChecker(["Admin", "Designer"]))
):
    """
    Generate dynamic meta titles, descriptions, OpenGraph headers, and Schema Markups.
    """
    return generate_seo_tags(payload.title, payload.body_content)

@router.post("/faq-generator")
def post_faq_generator(
    payload: FAQPayload,
    current_user: User = Depends(RoleChecker(["Admin", "Designer"]))
):
    """
    Generate customizable FAQ schemas for services pages.
    """
    return generate_faq_list(payload.service_name)
