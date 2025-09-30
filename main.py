from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Body, HTTPException, status
from deep_translator import GoogleTranslator
from datetime import datetime
from database import collection, init_indexes
from models import TranslationRequest, TranslationResponse
from starlette.concurrency import run_in_threadpool
from typing import Any, Dict, List

app = FastAPI()

origins = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000"
]

# Enable CORS so your React app can talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db():
    await init_indexes()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Language Translator API"}


# ✅ Recursive translator
async def translate_recursive(obj: Any, target_language: str) -> Any:
    if isinstance(obj, dict):
        return {k: await translate_recursive(v, target_language) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [await translate_recursive(i, target_language) for i in obj]
    elif isinstance(obj, str):
        return await run_in_threadpool(
            GoogleTranslator(source="auto", target=target_language).translate,
            obj
        )
    else:
        return obj


@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest = Body(...)):
    try:
        text_dict = request.text
        target_language = request.target_language
        user_info = request.user.dict()

        # ✅ Use recursive translation
        translated_texts = await translate_recursive(text_dict, target_language)

        translation_data = TranslationResponse(
            original_text=text_dict,
            translated_text=translated_texts,
            source_language="auto",
            target_language=target_language,
            timestamp=datetime.utcnow()
        )
        
        # Saving translation to MongoDB
        db_data = translation_data.dict()
        db_data["user_data"] = user_info
        db_data["timestamp"] = datetime.utcnow().isoformat()
        result = await collection.insert_one(db_data)

        if result.acknowledged:
            return translation_data
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save translation to database."
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Translation failed: {str(e)}"
        )
