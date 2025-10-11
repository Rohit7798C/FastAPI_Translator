from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Body, HTTPException, status
# Imports the main tools from the FastAPI framework:
# - FastAPI: The main class to create your web application.
# - Body, HTTPException, status: Tools for handling incoming data, errors, and status codes.

from deep_translator import GoogleTranslator
# Imports the tool that connects to Google's translation service.

from datetime import datetime
# Imports the tool to get the current date and time (for timestamps)

from database import collection, init_indexes
# Imports the collection (the MongoDB storage folder) and the index setup function
# from the 'database.py' file

from models import TranslationRequest, TranslationResponse
# Imports the data blueprints (User, TranslationRequest, TranslationResponse)
# from the 'models.py' file.

from starlette.concurrency import run_in_threadpool
# Imports a utility to safely run slow, non-asynchronous code (like the translation)
# without freezing the rest of the FastAPI application.

from typing import Any, Dict, List
# Imports types used for defining function inputs (Any, Dictionary, List).

app = FastAPI()
# This creates the actual web application instance.

origins = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000"
]
# Defines a list of web addresses (origins) that are allowed to talk to this API.


# Enable CORS so your React app can talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Applies the security permissions (CORS) using the list of allowed origins.
# This is what lets your frontend website communicate with this backend API.


@app.on_event("startup")
async def startup_db():
    await init_indexes()
# This tells FastAPI: "When you start up, run the init_indexes function (from database.py)
# to make sure the database is ready and has fast search indexes."

@app.get("/")
def read_root():
    return {"message": "Welcome to the Language Translator API"}
# This creates a simple web address (the root address '/') that, when visited,
# just returns a welcome message. This is a basic health check for the API.


# ✅ Recursive translator
async def translate_recursive(obj: Any, target_language: str) -> Any:
# This defines a special function that can translate text even if it's buried
# inside a complex structure of Dictionaries and Lists.
    if isinstance(obj, dict):
        return {k: await translate_recursive(v, target_language) for k, v in obj.items()}
        # If the input is a Dictionary, it calls itself (recursively) on every single value.
    elif isinstance(obj, list):
        return [await translate_recursive(i, target_language) for i in obj]
        # If the input is a List, it calls itself (recursively) on every single item in the list.
    elif isinstance(obj, str):
        return await run_in_threadpool(
            GoogleTranslator(source="auto", target=target_language).translate,
            obj
        )
            # If the input is a String (actual text!), this is where the translation happens:
            # 1. It creates the GoogleTranslator, setting the source language to 'auto-detect'.
            # 2. It runs the '.translate(obj)' method using run_in_threadpool to keep the API fast.
    else:
        return obj
        # If the input is not a dict, list, or string (e.g., a number), it just returns it unchanged.


@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest = Body(...)):
    try:
        # This starts a 'try block' to catch any errors that might occur during the process.
        text_dict = request.text
        target_language = request.target_language
        user_info = request.user.dict()
        # It unpacks the data from the incoming request for easier use.

        # ✅ Use recursive translation
        translated_texts = await translate_recursive(text_dict, target_language)
        # The actual translation is performed by calling the recursive function.

        translation_data = TranslationResponse(
            original_text=text_dict,
            translated_text=translated_texts,
            source_language="auto",
            target_language=target_language,
            timestamp=datetime.utcnow()
        )
        # It creates a new TranslationResponse object, filling it with the results.

        # Saving translation to MongoDB
        db_data = translation_data.dict()
        db_data["user_data"] = user_info
        db_data["timestamp"] = datetime.utcnow().isoformat()
        # It prepares the data for the database, adding the user information and formatting the timestamp.

        result = await collection.insert_one(db_data)
        # This line saves the complete translation record into the MongoDB database.

        if result.acknowledged:
            return translation_data
        # If the save operation was successful, it returns the TranslationResponse object (the final data to the user).

        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save translation to database."
            )
        # If the save failed for some reason, it sends back a server error.
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Translation failed: {str(e)}"
            )
        # If any other error occurs (like bad input or a translation error), it sends back a 'Bad Request' error message
