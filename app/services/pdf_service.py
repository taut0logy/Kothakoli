import json
import logging
from typing import Dict, Optional
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from io import BytesIO
from app.core.config import settings
from app.services.cache_service import cache_service
from app.services.content_service import content_service
import uuid
import os

logger = logging.getLogger(__name__)

class PDFService:
    def __init__(self):
        self.cache = cache_service
        logger.info("PDF Service initialized")

    def _create_pdf(self, story_data: Dict) -> bytes:
        """Create a PDF document from story data."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30
        )
        story.append(Paragraph(story_data["title"], title_style))
        story.append(Spacer(1, 12))

        # Add content
        content_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=12,
            leading=14,
            spaceAfter=10
        )
        
        # Split content into paragraphs
        paragraphs = story_data["content"].split('\n\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                story.append(Paragraph(paragraph, content_style))
                story.append(Spacer(1, 12))

        doc.build(story)
        return buffer.getvalue()

    async def generate_story_pdf(self, prompt: str, user_id: str, model_name: Optional[str] = None) -> Dict:
        """Generate a PDF story from a prompt."""
        try:
            # Generate story content using Gemini
            model = genai.GenerativeModel(
                model_name=model_name or settings.DEFAULT_MODEL
            )
            
            structured_prompt = f"""
            Create a modern and engaging story based on this prompt: {prompt}
            Format the response as a JSON object with the following structure:
            {{
                "title": "Story Title",
                "content": "Story content with multiple paragraphs"
            }}
            The story should be at least 2 pages and at most 10 pages long.
            """
            
            response = model.generate_content(structured_prompt)
            
            # Parse the JSON from the response text
            try:
                # Find the JSON object in the response
                text = response.text
                start_idx = text.find('{')
                end_idx = text.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = text[start_idx:end_idx]
                    story_data = json.loads(json_str)
                else:
                    # Fallback if no JSON is found
                    story_data = {
                        "title": "Generated Story",
                        "content": text
                    }
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                story_data = {
                    "title": "Generated Story",
                    "content": response.text
                }

            # Generate PDF
            pdf_content = self._create_pdf(story_data)
            
            # Generate unique file ID
            file_id = f"{uuid.uuid4()}.pdf"
            
            # Save PDF to file system
            pdf_path = os.path.join(settings.PDF_STORAGE_PATH, file_id)
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            
            with open(pdf_path, 'wb') as f:
                f.write(pdf_content)

            # Save to database
            file_url = f"/api/pdf/{file_id}"  # URL where the PDF can be accessed
            await content_service.save_content(
                user_id=user_id,
                content_type="PDF",
                title=story_data["title"],
                content=story_data["content"],
                filename=file_id,
                file_url=file_url,
                metadata={
                    "prompt": prompt,
                    "model": model_name,
                    "file_path": pdf_path
                }
            )

            return {
                "file_id": file_id,
                "path": pdf_path,
                "url": file_url,
                "title": story_data["title"]
            }

        except Exception as e:
            logger.error(f"Error generating story PDF: {str(e)}")
            raise
        
    def get_pdf_path(self, file_id: str) -> str:
        """Get the path to a generated PDF file."""
        return os.path.join(settings.PDF_STORAGE_PATH, file_id)

pdf_service = PDFService() 