import google.generativeai as genai
from dotenv import load_dotenv
import os
import logging
import uuid
from ..services.embedding_service import embedding_service
from ..services.banglish_service import banglish_service
from ..services.content_service import content_service
from typing import Optional, List, Tuple, Dict
from app.core.config import settings
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ChatBotService:
    def __init__(self):
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found")
            
            genai.configure(api_key=api_key)
            
            # Configure model with simple settings
            generation_config = {
                "temperature": 0.7,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048,
            }
            
            self.model = genai.GenerativeModel(
                model_name='gemini-2.0-flash-exp',
                generation_config=generation_config
            )
            
            self.chat = self.model.start_chat(history=[])
            logger.info("ChatService initialized successfully")
            
            self.embedding_service = embedding_service
            self.banglish_service = banglish_service
            
        except Exception as e:
            logger.error(f"Error initializing ChatService: {e}")
            raise

    async def get_response(self, message: str, user_id: str, model_name: Optional[str] = None) -> dict:
        try:
            # Check for Banglish and get correction suggestions
            banglish_correction = None
            if any(ord(c) < 128 for c in message):
                banglish_correction = await self.banglish_service.get_correction(message)
            
            # Get response from model
            response = await self._get_gemini_response(message)
            
            # Create embedding for the conversation
            conversation_text = f"User: {message}\nBot: {response}"
            conv_embedding = await self.embedding_service.create_embedding(conversation_text)
            
            # Cache the conversation if embedding was created
            cache_id = None
            if conv_embedding:
                cache_id = await self.embedding_service.cache_conversation(
                    conversation_text=conversation_text,
                    embedding=conv_embedding,
                    display_name=f"Chat_{int(time.time())}"
                )
                logger.info(f"Conversation cached with ID: {cache_id}")
            
            # Save as generated content
            if user_id:
                await content_service.save_content(
                    user_id=user_id,
                    content_type="CHATBOT",
                    title=message[:50] + "...",
                    content=response,
                    prompt=message,
                    metadata={
                        "banglish_correction": banglish_correction,
                        "conversation_text": conversation_text,
                        "embedding": conv_embedding,
                        "model_name": model_name or "gemini-2.0-flash-exp",
                        "cache_id": cache_id
                    }
                )
            
            return {
                "response": response,
                "banglish_correction": banglish_correction,
                "has_embedding": conv_embedding is not None,
                "cache_id": cache_id
            }
            
        except Exception as e:
            logger.error(f"Error in get_response: {e}")
            return {
                "response": "দুঃখিত, একটি ত্রুটি ঘটেছে। আবার চেষ্টা করুন।",
                "error": str(e)
            }

    async def _get_gemini_response(self, message: str) -> str:
        try:
            # Prepare prompt
            prompt = f"""
You are a highly helpful AI assistant who exclusively communicates in the Bangla language. 
- **Understanding Inputs:**
  - If the user writes in Banglish (Bengali using the Latin alphabet), interpret it accurately and respond in proper Bangla.
  - If the user writes in Bangla, respond directly in Bangla.
  - If the user writes in English, understand the intent and respond in Bangla.
- **Response Formatting:**
  - Maintain and utilize Markdown syntax to structure your responses effectively. This includes using headings, bullet points, numbered lists, bold and italic text, code blocks, and other relevant Markdown features.
  - Ensure that the Markdown formatting enhances readability and aesthetics, making the response both informative and visually appealing.
- **Style and Tone:**
  - Keep the language clear, polite, and engaging.
  - Strive for elegance and clarity in your Bangla responses to provide a pleasant user experience.

**User message:** {message}
"""

            
            # Get response
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                logger.error("Empty response received")
                return "দুঃখিত, কোনো উত্তর পাওয়া যায়নি। আবার চেষ্টা করুন।"
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error getting response: {e}")
            return "দুঃখিত, একটি ত্রুটি ঘটেছে। আবার চেষ্টা করুন।"
        
chatbot_service = ChatBotService()