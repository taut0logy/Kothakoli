import google.generativeai as genai
from dotenv import load_dotenv
import os
import logging
import datetime
import numpy as np
from typing import Dict, List, Optional, Tuple
import json
import time
from pathlib import Path
from app.core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class EmbeddingService:
    def __init__(self):
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found")
            
            genai.configure(api_key=api_key)
            
            self.embedding_model = "models/text-embedding-004"
            self.generation_model = settings.DEFAULT_MODEL
            
            # Create storage directory if it doesn't exist
            self.data_dir = Path(settings.STORAGE_PATH) / "data"
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize cache files
            self.cache_file = self.data_dir / "conversation_cache.json"
            self.embedding_file = self.data_dir / "embedding_cache.json"
            
            # Create files if they don't exist
            if not self.cache_file.exists():
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
                
            if not self.embedding_file.exists():
                with open(self.embedding_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
            
            # Load existing data
            self.cache_storage = self._load_cache()
            self.embedding_storage = self._load_embeddings()
            
            logger.info(f"EmbeddingService initialized with storage path: {self.data_dir}")
            
        except Exception as e:
            logger.error(f"Error initializing EmbeddingService: {e}")
            raise

    def _load_cache(self) -> Dict[str, dict]:
        """Load cache from file or return empty dict"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            return {}

    def _load_embeddings(self) -> Dict[str, List[float]]:
        """Load embeddings from file or return empty dict"""
        try:
            if self.embedding_file.exists():
                with open(self.embedding_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading embeddings: {e}")
            return {}

    def _save_cache(self):
        """Save cache to file"""
        try:
            # Ensure directory exists
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_storage, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Cache saved to {self.cache_file}")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")

    def _save_embeddings(self):
        """Save embeddings to file"""
        try:
            # Ensure directory exists
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.embedding_file, 'w', encoding='utf-8') as f:
                json.dump(self.embedding_storage, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Embeddings saved to {self.embedding_file}")
        except Exception as e:
            logger.error(f"Error saving embeddings: {e}")

    async def create_embedding(self, text: str) -> Optional[List[float]]:
        """Create embedding for text"""
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="RETRIEVAL_DOCUMENT"
            )
            return result["embedding"]
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            return None

    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings"""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0

    async def find_similar_conversations(self, query_embedding: List[float], 
                                      threshold: float = 0.8) -> List[Tuple[str, float]]:
        """Find similar conversations based on embedding similarity"""
        try:
            similar_conversations = []
            for cache_id, embedding in self.embedding_storage.items():
                similarity = self.compute_similarity(query_embedding, embedding)
                if similarity > threshold:
                    similar_conversations.append((cache_id, similarity))
            
            return sorted(similar_conversations, key=lambda x: x[1], reverse=True)
        except Exception as e:
            logger.error(f"Error finding similar conversations: {e}")
            return []

    async def cache_conversation(self, conversation_text: str, embedding: List[float], display_name: str = None) -> Optional[str]:
        """Cache conversation with its embedding"""
        try:
            cache_id = f"cache_{int(time.time())}_{len(self.cache_storage)}"
            
            cache_data = {
                "text": conversation_text,
                "display_name": display_name or f"Conversation_{cache_id}",
                "create_time": datetime.datetime.now().isoformat(),
                "expire_time": (datetime.datetime.now() + datetime.timedelta(hours=24)).isoformat()
            }
            
            # Store in memory
            self.cache_storage[cache_id] = cache_data
            self.embedding_storage[cache_id] = embedding
            
            # Save to files immediately
            self._save_cache()
            self._save_embeddings()
            
            logger.info(f"Created and saved cache with ID: {cache_id}")
            return cache_id
            
        except Exception as e:
            logger.error(f"Error caching conversation: {e}")
            return None

    async def get_cached_conversation(self, cache_id: str) -> Optional[dict]:
        """Get cached conversation by ID"""
        try:
            if cache_id in self.cache_storage:
                logger.info(f"Found conversation in cache: {cache_id}")
                return self.cache_storage[cache_id]
            
            logger.warning(f"Conversation not found in cache: {cache_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cache: {e}")
            return None

    async def list_caches(self) -> List[dict]:
        """List all cached conversations"""
        try:
            return [
                {
                    "name": cache_id,
                    "display_name": data["display_name"],
                    "create_time": data["create_time"],
                    "expire_time": data["expire_time"],
                    "in_memory": True
                }
                for cache_id, data in self.cache_storage.items()
            ]
        except Exception as e:
            logger.error(f"Error listing caches: {e}")
            return []

    async def cleanup_expired_caches(self):
        """Clean up expired caches"""
        try:
            current_time = datetime.datetime.now()
            expired_ids = []
            
            for cache_id, cache_data in self.cache_storage.items():
                expire_time = datetime.datetime.fromisoformat(cache_data["expire_time"])
                if current_time > expire_time:
                    expired_ids.append(cache_id)
            
            for cache_id in expired_ids:
                del self.cache_storage[cache_id]
                del self.embedding_storage[cache_id]
            
            # Save changes to files
            if expired_ids:
                self._save_cache()
                self._save_embeddings()
                
            logger.info(f"Cleaned up {len(expired_ids)} expired caches")
            
        except Exception as e:
            logger.error(f"Error cleaning up caches: {e}")

embedding_service = EmbeddingService()