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
        """
        Parse natural language command into structured intent.

        Strategy:
        1. Run the local rule-based parser first (fast, no API quota).
        2. If the local parser confidently recognises the command (non-chat intent),
           return immediately — no Gemini call needed.
        3. Only call Gemini for genuine free-form conversation ('chat' intent),
           where the LLM's language understanding actually adds value.
        """
        # --- Step 1: Try local rule-based parser ---
        local_result = self._fallback_intent_parser(text)
        local_intent = local_result.get("intent", "chat")

        # If local parser matched a structured intent, use it immediately
        if local_intent != "chat":
            logger.info(f"Local parser matched: {local_result}")
            return local_result

        # --- Step 2: For alarms/reminders with specific times, prefer Gemini ---
        # because it can correctly compute relative times ("in 5 minutes", "tomorrow at 3pm")
        needs_time_calc = any(kw in text.lower() for kw in [
            "remind me", "set alarm", "alarm for", "reminder for",
            "in 5 minutes", "in an hour", "tomorrow", "at ", "pm", "am"
        ])

        # --- Step 3: Call Gemini only when needed and available ---
        if self.api_available and needs_time_calc:
            current_time_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            system_instruction = (
                f"You are the intent parser for JARVIS, a Windows desktop assistant.\n"
                f"Your job is to parse the user's spoken command into a structured JSON object.\n"
                f"Current local time: {current_time_str}\n\n"
                "Supported intents:\n"
                "- intent: 'alarm_reminder', action: 'set_reminder' (params: 'text', 'trigger_time' in ISO-8601 YYYY-MM-DDTHH:MM:SS)\n"
                "- intent: 'alarm_reminder', action: 'set_alarm' (params: 'time_hhmm' in 24hr 'HH:MM', 'label')\n"
                "- intent: 'chat', action: 'general_conversation' (params: none)\n\n"
                "Output ONLY valid raw JSON without markdown code blocks."
            )
            try:
                import google.generativeai as genai
                response = self.model.generate_content(
                    [system_instruction, f"Parse command: '{text}'"],
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=150,
                    )
                )
                raw = response.text.strip()
                if raw.startswith("```"):
                    lines = raw.splitlines()
                    raw = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:]).strip()
                parsed = json.loads(raw)
                logger.info(f"Gemini parsed alarm/reminder: {parsed}")
                return parsed
            except Exception as e:
                logger.warning(f"Gemini call failed ({e}), using local fallback.")

        # --- Step 4: Return the local 'chat' result (general conversation) ---
        return local_result


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
        """Comprehensive rule-based intent parser when Gemini is unavailable."""
        import re
        t = text.lower().strip()
        logger.debug(f"Fallback parsing: '{t}'")

        # Helper: extract trailing name after a prefix phrase
        def after(prefix: str, src: str = t) -> str:
            idx = src.find(prefix)
            if idx == -1:
                return ""
            return src[idx + len(prefix):].strip()

        # ── 1. OPEN APP ──────────────────────────────────────────────────────
        if "notepad" in t:
            return {"intent": "open_app", "action": "open_notepad", "params": {}}
        if "calculator" in t or "calc" in t:
            return {"intent": "open_app", "action": "open_calculator", "params": {}}
        if "command prompt" in t or " cmd" in t:
            return {"intent": "open_app", "action": "open_command_prompt", "params": {}}
        if "file explorer" in t or "explorer" in t:
            return {"intent": "open_app", "action": "open_file_explorer", "params": {}}
        if "control panel" in t:
            return {"intent": "open_app", "action": "open_control_panel", "params": {}}
        if "settings" in t:
            return {"intent": "open_app", "action": "open_settings", "params": {}}
        if "camera" in t:
            return {"intent": "open_app", "action": "open_camera", "params": {}}
        if "chrome" in t:
            return {"intent": "open_app", "action": "open_chrome", "params": {}}
        if "vs code" in t or "vscode" in t or "visual studio code" in t:
            return {"intent": "open_app", "action": "open_vscode", "params": {}}

        # ── 2. PC CONTROL ────────────────────────────────────────────────────
        if "volume up" in t or "increase volume" in t:
            return {"intent": "pc_control", "action": "volume_up", "params": {}}
        if "volume down" in t or "decrease volume" in t:
            return {"intent": "pc_control", "action": "volume_down", "params": {}}
        if "unmute" in t:
            return {"intent": "pc_control", "action": "unmute", "params": {}}
        if "mute" in t:
            return {"intent": "pc_control", "action": "mute", "params": {}}
        if "brighter" in t or "increase brightness" in t or "brightness up" in t:
            return {"intent": "pc_control", "action": "brightness_increase", "params": {}}
        if "dim" in t or "decrease brightness" in t or "brightness down" in t:
            return {"intent": "pc_control", "action": "brightness_decrease", "params": {}}
        if "screenshot" in t or "take screen" in t or "screen shot" in t:
            return {"intent": "pc_control", "action": "screenshot", "params": {}}
        if "wifi on" in t or "wi-fi on" in t or "enable wifi" in t or "turn on wifi" in t:
            return {"intent": "pc_control", "action": "wifi_on", "params": {}}
        if "wifi off" in t or "wi-fi off" in t or "disable wifi" in t or "turn off wifi" in t:
            return {"intent": "pc_control", "action": "wifi_off", "params": {}}
        if "bluetooth on" in t or "enable bluetooth" in t or "turn on bluetooth" in t:
            return {"intent": "pc_control", "action": "bluetooth_on", "params": {}}
        if "bluetooth off" in t or "disable bluetooth" in t or "turn off bluetooth" in t:
            return {"intent": "pc_control", "action": "bluetooth_off", "params": {}}
        if "lock" in t and ("pc" in t or "computer" in t or "screen" in t or "workstation" in t):
            return {"intent": "pc_control", "action": "lock_pc", "params": {}}
        if "sleep" in t:
            return {"intent": "pc_control", "action": "sleep", "params": {}}
        if "shutdown" in t or "shut down" in t:
            return {"intent": "pc_control", "action": "shutdown", "params": {}}
        if "restart" in t or "reboot" in t:
            return {"intent": "pc_control", "action": "restart", "params": {}}

        # ── 3. FILE OPERATIONS ───────────────────────────────────────────────
        # Open Downloads
        if "download" in t and ("open" in t or "folder" in t or "show" in t):
            return {"intent": "file_operation", "action": "open_downloads", "params": {}}

        # Open Recent
        if "recent" in t and ("file" in t or "open" in t or "show" in t):
            return {"intent": "file_operation", "action": "open_recent", "params": {}}

        # Organize Files
        if "organize" in t:
            for folder in ["desktop", "downloads", "documents", "pictures", "videos", "music"]:
                if folder in t:
                    return {"intent": "file_operation", "action": "organize_files", "params": {"path": folder}}
            return {"intent": "file_operation", "action": "organize_files", "params": {"path": "downloads"}}

        # List folder contents
        if re.search(r'(list|show|what.?s in|contents? of)', t):
            for kw, folder in [("desktop", "desktop"), ("downloads", "downloads"),
                               ("documents", "documents"), ("pictures", "pictures"),
                               ("videos", "videos"), ("music", "music")]:
                if kw in t:
                    return {"intent": "file_operation", "action": "list_folder", "params": {"path": folder}}
            name = re.sub(r'(list|show|what.?s in|contents? of|folder|the|my)', '', t).strip()
            return {"intent": "file_operation", "action": "list_folder", "params": {"path": name}}

        # Move file/folder: "move X to Y"
        mv = re.search(r'move (.+?) to (.+)', t)
        if mv:
            return {"intent": "file_operation", "action": "move_file",
                    "params": {"path": mv.group(1).strip(), "destination": mv.group(2).strip()}}

        # Rename: "rename X to Y"
        rn = re.search(r'rename (.+?) to (.+)', t)
        if rn:
            return {"intent": "file_operation", "action": "rename_file_or_folder",
                    "params": {"old_path": rn.group(1).strip(), "new_path": rn.group(2).strip()}}

        # Delete file
        if re.search(r'delete (file|the file)', t):
            name = re.sub(r'delete (the )?file( named| called)?', '', t).strip()
            return {"intent": "file_operation", "action": "delete_file", "params": {"path": name}}

        # Delete folder
        if re.search(r'delete (folder|directory|the folder)', t):
            name = re.sub(r'delete (the )?(folder|directory)( named| called)?', '', t).strip()
            return {"intent": "file_operation", "action": "delete_folder", "params": {"path": name}}

        # Create file
        if re.search(r'create (a |new )?(file|document|text)', t):
            name = re.sub(r'create (a |new )?(file|document|text file|text)( named| called)?', '', t).strip()
            if not name:
                name = "untitled.txt"
            return {"intent": "file_operation", "action": "create_file", "params": {"path": name, "content": ""}}

        # Create folder
        if re.search(r'create (a |new )?(folder|directory)', t):
            name = re.sub(r'create (a |new )?(folder|directory)( named| called)?', '', t).strip()
            if not name:
                name = "New Folder"
            return {"intent": "file_operation", "action": "create_folder", "params": {"path": name}}

        # Copy file
        if re.search(r'copy (file|the file)?', t):
            name = re.sub(r'copy (the )?(file)?( named| called)?', '', t).strip()
            return {"intent": "file_operation", "action": "copy_file", "params": {"path": name}}

        # Paste file
        if "paste" in t:
            dest = re.sub(r'paste( file| it)?(( to| in| into| on)( the)?)?', '', t).strip()
            dest = dest if dest else "desktop"
            return {"intent": "file_operation", "action": "paste_file", "params": {"destination": dest}}

        # Search files by name
        if re.search(r'(search|find|look for|locate) (file|files|for)', t):
            kw = re.sub(r'(search|find|look for|locate) (for )?(files?|document|the)?( named| called)?', '', t).strip()
            kw = re.sub(r'^for\s+', '', kw).strip()  # strip leading 'for'
            return {"intent": "file_operation", "action": "search_files", "params": {"keyword": kw}}

        # Search documents by content
        if re.search(r'(search|find).+(document|content|text|contain)', t):
            kw = re.sub(r'(search|find|look for).+(in|containing|with|about|inside)', '', t).strip()
            return {"intent": "file_operation", "action": "search_documents", "params": {"keyword": kw}}

        # Open specific folder
        if re.search(r'open (folder|folders|directory)', t):
            name = re.sub(r'open (the )?(folder[s]?|directory)( named| called)?', '', t).strip()
            # resolve common spoken aliases like 'document' -> 'documents'
            spoken_aliases = {
                'document': 'documents', 'download': 'downloads',
                'picture': 'pictures', 'video': 'videos',
                'music': 'music', 'desktop': 'desktop',
            }
            name = spoken_aliases.get(name, name)
            return {"intent": "file_operation", "action": "open_folder", "params": {"path": name}}

        # Open specific file — "open file X", "open the X.pdf", or "open X.pdf"
        if re.search(r'open (file|the file)', t):
            name = re.sub(r'open (the )?(file)?( named| called)?', '', t).strip()
            return {"intent": "file_operation", "action": "open_specific_file", "params": {"path": name}}
        # Catch "open X.ext" where the filename has a known file extension
        file_ext_match = re.search(r'open\s+([\w\s\-]+\.(pdf|docx?|xlsx?|pptx?|txt|png|jpg|mp4|mp3|zip|py|js|html|csv|json))', t)
        if file_ext_match:
            name = file_ext_match.group(1).strip()
            return {"intent": "file_operation", "action": "open_specific_file", "params": {"path": name}}


        # ── 4. VOICE TYPING ──────────────────────────────────────────────────
        if "start voice typing" in t or "start typing" in t or "voice type" in t:
            return {"intent": "voice_typing", "action": "start_typing", "params": {}}

        # ── 5. EMAIL ─────────────────────────────────────────────────────────
        if "send email to" in t:
            addr = after("send email to")
            return {"intent": "email", "action": "send_email",
                    "params": {"to_email": addr, "subject": "", "body": ""}}
        if "read email" in t or "check email" in t:
            return {"intent": "email", "action": "read_emails", "params": {}}

        # ── 6. ALARMS / REMINDERS ────────────────────────────────────────────
        if "stop alarm" in t:
            return {"intent": "alarm_reminder", "action": "stop_alarm", "params": {}}
        if "list reminder" in t or "show reminder" in t:
            return {"intent": "alarm_reminder", "action": "list_reminders", "params": {}}
        if "remind me to" in t:
            from datetime import timedelta
            rem_text = after("remind me to")
            trigger = (datetime.now() + timedelta(minutes=5)).isoformat()
            return {"intent": "alarm_reminder", "action": "set_reminder",
                    "params": {"text": rem_text, "trigger_time": trigger}}
        if "set alarm" in t or "alarm for" in t:
            m = re.search(r'(\d{1,2})[.:]?(\d{2})', t)
            hhmm = f"{int(m.group(1)):02d}:{int(m.group(2)):02d}" if m else "08:00"
            return {"intent": "alarm_reminder", "action": "set_alarm",
                    "params": {"time_hhmm": hhmm, "label": "Alarm"}}

        # 7. Weather
        elif "weather" in t or "temp" in t or "temperature" in t:
            import re
            clean_text = t

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
        elif "news" in t:
            return {"intent": "news", "action": "get_news", "params": {"country": "us"}}

        # Default Chat
        return {"intent": "chat", "action": "general_conversation", "params": {}}
