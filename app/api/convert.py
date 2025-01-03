from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from ..services.convert_service import convert_service
from ..api.auth import get_current_user
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/convert", tags=["convert"])

# Define request/response models
class BanglishRequest(BaseModel):
    text: str

class BengaliResponse(BaseModel):
    bengali_text: str

class TitleCaptionResponse(BaseModel):
    title: str
    caption: str

@router.post("/", response_model=BengaliResponse)
async def convert_to_bengali(
    request: BanglishRequest,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Convert Banglish text to Bengali."""
    try:
        user_id = current_user["id"] if current_user else None
        result = await convert_service.convert_to_bengali(request.text, user_id)
        return BengaliResponse(**result)
    except Exception as e:
        logger.error(f"Error converting Banglish to Bengali: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-title-caption", response_model=TitleCaptionResponse)
async def generate_title_caption(
    request: BanglishRequest,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Generate a creative title and caption in Bengali."""
    try:
        user_id = current_user["id"] if current_user else None
        result = await convert_service.generate_title_caption(request.text, user_id)
        return TitleCaptionResponse(**result)
    except Exception as e:
        logger.error(f"Error generating title and caption: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

