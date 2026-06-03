from typing import Dict, Any
from jarvis.utils.logger import logger
from jarvis.services.gemini_service import GeminiService

class CommandParser:
    def __init__(self, gemini_service: GeminiService):
        self.gemini = gemini_service
        logger.info("Command Parser initialized.")

    def parse(self, text: str) -> Dict[str, Any]:
        """Parse natural language command into structured actions."""
        if not text or not text.strip():
            return {"intent": "chat", "action": "general_conversation", "params": {}}

        logger.info(f"Command Parser received: '{text}'")
        parsed = self.gemini.parse_intent(text)
        
        # Verify result contains minimal required fields
        if "intent" not in parsed or "action" not in parsed:
            logger.warning(f"Parsed response has invalid format: {parsed}. Defaulting to chat.")
            return {"intent": "chat", "action": "general_conversation", "params": {}}

        return parsed
