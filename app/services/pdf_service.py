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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont, TTFError
from reportlab.lib import colors
from reportlab.lib.fonts import addMapping
import unicodedata

logger = logging.getLogger(__name__)

class PDFService:
    def __init__(self):
        self.cache = cache_service
        logger.info("PDF Service initialized")
        
        # Check directory structure
        self.check_directory_structure()
        
        # Simplified font configuration
        self.available_fonts = {
            "Kalpurush": "kalpurush.ttf",
            "Mitra": "mitra.ttf",
            "Nikosh": "Nikosh.ttf",
            "Muktinarrow": "muktinarrow.ttf"
        }
        
        # Create fonts directory if it doesn't exist
        os.makedirs(settings.FONTS_PATH, exist_ok=True)
        
        # Register fonts with proper error handling
        for font_name, font_file in self.available_fonts.items():
            try:
                font_path = os.path.join(settings.FONTS_PATH, font_file)
                if not os.path.exists(font_path):
                    logger.error(f"Font file not found: {font_path}")
                    continue
                
                # Simply register the font
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                logger.info(f"Successfully registered font: {font_name}")
            except Exception as e:
                logger.error(f"Error registering font {font_name}: {str(e)}")

    def check_directory_structure(self):
        """Ensure all required directories exist."""
        required_dirs = [
            settings.FONTS_PATH,
            settings.PDF_STORAGE_PATH,
            settings.TEMP_STORAGE_PATH,
            settings.CONTRIBUTIONS_STORAGE_PATH
        ]
        
        for directory in required_dirs:
            try:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Directory ensured: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {str(e)}")

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

    async def generate_story_pdf(self, prompt: str, user_id: str, model_name: Optional[str] = None, is_public: bool = True) -> Dict:
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
                is_public=is_public,
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

    def _normalize_bengali_text(self, text: str) -> str:
        """Normalize Bengali text for proper rendering."""
        return unicodedata.normalize('NFC', text)

    async def generate_custom_pdf(
        self,
        content: str,
        title: str,
        user_id: str,
        font_name: str = "Kalpurush",
        caption: Optional[str] = None,
        is_public: bool = True
    ) -> Dict:
        """Generate a custom PDF with Bengali text."""
        try:
            # Validate font
            if font_name not in self.available_fonts:
                font_name = "Kalpurush"  # Default to Kalpurush if font not found
                logger.warning(f"Invalid font requested, falling back to {font_name}")

            # Create PDF content
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            # Define styles
            styles = getSampleStyleSheet()
            
            # Custom style for Bengali text - using direct font name
            bengali_title = ParagraphStyle(
                'BengaliTitle',
                parent=styles['Title'],
                fontName=font_name,  # Direct font name
                fontSize=24,
                spaceAfter=30,
                alignment=1
            )
            
            bengali_caption = ParagraphStyle(
                'BengaliCaption',
                parent=styles['Italic'],
                fontName=font_name,  # Direct font name
                fontSize=12,
                textColor=colors.gray,
                spaceAfter=20
            )
            
            bengali_content = ParagraphStyle(
                'BengaliContent',
                parent=styles['Normal'],
                fontName=font_name,  # Direct font name
                fontSize=12,
                leading=16,
                spaceAfter=12
            )

            # Build story
            story = []
            
            # Add title
            story.append(Paragraph(self._normalize_bengali_text(title), bengali_title))
            
            # Add caption if provided
            if caption:
                story.append(Paragraph(self._normalize_bengali_text(caption), bengali_caption))
            
            # Add content (split into paragraphs)
            paragraphs = content.split('\n\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    story.append(Paragraph(
                        self._normalize_bengali_text(paragraph), 
                        bengali_content
                    ))

            # Build PDF
            doc.build(story)
            pdf_content = buffer.getvalue()
            buffer.close()

            # Generate unique file ID and save
            file_id = f"{uuid.uuid4()}.pdf"
            pdf_path = os.path.join(settings.PDF_STORAGE_PATH, file_id)
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            
            with open(pdf_path, 'wb') as f:
                f.write(pdf_content)

            # Save to database
            file_url = f"/api/pdf/{file_id}"
            await content_service.save_content(
                user_id=user_id,
                content_type="PDF",
                title=title,
                content=content,
                filename=file_id,
                file_url=file_url,
                is_public=is_public,
                metadata={
                    "caption": caption,
                    "font": font_name,
                    "file_path": pdf_path
                }
            )

            return {
                "success": True,
                "data": {
                    "file_id": file_id,
                    "path": pdf_path,
                    "url": file_url,
                    "title": title
                }
            }

        except Exception as e:
            logger.error(f"Error generating custom PDF: {str(e)}")
            raise

    def verify_fonts(self):
        """Verify that font files exist and are accessible."""
        missing_fonts = []
        for font_name, font_file in self.available_fonts.items():
            font_path = os.path.join(settings.FONTS_PATH, font_file)
            if not os.path.exists(font_path):
                missing_fonts.append(font_file)
                logger.error(f"Missing font file: {font_path}")
        
        if missing_fonts:
            logger.error(f"Missing font files: {', '.join(missing_fonts)}")
            logger.error(f"Please ensure font files are placed in: {settings.FONTS_PATH}")

    def test_font_registration(self):
        """Test if fonts are properly registered."""
        for font_name in self.available_fonts:
            try:
                font = pdfmetrics.getFont(font_name)
                logger.info(f"Font {font_name} is properly registered")
                # Test some Bengali characters
                test_text = "অআইঈউঊঋএঐওঔ"
                for char in test_text:
                    if ord(char) not in font.face.charToGlyph:
                        logger.warning(f"Character {char} not found in font {font_name}")
            except Exception as e:
                logger.error(f"Error testing font {font_name}: {str(e)}")

pdf_service = PDFService() 