import json
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from jarvis.utils.logger import logger
from jarvis.config.settings import GEMINI_API_KEY

class GeminiService:
    def __init__(self):
        self.api_available = False
        if not GEMINI_API_KEY or "YOUR_GEMINI_API_KEY" in GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY is not configured or is default. Running Gemini in simulation/fallback mode.")
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            # Use gemini-2.5-flash as the default model
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.api_available = True
            logger.info("Gemini API initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize google-generativeai client: {e}")

    def chat_response(self, prompt: str, chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """Get conversational response from Gemini. Fallback to basic assistant behavior if offline."""
        if not self.api_available:
            return self._fallback_chat(prompt)

        try:
            import google.generativeai as genai
            
            # Format history for Gemini SDK if provided
            # Gemini SDK uses [{'role': 'user'|'model', 'parts': [str]}]
            contents = []
            if chat_history:
                for msg in chat_history:
                    role = 'user' if msg['role'] == 'user' else 'model'
                    contents.append({
                        'role': role,
                        'parts': [msg['content']]
                    })
            contents.append({'role': 'user', 'parts': [prompt]})

            # Call API
            response = self.model.generate_content(
                contents,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=150,
                )
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API chat request failed: {e}")
            return self._fallback_chat(prompt)

    def parse_intent(self, text: str) -> Dict[str, Any]:
        """Use Gemini to translate a natural language command into structured JSON execution blocks."""
        current_time_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        
        system_instruction = (
            f"You are the intent parser for JARVIS, a Windows desktop assistant.\n"
            f"Your job is to parse the user's spoken command into a structured JSON object.\n"
            f"Current local time: {current_time_str}\n\n"
            "Supported intents, actions, and expected parameters:\n"
            "1. intent: 'open_app'\n"
            "   - action: 'open_notepad' | 'open_calculator' | 'open_command_prompt' | 'open_file_explorer' | 'open_control_panel' | 'open_settings' | 'open_camera' | 'open_chrome' | 'open_vscode'\n"
            "2. intent: 'pc_control'\n"
            "   - action: 'volume_up' | 'volume_down' | 'mute' | 'unmute' | 'brightness_increase' | 'brightness_decrease' | 'screenshot' | 'wifi_on' | 'wifi_off' | 'bluetooth_on' | 'bluetooth_off' | 'lock_pc' | 'shutdown' | 'restart' | 'sleep'\n"
            "3. intent: 'file_operation'\n"
            "   - action: 'open_folder' (params: 'path')\n"
            "   - action: 'create_file' (params: 'path', 'content')\n"
            "   - action: 'delete_file' (params: 'path')\n"
            "   - action: 'open_downloads' (params: None)\n"
            "   - action: 'search_files' (params: 'keyword')\n"
            "   - action: 'rename_file_or_folder' (params: 'old_path', 'new_path')\n"
            "   - action: 'move_file' (params: 'path', 'destination')\n"
            "   - action: 'copy_file' (params: 'path')\n"
            "   - action: 'paste_file' (params: 'destination')\n"
            "   - action: 'open_recent' (params: None)\n"
            "   - action: 'open_specific_file' (params: 'path')\n"
            "   - action: 'create_folder' (params: 'path')\n"
            "   - action: 'delete_folder' (params: 'path')\n"
            "   - action: 'organize_files' (params: 'path')\n"
            "4. intent: 'alarm_reminder'\n"
            "   - action: 'set_reminder' (params: 'text', 'trigger_time' formatted in ISO-8601 YYYY-MM-DDTHH:MM:SS based on current time context)\n"
            "   - action: 'delete_reminder' (params: 'keyword')\n"
            "   - action: 'list_reminders' (params: None)\n"
            "   - action: 'set_alarm' (params: 'time_hhmm' in 24-hour 'HH:MM', 'label')\n"
            "   - action: 'stop_alarm' (params: None)\n"
            "   - action: 'delete_alarm' (params: 'time_hhmm' in 'HH:MM')\n"
            "5. intent: 'email'\n"
            "   - action: 'send_email' (params: 'to_email', 'subject', 'body')\n"
            "   - action: 'read_emails' (params: None)\n"
            "6. intent: 'weather'\n"
            "   - action: 'get_weather' (params: 'city')\n"
            "7. intent: 'news'\n"
            "   - action: 'get_news' (params: 'country')\n"
            "8. intent: 'voice_typing'\n"
            "   - action: 'start_typing' (params: None)\n"
            "9. intent: 'chat'\n"
            "   - action: 'general_conversation' (params: None)\n\n"
            "Examples:\n"
            "- 'Open Notepad' -> {\"intent\": \"open_app\", \"action\": \"open_notepad\", \"params\": {}}\n"
            "- 'Remind me to call Rahul at 6 PM' -> Compute 6 PM from current time. E.g. if today is 2026-06-03, 6 PM is '2026-06-03T18:00:00'. -> {\"intent\": \"alarm_reminder\", \"action\": \"set_reminder\", \"params\": {\"text\": \"call Rahul\", \"trigger_time\": \"2026-06-03T18:00:00\"}}\n"
            "- 'Rename old.txt to new.txt' -> {\"intent\": \"file_operation\", \"action\": \"rename_file_or_folder\", \"params\": {\"old_path\": \"old.txt\", \"new_path\": \"new.txt\"}}\n"
            "- 'Send email to john@example.com' -> {\"intent\": \"email\", \"action\": \"send_email\", \"params\": {\"to_email\": \"john@example.com\", \"subject\": \"\", \"body\": \"\"}}\n\n"
            "Output ONLY valid raw JSON without any markdown code block formatting (no ```json and no ```). If no command fits, return intent: 'chat' and action: 'general_conversation'."
        )

        if not self.api_available:
            return self._fallback_intent_parser(text)

        try:
            import google.generativeai as genai
            
            response = self.model.generate_content(
                [system_instruction, f"Parse command: '{text}'"],
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  # Low temp for deterministic structured output
                    max_output_tokens=200,
                )
            )
            raw_response = response.text.strip()
            # Remove any markdown wrapping if the LLM outputted it anyway
            if raw_response.startswith("```"):
                lines = raw_response.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_response = "\n".join(lines).strip()
            
            parsed = json.loads(raw_response)
            logger.info(f"Gemini Intent Parsing Succeeded: {parsed}")
            return parsed
        except Exception as e:
            logger.error(f"Gemini intent parsing failed: {e}")
            return self._fallback_intent_parser(text)

    def _fallback_chat(self, prompt: str) -> str:
        """Rule-based simulation fallback chat."""
        prompt_l = prompt.lower()
        if "hello" in prompt_l or "hi " in prompt_l or "hey" in prompt_l:
            return "Hello, Sir. I am online and ready to assist you. How can I help you today?"
        elif "who are you" in prompt_l or "your name" in prompt_l:
            return "I am JARVIS, your personal artificial intelligence desktop assistant."
        elif "thank" in prompt_l:
            return "You are very welcome, Sir. It is my pleasure."
        else:
            return "Sir, I have recorded your input, but I am currently running without a Gemini connection. Please configure your API key."

    def _fallback_intent_parser(self, text: str) -> Dict[str, Any]:
        """Rule-based simple intent parser when Gemini is unavailable."""
        text_l = text.lower().replace("-", "")
        logger.debug(f"Executing rule-based local command matching for: '{text}' (normalized: '{text_l}')")
        
        # 1. Apps
        if "notepad" in text_l:
            return {"intent": "open_app", "action": "open_notepad", "params": {}}
        elif "calculator" in text_l or "calc" in text_l:
            return {"intent": "open_app", "action": "open_calculator", "params": {}}
        elif "command prompt" in text_l or "cmd" in text_l:
            return {"intent": "open_app", "action": "open_command_prompt", "params": {}}
        elif "explorer" in text_l:
            return {"intent": "open_app", "action": "open_file_explorer", "params": {}}
        elif "control panel" in text_l:
            return {"intent": "open_app", "action": "open_control_panel", "params": {}}
        elif "settings" in text_l:
            return {"intent": "open_app", "action": "open_settings", "params": {}}
        elif "camera" in text_l:
            return {"intent": "open_app", "action": "open_camera", "params": {}}
        elif "chrome" in text_l or "google chrome" in text_l or "launch chrome" in text_l:
            return {"intent": "open_app", "action": "open_chrome", "params": {}}
        elif "vs code" in text_l or "vscode" in text_l:
            return {"intent": "open_app", "action": "open_vscode", "params": {}}
            
        # 2. Volume / Brightness / Controls
        elif "volume up" in text_l or "increase volume" in text_l or "volume increase" in text_l:
            return {"intent": "pc_control", "action": "volume_up", "params": {}}
        elif "volume down" in text_l or "decrease volume" in text_l or "volume decrease" in text_l:
            return {"intent": "pc_control", "action": "volume_down", "params": {}}
        elif "unmute" in text_l:
            return {"intent": "pc_control", "action": "unmute", "params": {}}
        elif "mute" in text_l:
            return {"intent": "pc_control", "action": "mute", "params": {}}
        elif "increase brightness" in text_l or "brightness increase" in text_l or "brighter" in text_l:
            return {"intent": "pc_control", "action": "brightness_increase", "params": {}}
        elif "decrease brightness" in text_l or "brightness decrease" in text_l or "dim" in text_l:
            return {"intent": "pc_control", "action": "brightness_decrease", "params": {}}
        elif "screenshot" in text_l or "take screen" in text_l:
            return {"intent": "pc_control", "action": "screenshot", "params": {}}
        elif "wifi on" in text_l or "enable wifi" in text_l:
            return {"intent": "pc_control", "action": "wifi_on", "params": {}}
        elif "wifi off" in text_l or "disable wifi" in text_l:
            return {"intent": "pc_control", "action": "wifi_off", "params": {}}
        elif "bluetooth on" in text_l:
            return {"intent": "pc_control", "action": "bluetooth_on", "params": {}}
        elif "bluetooth off" in text_l:
            return {"intent": "pc_control", "action": "bluetooth_off", "params": {}}
        elif "lock pc" in text_l or "lock computer" in text_l or "lock workstation" in text_l:
            return {"intent": "pc_control", "action": "lock_pc", "params": {}}
        elif "sleep" in text_l:
            return {"intent": "pc_control", "action": "sleep", "params": {}}
        elif "shutdown" in text_l:
            return {"intent": "pc_control", "action": "shutdown", "params": {}}
        elif "restart" in text_l:
            return {"intent": "pc_control", "action": "restart", "params": {}}

        # 3. File Operations
        elif "downloads folder" in text_l or "downloads" in text_l:
            return {"intent": "file_operation", "action": "open_downloads", "params": {}}
        elif "create file" in text_l:
            # "create file notes.txt" -> extract name
            parts = text.split("create file")
            filename = parts[1].strip() if len(parts) > 1 else "untitled.txt"
            return {"intent": "file_operation", "action": "create_file", "params": {"path": filename, "content": ""}}
        elif "delete file" in text_l:
            parts = text.split("delete file")
            filename = parts[1].strip() if len(parts) > 1 else ""
            return {"intent": "file_operation", "action": "delete_file", "params": {"path": filename}}
        elif "rename file" in text_l:
            # "rename file old.txt to new.txt"
            # very basic splitter
            text_norm = text_l.replace("rename file ", "")
            parts = text_norm.split(" to ")
            if len(parts) == 2:
                return {"intent": "file_operation", "action": "rename_file_or_folder", "params": {"old_path": parts[0].strip(), "new_path": parts[1].strip()}}
            return {"intent": "file_operation", "action": "rename_file_or_folder", "params": {"old_path": "", "new_path": ""}}
        
        # 4. Dictation Mode
        elif "start voice typing" in text_l or "start typing" in text_l:
            return {"intent": "voice_typing", "action": "start_typing", "params": {}}

        # 5. Email
        elif "send email to" in text_l:
            # "send email to john@example.com"
            parts = text_l.split("send email to")
            email_addr = parts[1].strip() if len(parts) > 1 else ""
            return {"intent": "email", "action": "send_email", "params": {"to_email": email_addr, "subject": "", "body": ""}}
        elif "read email" in text_l:
            return {"intent": "email", "action": "read_emails", "params": {}}

        # 6. Alarms / Reminders
        elif "stop alarm" in text_l:
            return {"intent": "alarm_reminder", "action": "stop_alarm", "params": {}}
        elif "list reminders" in text_l:
            return {"intent": "alarm_reminder", "action": "list_reminders", "params": {}}
        elif "remind me to" in text_l:
            # Simple fallback reminder set: 5 minutes from now
            rem_text = text.replace("remind me to ", "").strip()
            trigger_time = (datetime.now() + timedelta(minutes=5)).isoformat()
            return {"intent": "alarm_reminder", "action": "set_reminder", "params": {"text": rem_text, "trigger_time": trigger_time}}
        elif "set alarm for" in text_l:
            # extract alarm time "alarm for 08:30"
            import re
            match = re.search(r'(\d{1,2})[.:](\d{2})', text_l)
            if match:
                hh, mm = match.groups()
                time_str = f"{int(hh):02d}:{int(mm):02d}"
                return {"intent": "alarm_reminder", "action": "set_alarm", "params": {"time_hhmm": time_str, "label": "Alarm"}}
            return {"intent": "alarm_reminder", "action": "set_alarm", "params": {"time_hhmm": "08:00", "label": "Alarm"}}

        # 7. Weather
        elif "weather" in text_l or "temp" in text_l or "temperature" in text_l:
            import re
            clean_text = text_l

            # Step 1: Remove multi-word filler phrases (order longest first)
            filler_phrases = [
                "what is the weather today in", "what is the weather today",
                "what is the weather in", "what is the weather of", "what is the weather",
                "what's the weather today in", "what's the weather today",
                "what's the weather in", "what's the weather of", "what's the weather",
                "tell me the weather report of", "tell me the weather report in",
                "tell me the weather report for", "tell me the weather report",
                "tell me the weather in", "tell me the weather of",
                "tell me the weather for", "tell me the weather",
                "tell me about the weather in", "tell me about the weather",
                "how is the weather in", "how is the weather",
                "tell weather report of", "tell weather report in",
                "tell weather report for", "tell weather report",
                "weather report of", "weather report in", "weather report for", "weather report",
                "weather forecast for", "weather forecast in", "weather forecast of", "weather forecast",
                "weather today in", "weather today of", "weather today",
                "what's the temperature in", "what is the temperature in",
                "temperature in", "temperature of", "temperature",
                "weather in", "weather of", "weather for", "weather",
                "tell me", "tell", "report", "temp",
            ]
            for phrase in sorted(filler_phrases, key=len, reverse=True):
                clean_text = clean_text.replace(phrase, " ")

            # Step 2: Strip leftover single filler words from start/end
            filler_words = {"in", "of", "for", "at", "the", "me", "a", "about", "is", "are"}
            words = clean_text.split()
            while words and words[0] in filler_words:
                words.pop(0)
            while words and words[-1] in filler_words:
                words.pop()
            clean_text = " ".join(words)

            # Step 3: Remove any stray non-alphabetic chars (except spaces and hyphens)
            clean_text = re.sub(r"[^a-z\s\-]", "", clean_text).strip()

            city = clean_text.strip()
            logger.debug(f"Extracted city from weather query: '{city}'")
            return {"intent": "weather", "action": "get_weather", "params": {"city": city if city else None}}



        # 8. News
        elif "news" in text_l:
            return {"intent": "news", "action": "get_news", "params": {"country": "us"}}

        # Default Chat
        return {"intent": "chat", "action": "general_conversation", "params": {}}
