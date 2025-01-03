import os
import logging
from fastapi import APIRouter, HTTPException, Response, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from ..services.pdf_service import PDFService
from .auth import get_current_user
from typing import Dict


# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/pdf", tags=["pdf"])

# Initialize PDF service with API key from environment
pdf_service = PDFService()

class StoryPrompt(BaseModel):
    prompt: str
    model_name: Optional[str] = None

@router.post("/generate-story")
async def generate_story(
    prompt: StoryPrompt,
    current_user: Dict = Depends(get_current_user)
):
    """Generate a story PDF from a prompt."""
    try:
        # Await the PDF generation
        result = await pdf_service.generate_story_pdf(
            prompt=prompt.prompt,
            user_id=str(current_user["id"]),
            model_name=prompt.model_name
        )

        return {
            "success": True,
            "data": {
                "file_id": result["file_id"],
                "url": f"/api/pdf/download/{result['file_id']}"
            }
        }
    except Exception as e:
        logger.error(f"Failed to generate story PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{file_id}")
async def download_pdf(file_id: str):
    """Download a generated PDF file."""
    try:
        file_path = pdf_service.get_pdf_path(file_id)
        return FileResponse(
            file_path,
            media_type="application/pdf",
            filename=file_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error downloading PDF: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download PDF") 