import os
import logging
from fastapi import APIRouter, HTTPException, Response, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from ..services.pdf_service import PDFService
from .auth import get_current_user
from typing import Dict
from fastapi import status


# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/pdf", tags=["pdf"])

# Initialize PDF service with API key from environment
pdf_service = PDFService()

class StoryPrompt(BaseModel):
    prompt: str
    model_name: Optional[str] = None

class PDFResponse(BaseModel):
    success: bool
    data: Dict[str, str]

class CustomPDFRequest(BaseModel):
    content: str
    title: str
    caption: Optional[str] = None
    font_name: str = "Kalpurush"
    is_public: bool = True 

@router.post("/generate-story")
async def generate_story(
    prompt: StoryPrompt,
    is_public: bool = True,
    current_user: Dict = Depends(get_current_user)
):
    """Generate a story PDF from a prompt."""
    try:
        # Await the PDF generation
        result = await pdf_service.generate_story_pdf(
            prompt=prompt.prompt,
            user_id=str(current_user["id"]),
            model_name=prompt.model_name,
            is_public=is_public
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

@router.post("/generate-custom", response_model=PDFResponse)
async def generate_custom_pdf(
    request: CustomPDFRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Generate a custom PDF with Bengali text."""
    try:
        result = await pdf_service.generate_custom_pdf(
            content=request.content,
            title=request.title,
            caption=request.caption,
            user_id=current_user["id"],
            font_name=request.font_name,
            is_public=request.is_public
        )
        return PDFResponse(
            success=True,
            data={
                "file_id": result["data"]["file_id"],
                "path": result["data"]["path"],
                "url": result["data"]["url"],
                "title": result["data"]["title"]
            }
        )
    except Exception as e:
        logger.error(f"Error generating custom PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
