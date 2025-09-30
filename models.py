# This file is like a blueprint for your data.
# It defines what a User looks like,
# what a TranslationRequest should contain,
# And what the final TranslationResponse.


from pydantic import BaseModel, Field, EmailStr
from typing import Any, Dict
from datetime import datetime

class User(BaseModel):
    name: str
    email: EmailStr

class TranslationRequest(BaseModel):
    text: Dict[str, Any]
    target_language: str
    user: User

class TranslationResponse(BaseModel):
    original_text: Dict[str, Any]
    translated_text: Dict[str, Any]
    source_language: str
    target_language: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)