import logging
from typing import Dict, Optional
import google.generativeai as genai
import json
from pathlib import Path
from ..core.config import settings
from .content_service import content_service

logger = logging.getLogger(__name__)

class ConvertService:
    def __init__(self):
        logger.info("Convert Service initialized")
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(settings.DEFAULT_MODEL)

    def _enhance_prompt_with_contributions(self):
        """Update the conversion prompt with recent user contributions."""
        examples = []
        
        # Create contributions directory if it doesn't exist
        contributions_dir = Path(settings.CONTRIBUTIONS_STORAGE_PATH)
        contributions_dir.mkdir(parents=True, exist_ok=True)
        
        # Load recent contributions (limit to last 10 for performance)
        contribution_files = sorted(contributions_dir.glob('*.json'), reverse=True)[:10]
        
        for file in contribution_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    contribution = json.load(f)
                    example = f"- \"{contribution['banglish']}\" should be \"{contribution['bengali']}\""
                    # Add feedback as context if available
                    if contribution.get('feedback'):
                        example += f"\n  Context: {contribution['feedback']}"
                    examples.append(example)
            except Exception as e:
                logger.error(f"Error loading contribution {file}: {str(e)}")
        
        return "\n".join(examples)

    async def convert_to_bengali(self, text: str, user_id: Optional[str] = None) -> Dict:
        """Convert Banglish text to Bengali and save to database if user_id provided."""
        try:
            prompt = f"""Convert the following Banglish text to proper Bengali (Bangla) text:
            Banglish: {text}
            
            Only provide the Bengali translation, nothing else. For example if the Banglish text is "tumi kemon acho" then the Bengali translation should be "তুমি কেমন আছো". If the Banglish text is "Ami valo achi" then the Bengali translation should be "আমি ভালো আছি".
            
            Recent user-contributed examples with context:
            {self._enhance_prompt_with_contributions()}
            
            Note: Pay attention to the context provided with examples to understand special cases,
            dialectal variations, and cultural nuances in the translations.
            
            Vowels mapping:     
            "o" means "ও", "a" means "আ", "e" means "এ", "i" means "ই", "u" means "উ, "oi" means "ঐ", "ou" means "ঔ""
            Consonant mappings:
            "b" means "ব", "d" means "দ", "g" means "গ", "r" means "র", "k" means "ক", "sh" means "শ", "bh" means "ভ", "ch" means "ছ", "dh" means "ধ", "kh" means "খ", "ph" means "ফ"
            ,"sh" means "শ"
            ,"th" means "থ"
            ,"ng" means "ঙ"
            ,"gh" means "ঘ"
            ,"jh" means "ঝ"
            ,"rr" means "ঋ"
            ,"ny" means "ঞ"."""

            response = self.model.generate_content(prompt)
            bengali_text = response.text.strip()

            # Save to database if user_id is provided
            if user_id:
                await content_service.save_content(
                    user_id=user_id,
                    content_type="BENGALI_TRANSLATION",
                    title=text[:50] + "...",
                    content=bengali_text,
                    prompt=text,
                    metadata={
                        "banglish": text,
                        "bengali": bengali_text
                    }
                )

            return {"bengali_text": bengali_text}

        except Exception as e:
            logger.error(f"Error converting Banglish to Bengali: {str(e)}")
            raise

    async def generate_title_caption(self, text: str, user_id: Optional[str] = None) -> Dict:
        """Generate a creative title and caption in Bengali and save to database if user_id provided."""
        try:
            prompt = f"""Generate a creative title and caption in Bengali for the following Bengali text. 
            The title should be short (2-4 words) and catchy, while the caption should be a brief summary (15-20 words).
            
            Text: {text}
            
            Provide the output in this format:
            Title: <bengali_title>
            Caption: <bengali_caption>
            """
            
            response = self.model.generate_content(prompt) 
            response.resolve()
            
            # Split the response into title and caption
            lines = response.text.strip().split('\n')
            title = lines[0].replace('Title:', '').strip()
            caption = lines[1].replace('Caption:', '').strip()

            # Save to database if user_id is provided
            if user_id:
                await content_service.save_content(
                    user_id=user_id,
                    content_type="BENGALI_STORY",
                    title=title,
                    content=caption,
                    prompt=text,
                    metadata={
                        "original_text": text,
                        "title": title,
                        "caption": caption
                    }
                )

            return {
                "title": title,
                "caption": caption
            }

        except Exception as e:
            logger.error(f"Error generating title and caption: {str(e)}")
            raise

convert_service = ConvertService() 