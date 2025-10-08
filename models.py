# This file is like a blueprint for your data.
# It defines what a User looks like,
# what a TranslationRequest should contain,
# And what the final TranslationResponse.


from pydantic import BaseModel, Field, EmailStr
# This line imports the main tools from the Pydantic library:
# - BaseModel: The basic building block for all your data blueprints (schemas).
# - Field: A tool to add extra details, like a default value.
# - EmailStr: A special type that ensures a string is a valid email address.

from typing import Any, Dict
# This imports useful tools from Python's 'typing' system:
# - Any: Means "could be any type of data."
# - Dict: Stands for 'Dictionary' (a collection of key-value pairs).

from datetime import datetime
# This imports the 'datetime' tool, which is used to record a specific moment in time.

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
