from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Optional, Dict
from pydantic import BaseModel
import logging
import io
from ..services.chat_service import chat_service
from .auth import get_current_user
from ..middleware.rate_limiter import default_limiter, strict_limiter

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    message: str
    model_name: Optional[str] = None

class TextToSpeech(BaseModel):
    text: str

@router.post("/text")
async def chat_text(
    message: ChatMessage,
    current_user: Dict = Depends(get_current_user),
    _: None = Depends(default_limiter())
):
    """
    Process text input and return AI response
    """
    try:
        response = await chat_service.process_text_input(
            text=message.message,
            user_id=str(current_user["id"]),
            model_name=message.model_name or current_user.get("modelName")
        )
        
        return {
            "success": True,
            "data": response
        }
    except Exception as e:
        logger.error(f"Error in chat_text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice")
async def chat_voice(
    audio: UploadFile = File(...),
    model_name: Optional[str] = None,
    current_user: Dict = Depends(get_current_user),
    _: None = Depends(strict_limiter())
):
    """
    Process voice input and return AI response
    """
    try:
        # throw exception if the file size is larger than 10 MB
        if audio.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File size is too large")

        # Read the audio file into memory
        audio_bytes = await audio.read()
        
        # Process the audio
        response = await chat_service.process_voice_input(
            audio_data=audio_bytes,
            user_id=str(current_user["id"]),
            model_name=model_name or current_user.get("modelName")
        )
        
        return {
            "success": True,
            "data": response
        }
    except Exception as e:
        logger.error(f"Error in chat_voice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text-to-speech")
async def text_to_speech(text: TextToSpeech):
    """
    Convert text to speech
    """
    try:
        audio_data = await chat_service.text_to_speech(text)
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/mp3",
            headers={"Content-Disposition": "attachment; filename=response.mp3"}
        )
    except Exception as e:
        logger.error(f"Error in text_to_speech: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 