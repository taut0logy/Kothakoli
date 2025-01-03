import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Optional, Dict
from ..services.file_service import file_service
from ..core.config import settings
from ..api.auth import get_current_user

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/files", tags=["files"])

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    model_name: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """Upload and process a file (image or text)"""
    logger.info(f"Received file upload request: {file.filename}")
    if file.size > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds the 20MB limit")
    
    try:
        logger.info(f"Received file upload request: {file.filename}")
        
        # Read file content
        file_content = await file.read()
        
        # Process the file
        result = await file_service.process_file_with_gemini(
            file=file.file,
            filename=file.filename,
            user_id=str(current_user["id"]),
            model_name=model_name or settings.DEFAULT_MODEL
        )
            
        logger.info("File processed successfully")
        return {
            "success": True,
            "data": result
        }
        
    except ValueError as e:
        logger.error(f"File processing error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in file upload: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the file"
        )

@router.post("/process-file")
async def process_image(
    file: UploadFile = File(...),
    model_name: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """Process an image file specifically"""
    try:
        logger.info(f"Received image processing request: {file.filename}")
    
        
        # Validate file size (5MB limit for images)
        file_size_limit = 5 * 1024 * 1024  # 5MB
        file_content = await file.read(file_size_limit + 1)
        
        if len(file_content) > file_size_limit:
            logger.error("Image size exceeds limit")
            raise HTTPException(
                status_code=400,
                detail="Image size exceeds the 5MB limit"
            )
        
        # Process the image
        result = await file_service.process_file(
            file=file.file,
            filename=file.filename,
            user_id=str(current_user["id"]),
            model_name=model_name or current_user.get("modelName")
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
            
        logger.info("File processed successfully")
        return result
        
    except ValueError as e:
        logger.error(f"Image processing error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in image processing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the image"
        )