import keyboard
import pyautogui
from jarvis.utils.logger import logger

class VoiceTyping:
    @staticmethod
    def type_text(text: str) -> bool:
        """Type the given text at the current active cursor location."""
        if not text:
            return False
            
        try:
            logger.info(f"Voice Typing: simulating typing for text: '{text}'")
            # keyboard.write is fast and reliable for text input simulation
            keyboard.write(text + " ")
            return True
        except Exception as e:
            logger.error(f"Failed typing with 'keyboard' library: {e}. Trying PyAutoGUI fallback.")
            try:
                # pyautogui.write behaves like keypresses
                pyautogui.write(text + " ")
                return True
            except Exception as ex:
                logger.error(f"PyAutoGUI fallback typing also failed: {ex}")
                return False
