import logging
from typing import Dict, Optional
import google.generativeai as genai
from app.core.config import settings
from app.services.cache_service import cache_service
from app.services.content_service import content_service
import speech_recognition as sr
from gtts import gTTS
import io
import json
import os
from pydub import AudioSegment

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.cache = cache_service
        self.recognizer = sr.Recognizer()
    def _get_model_config(self, model_name: str) -> Dict:
        """Get the configuration for the specified model."""
        return settings.MODEL_CONFIGS.get(model_name, settings.MODEL_CONFIGS[settings.DEFAULT_MODEL])

    async def process_text_input(self, text: str, user_id: str, model_name: Optional[str] = None) -> Dict:
        """Process text input using the specified model."""
        try:
            # Use default model if none specified
            model_name = model_name or settings.DEFAULT_MODEL
            if model_name not in settings.AVAILABLE_MODELS:
                model_name = settings.DEFAULT_MODEL

            # Configure model
            model = genai.GenerativeModel(
                model_name=model_name,
            )

            # Generate response
            response = model.generate_content(text)
            
            # Cache the response
            cache_key = f"chat:{user_id}:{text}"
            await self.cache.set(cache_key, response.text)

            # Save to database
            await content_service.save_content(
                user_id=user_id,
                content_type="CHAT",
                title=text[:50] + "...",  # Use first 50 chars of query as title
                content=response.text,
                metadata={
                    "query": text,
                    "model": model_name
                }
            )

            return {
                "text": response.text,
                "model": model_name,
            }

        except Exception as e:
            logger.error(f"Error processing text input: {str(e)}")
            raise

    async def process_voice_input(self, audio_data: bytes, user_id: str, model_name: Optional[str] = None) -> Dict:
        """Process voice input using the specified model."""
        try:
            # Use default model if none specified
            model_name = model_name or settings.VOICE_MODEL
            if model_name not in settings.AVAILABLE_VOICE_MODELS:
                model_name = settings.VOICE_MODEL

            # Convert WebM to WAV
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="webm")
            wav_io = io.BytesIO()
            audio_segment.export(wav_io, format="wav")
            wav_io.seek(0)
            
            # Create AudioFile from WAV bytes
            # with sr.AudioFile(wav_io) as source:
            #     audio = self.recognizer.record(source)

            # temporarily store the wav file
            wav_file_path = os.path.join(settings.TEMP_STORAGE_PATH, f"audio{user_id}.wav")
            os.makedirs(os.path.dirname(wav_file_path), exist_ok=True)
            
            with open(wav_file_path, "wb") as f:
                f.write(wav_io.getvalue())
                
            try:
                # Perform speech recognition
                # transcribed_text = self.recognizer.recognize_google(audio)
                # logger.info(f"Transcribed text: {transcribed_text}")
                
                # Now process the text with Gemini

                model = genai.GenerativeModel(model_name=model_name)

                # add the file to the model
                file = genai.upload_file(path=wav_file_path)

                prompt = f"""You are a helpful assistant. You are given a voice message. Please transcribe it and respond to the user.
                Format the response as a JSON object with the following structure:
                {{
                    "transcription": "Transcribed text",
                    "response": "Response to the user"
                }}
                """
                gemini_response = model.generate_content([file, prompt])
                logger.info(f"Gemini response: {gemini_response.text}")

                # delete the file
                os.remove(wav_file_path)
                file.delete()

                # Parse the JSON from the response text
                try:
                # Find the JSON object in the response
                    text = gemini_response.text
                    start_idx = text.find('{')
                    end_idx = text.rfind('}') + 1
                    if start_idx != -1 and end_idx != 0:
                        json_str = text[start_idx:end_idx]
                        response_data = json.loads(json_str)
                    else:
                        # Fallback if no JSON is found
                        response_data = {
                            "transcription": "Unavle to transcribe",
                            "response": "I couldn't understand the audio. Please try speaking more clearly."
                        }
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    response_data = {
                        "transcription": "Unavle to transcribe",
                        "response": "I couldn't understand the audio. Please try speaking more clearly."
                    }
                
                # Cache the response
                cache_key = f"voice:{user_id}:{hash(str(audio_data))}"
                await self.cache.set(cache_key, response_data)

                # Save to database
                await content_service.save_content(
                    user_id=user_id,
                    content_type="VOICE",
                    title=response_data["transcription"][:50] + "...",
                    content=response_data["response"],
                    metadata={
                        "transcription": response_data["transcription"],
                        "model": model_name
                    }
                )

                return {
                    "text": response_data["response"],
                    "model": model_name,
                    "transcription": response_data["transcription"]
                }
                
            except sr.UnknownValueError:
                return {
                    "text": "I couldn't understand the audio. Please try speaking more clearly.",
                    "model": model_name,
                    "transcription": None
                }
            except sr.RequestError as e:
                logger.error(f"Speech recognition request error: {str(e)}")
                raise Exception("Speech recognition service is unavailable")

        except Exception as e:
            logger.error(f"Error processing voice input: {str(e)}")
            raise
        
    async def text_to_speech(self, text: str) -> bytes:
        """Convert text response to speech using gTTS"""
        try:
            # Ensure text is a string and clean it up
            if not isinstance(text, str):
                text = str(text)
            
            # Clean and normalize the text
            text = text.strip()
            if not text:
                raise ValueError("Empty text provided for conversion")

            # Remove any debug text that might be at the start
            if text.startswith("text="):
                text = text.replace("text=", "", 1).strip()

            # Create an in-memory bytes buffer
            audio_buffer = io.BytesIO()
            
            try:
                # Convert text to speech
                tts = gTTS(text=text, lang='en', slow=False)
                logger.info("Text converted to speech")
                
                # Save to buffer
                tts.write_to_fp(audio_buffer)
                logger.info("Speech saved to buffer")
                
                # Get the audio data
                audio_buffer.seek(0)
                audio_data = audio_buffer.getvalue()
                
                logger.info("Text to speech conversion completed")
                return audio_data

            finally:
                # Ensure buffer is closed even if an error occurs
                audio_buffer.close()

        except ValueError as ve:
            logger.error(f"Invalid input for text-to-speech: {str(ve)}")
            raise Exception(f"Text-to-speech conversion failed: {str(ve)}")
        except Exception as e:
            logger.error(f"Text-to-speech conversion failed: {str(e)}")
            raise Exception(f"Text-to-speech conversion failed: {str(e)}")

chat_service = ChatService()