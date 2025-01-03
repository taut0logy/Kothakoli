import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class BanglishService:
    def __init__(self):
        try:
            # Load banglish spelling correction mapping
            self.mapping_file = Path("data/banglish_mapping.json")
            self.mapping = self._load_mapping()
            logger.info("BanglishService initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing BanglishService: {e}")
            raise

    def _load_mapping(self) -> Dict[str, str]:
        """Load or create banglish spelling correction mapping"""
        default_mapping = {
            # Common Banglish spelling corrections
            "ame": "ami",
            "amee": "ami",
            "tume": "tumi",
            "tumee": "tumi",
            "apne": "apni",
            "kemun": "kemon",
            "kmn": "kemon",
            "acho": "acho",
            "achen": "achen",
            "valo": "bhalo",
            "balo": "bhalo",
            "kothai": "kothay",
            "koi": "kothay",
            "ke": "ki",
            "kee": "ki",
            "korcho": "korcho",
            "krcho": "korcho",
            "korchen": "korchen",
            "krchen": "korchen",
            "bolo": "bolo",
            "bol": "bolo",
            "bolun": "bolun",
            "blun": "bolun",
            "dhk": "dhaka",
            "dkh": "dhaka",
            "bangla": "bangla",
            "bangali": "bangla",
            "english": "english",
            "ing": "english",
            "sekhi": "shikhi",
            "sikhi": "shikhi",
            "sekhbo": "shikhbo",
            "sikhbo": "shikhbo",
            "jni": "jani",
            "janina": "janina",
            "janena": "janina",
            "bujhi": "bujhi",
            "buji": "bujhi",
            "bujina": "bujhina",
            "bujhena": "bujhina",
            "khub": "khub",
            "kub": "khub",
            "onek": "onek",
            "onk": "onek",
            "sundor": "sundor",
            "sundr": "sundor",
            "shundr": "sundor",
            # Add more mappings as needed
        }

        try:
            if self.mapping_file.exists():
                with open(self.mapping_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Create data directory if it doesn't exist
                self.mapping_file.parent.mkdir(exist_ok=True)
                # Save default mapping
                with open(self.mapping_file, 'w', encoding='utf-8') as f:
                    json.dump(default_mapping, f, ensure_ascii=False, indent=2)
                return default_mapping
        except Exception as e:
            logger.error(f"Error loading mapping: {e}")
            return default_mapping

    async def get_correction(self, text: str) -> Optional[str]:
        """Get spelling correction for Banglish text"""
        try:
            words = text.lower().split()
            corrected_words = []
            
            for word in words:
                if word in self.mapping:
                    corrected_words.append(self.mapping[word])
                else:
                    corrected_words.append(word)
            
            corrected_text = ' '.join(corrected_words)
            return corrected_text if corrected_text != text else None
            
        except Exception as e:
            logger.error(f"Error getting correction: {e}")
            return None

    async def get_suggestions(self, text: str) -> List[str]:
        """Get possible spelling suggestions for Banglish text"""
        try:
            suggestions = []
            words = text.lower().split()
            
            # Get exact matches
            exact_match = await self.get_correction(text)
            if exact_match:
                suggestions.append(exact_match)
            
            # Get partial matches
            for word in words:
                for misspelled, correct in self.mapping.items():
                    # Check if the word might be a misspelling
                    if (word in misspelled or misspelled in word or 
                        self._similarity_score(word, misspelled) > 0.7):
                        new_words = words.copy()
                        new_words[words.index(word)] = correct
                        suggestion = ' '.join(new_words)
                        if suggestion not in suggestions:
                            suggestions.append(suggestion)
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error getting suggestions: {e}")
            return []

    def _similarity_score(self, word1: str, word2: str) -> float:
        """Calculate similarity between two words using character overlap"""
        if not word1 or not word2:
            return 0.0
        
        set1 = set(word1)
        set2 = set(word2)
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        return len(intersection) / len(union)

    def add_mapping(self, misspelled: str, correct: str) -> bool:
        """Add new Banglish spelling correction mapping"""
        try:
            self.mapping[misspelled.lower()] = correct.lower()
            with open(self.mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.mapping, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error adding mapping: {e}")
            return False

banglish_service = BanglishService()