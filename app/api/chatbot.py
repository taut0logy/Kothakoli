from fastapi import APIRouter, Form, HTTPException, Depends, Body, Query
from typing import Optional
from ..services.chatbot_service import chatbot_service
from ..services.content_service import content_service
from ..api.auth import get_current_user
from typing import Dict
from app.core.database import db
from app.api.chat import ChatMessage
from pydantic import BaseModel
from ..services.banglish_spell_checker import check_banglish_text
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


@router.post("/chat")
async def chat(
    message: ChatMessage,
    current_user: Dict = Depends(get_current_user),
):
    try:
        user_id = current_user['id']
        response = await chatbot_service.get_response(
            message=message.message,
            user_id=user_id,
            model_name=message.model_name or current_user.get("modelName")
        )
        

        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
            
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/history")
async def get_chat_history(current_user: Dict = Depends(get_current_user)):
    try:
        # Get user's chat history
        history = await content_service.get_content_by_type("CHATBOT", limit=5000, offset=0, isPublic=True)
        
        return {
            "status": "success",
            "history": [
                {
                    "id": str(chat.id),
                    "prompt": chat.prompt,
                    "response": chat.generated_content,
                    "created_at": chat.created_at,
                    "metadata": chat.metadata
                }
                for chat in history
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SpellCheckRequest(BaseModel):
    message: str

@router.post("/check-spelling")
@router.get("/check-spelling")
async def check_spelling(
    message: str = Query(..., description="Text to check spelling"),
    current_user: Dict = Depends(get_current_user)
):
    try:
        if not message or not message.strip():
            return {
                "status": "success",
                "suggestions": [],
                "original": message
            }

        # Get suggestions using check_banglish_text
        suggestions = check_banglish_text(message)
        
        return {
            "status": "success",
            "suggestions": suggestions[:5],  # Limit to top 5 suggestions
            "original": message
        }

    except Exception as e:
        logger.error(f"Error in spell checking: {e}")
        return {
            "status": "error",
            "suggestions": [],
            "error": str(e)
        }

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/cached-conversations")
async def get_cached_conversations(
    current_user: Dict = Depends(get_current_user)
):
    """Get all cached conversations"""
    try:
        from app.services.embedding_service import embedding_service
        
        # Get all cached conversations
        conversations = await embedding_service.list_caches()
        
        # Format the conversations for frontend
        formatted_conversations = []
        for conv in conversations:
            cache_data = await embedding_service.get_cached_conversation(conv["name"])
            if cache_data and "text" in cache_data:
                # Split the conversation text into user and bot messages
                messages = []
                for part in cache_data["text"].split("\n"):
                    if part.startswith("User: "):
                        messages.append({
                            "role": "user",
                            "content": part.replace("User: ", "")
                        })
                    elif part.startswith("Bot: "):
                        messages.append({
                            "role": "bot",
                            "content": part.replace("Bot: ", "")
                        })
                
                formatted_conversations.append({
                    "id": conv["name"],
                    "messages": messages,
                    "created_at": conv["create_time"],
                    "display_name": conv["display_name"]
                })
        
        return {
            "status": "success",
            "conversations": formatted_conversations
        }
        
    except Exception as e:
        logger.error(f"Error getting cached conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class CacheConversationRequest(BaseModel):
    conversation_id: str

@router.post("/cache-conversation")
async def cache_conversation(
    request: CacheConversationRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Cache a specific conversation for training"""
    try:
        from app.services.embedding_service import embedding_service
        
        # Get the conversation
        conversation = await embedding_service.get_cached_conversation(request.conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
            
        # Create embedding for the conversation
        embedding = await embedding_service.create_embedding(conversation["text"])
        
        # Cache the conversation with its embedding
        cache_id = await embedding_service.cache_conversation(
            conversation_text=conversation["text"],
            embedding=embedding,
            display_name=f"Training_{request.conversation_id}"
        )
        
        return {
            "status": "success",
            "cache_id": cache_id,
            "message": "Conversation cached for training"
        }
        
    except Exception as e:
        logger.error(f"Error caching conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
