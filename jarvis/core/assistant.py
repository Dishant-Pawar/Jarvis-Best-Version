import os
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from jarvis.utils.logger import logger

# Voice components
from jarvis.voice.audio_listener import AudioListener
from jarvis.voice.tts_engine import TTSEngine

# Services
from jarvis.services.gemini_service import GeminiService
from jarvis.services.weather_service import WeatherService
from jarvis.services.news_service import NewsService
from jarvis.services.email_service import EmailService
from jarvis.services.reminder_service import ReminderService

# Automation
from jarvis.automation.system_apps import SystemApps
from jarvis.automation.pc_control import PCControl
from jarvis.automation.file_manager import FileManager
from jarvis.automation.voice_typing import VoiceTyping

# Core Parser
from jarvis.core.command_parser import CommandParser


class Assistant(QObject):
    # Signals for UI communication
    status_changed = pyqtSignal(str)          # Current assistant status message
    speech_status_changed = pyqtSignal(str)   # "idle", "listening_wake", "listening_command", "listening_typing", "processing"
    response_ready = pyqtSignal(str)          # Jarvis' spoken response text
    error_occurred = pyqtSignal(str)          # Error message to show in UI

    def __init__(self):
        super().__init__()
        logger.info("Initializing JARVIS Assistant Orchestrator...")
        
        # Initialize Core Services
        self.gemini = GeminiService()
        self.parser = CommandParser(self.gemini)
        self.reminder_service = ReminderService()
        self.tts = TTSEngine()
        
        # Listening thread
        self.listener = AudioListener()

        # State Variables
        self.chat_history = []
        self.pending_action = None           # Stores metadata for multi-turn steps
        self.is_waiting_for_input = False    # True when waiting for multi-turn answer
        self.is_running = False
        self.post_speak_action = None        # Callback to execute after TTS finishes speaking

        # Connect Signals
        self.listener.status_changed.connect(self._on_speech_status_changed)
        self.listener.wake_word_detected.connect(self._on_wake_word_detected)
        self.listener.command_detected.connect(self._on_command_detected)
        self.listener.dictation_detected.connect(self._on_dictation_detected)
        self.listener.error_occurred.connect(self.error_occurred.emit)

        self.tts.started.connect(self._on_tts_started)
        self.tts.finished.connect(self._on_tts_finished)

        # Connect Reminder alerts
        self.reminder_service.reminder_alert.connect(self._on_reminder_alert)
        self.reminder_service.alarm_alert.connect(self._on_alarm_alert)

        logger.info("JARVIS Assistant Orchestrator initialized successfully.")

    def start(self):
        """Start background listening."""
        if not self.is_running:
            logger.info("Starting JARVIS Assistant...")
            self.is_running = True
            self.listener.set_mode("wake")
            self.listener.start()
            self.status_changed.emit("Jarvis is online. Say 'Hey Jarvis' to wake.")
            self.speak("Jarvis is online and ready, Sir.")

    def stop(self):
        """Stop background services."""
        if self.is_running:
            logger.info("Stopping JARVIS Assistant...")
            self.is_running = False
            self.listener.stop_listening()
            self.reminder_service.shutdown()
            self.tts.shutdown()
            self.status_changed.emit("Jarvis is offline.")

    def speak(self, text: str, post_action: str = None):
        """Speak a response through TTS, pausing the listener and registering post-speak tasks."""
        self.listener.pause_listening()
        self.post_speak_action = post_action
        self.response_ready.emit(text)
        self.tts.speak(text)

    # --- VOICE EVENT SLOTS ---

    @pyqtSlot(str)
    def _on_speech_status_changed(self, status: str):
        self.speech_status_changed.emit(status)

    @pyqtSlot()
    def _on_wake_word_detected(self):
        logger.info("Wake word callback triggered in Assistant.")
        self.status_changed.emit("Waking up...")
        # Respond and switch to command mode after speaking
        self.speak("Yes Sir, I'm listening.", post_action="enter_command_mode")

    @pyqtSlot(str)
    def _on_command_detected(self, text: str):
        logger.info(f"Command heard: '{text}'")
        self.status_changed.emit(f"Heard: '{text}'")
        
        # 1. Check if we are waiting for multi-turn input
        if self.is_waiting_for_input and self.pending_action:
            self._handle_multiturn_input(text)
            return

        # 2. Parse command
        try:
            parsed = self.parser.parse(text)
            self._execute_action(parsed, text)
        except Exception as e:
            logger.error(f"Error processing command '{text}': {e}")
            self.speak("Sorry Sir, I encountered an error processing that command.", post_action="enter_wake_mode")

    @pyqtSlot(str)
    def _on_dictation_detected(self, text: str):
        # In dictation mode, we type everything unless user requests to stop
        text_l = text.lower()
        if "stop voice typing" in text_l or "stop dictation" in text_l:
            self.listener.pause_listening()
            self.listener.set_mode("wake")
            self.speak("Stopping voice typing, Sir.", post_action="enter_wake_mode")
        else:
            # Type text using typing automation
            VoiceTyping.type_text(text)
            # Re-enable listening immediately (without TTS)
            self.listener.resume_listening()

    @pyqtSlot(str)
    def _on_tts_started(self, text: str):
        self.status_changed.emit("Speaking...")
        # Emit speech_status_changed so the waveform animates in speaking state
        self.speech_status_changed.emit("speaking")

    @pyqtSlot(str)
    def _on_tts_finished(self, text: str):
        self.status_changed.emit("Idle")
        self.speech_status_changed.emit("idle")
        
        # Handle registered callbacks
        action = self.post_speak_action
        self.post_speak_action = None  # Clear
        
        if action == "enter_command_mode":
            self.listener.set_mode("command")
            self.listener.resume_listening()
        elif action == "enter_wake_mode":
            self.listener.set_mode("wake")
            self.listener.resume_listening()
        elif action == "enter_typing_mode":
            self.listener.set_mode("typing")
            self.listener.resume_listening()
        else:
            # By default, return to wake word listening
            self.listener.set_mode("wake")
            self.listener.resume_listening()

    # --- REMINDER/ALARM SLOTS ---

    @pyqtSlot(str)
    def _on_reminder_alert(self, text: str):
        logger.info(f"Triggering reminder TTS: {text}")
        self.speak(f"Sir, I have a reminder for you: {text}", post_action="enter_wake_mode")

    @pyqtSlot(str)
    def _on_alarm_alert(self, message: str):
        logger.info(f"Triggering alarm TTS: {message}")
        # Keep announcing alarm until user stops it
        self.speak(f"Attention, Sir! {message} Say stop alarm to silence.", post_action="enter_command_mode")

    # --- MULTI-TURN PROCESSOR ---

    def _handle_multiturn_input(self, text: str):
        """Process the secondary input of a multi-turn conversation (e.g. Email body)."""
        action_type = self.pending_action.get("action")
        
        if action_type == "send_email":
            params = self.pending_action.get("params", {})
            to_email = params.get("to_email")
            subject = "Message from JARVIS Assistant"
            body = text
            
            self.status_changed.emit("Sending email...")
            success, msg = EmailService.send_email(to_email, subject, body)
            
            # Clear state
            self.is_waiting_for_input = False
            self.pending_action = None
            
            if success:
                self.speak(f"Email sent successfully to {to_email}, Sir.", post_action="enter_wake_mode")
            else:
                self.speak("Sorry Sir, I failed to send the email.", post_action="enter_wake_mode")

    # --- ACTION EXECUTION ROUTER ---

    def _execute_action(self, parsed: dict, original_text: str):
        """Router matching parsed intent to core automation modules and services."""
        intent = parsed.get("intent")
        action = parsed.get("action")
        params = parsed.get("params", {})

        logger.info(f"Executing: Intent={intent}, Action={action}, Params={params}")
        
        # -- 1. OPEN APPLICATION INTENT --
        if intent == "open_app":
            success = False
            app_name = action.replace("open_", "")
            
            if action == "open_notepad":
                success = SystemApps.open_notepad()
            elif action == "open_calculator":
                success = SystemApps.open_calculator()
            elif action == "open_command_prompt":
                success = SystemApps.open_command_prompt()
            elif action == "open_file_explorer":
                success = SystemApps.open_file_explorer()
            elif action == "open_control_panel":
                success = SystemApps.open_control_panel()
            elif action == "open_settings":
                success = SystemApps.open_settings()
            elif action == "open_camera":
                success = SystemApps.open_camera()
            elif action == "open_chrome":
                success = SystemApps.open_chrome()
            elif action == "open_vscode":
                success = SystemApps.open_vscode()

            if success:
                self.speak(f"Opening {app_name.replace('_', ' ')}.", post_action="enter_wake_mode")
            else:
                self.speak(f"Sorry Sir, I was unable to open {app_name.replace('_', ' ')}.", post_action="enter_wake_mode")

        # -- 2. SYSTEM CONTROL INTENT --
        elif intent == "pc_control":
            if action in ["volume_up", "volume up", "volume_down", "volume down", "mute", "unmute"]:
                try:
                    if action in ["volume_up", "volume up"]:
                        PCControl.change_volume(10)
                        logger.info("Volume increased")
                        self.speak("Volume increased, Sir.", post_action="enter_wake_mode")
                    elif action in ["volume_down", "volume down"]:
                        PCControl.change_volume(-10)
                        logger.info("Volume decreased")
                        self.speak("Volume decreased, Sir.", post_action="enter_wake_mode")
                    elif action == "mute":
                        PCControl.mute_audio(True)
                        logger.info("Audio muted")
                        self.speak("System muted.", post_action="enter_wake_mode")
                    elif action == "unmute":
                        PCControl.mute_audio(False)
                        logger.info("Audio unmuted")
                        self.speak("System unmuted, Sir.", post_action="enter_wake_mode")
                except Exception as e:
                    logger.error(f"Audio Control Error: {e}")
                    self.speak("I couldn't control the audio.", post_action="enter_wake_mode")
            elif action == "brightness_increase":
                PCControl.change_brightness(15)
                self.speak("Brightness increased.", post_action="enter_wake_mode")
            elif action == "brightness_decrease":
                PCControl.change_brightness(-15)
                self.speak("Brightness decreased.", post_action="enter_wake_mode")
            elif action == "screenshot":
                path = PCControl.take_screenshot()
                if path:
                    self.speak("Screenshot taken and saved to Desktop, Sir.", post_action="enter_wake_mode")
                else:
                    self.speak("I was unable to capture a screenshot.", post_action="enter_wake_mode")
            elif action == "wifi_on":
                PCControl.toggle_wifi(True)
                self.speak("Turning Wi-Fi on.", post_action="enter_wake_mode")
            elif action == "wifi_off":
                PCControl.toggle_wifi(False)
                self.speak("Turning Wi-Fi off.", post_action="enter_wake_mode")
            elif action == "bluetooth_on":
                PCControl.toggle_bluetooth(True)
                self.speak("Turning Bluetooth on.", post_action="enter_wake_mode")
            elif action == "bluetooth_off":
                PCControl.toggle_bluetooth(False)
                self.speak("Turning Bluetooth off.", post_action="enter_wake_mode")
            elif action == "lock_pc":
                self.speak("Locking workstation, Sir.", post_action="enter_wake_mode")
                PCControl.lock_pc()
            elif action == "sleep":
                self.speak("Putting the system to sleep, Sir.", post_action="enter_wake_mode")
                PCControl.sleep_mode()
            elif action == "shutdown":
                self.speak("Initiating system shutdown. Goodbye, Sir.", post_action="enter_wake_mode")
                PCControl.shutdown_pc()
            elif action == "restart":
                self.speak("Initiating system restart, Sir.", post_action="enter_wake_mode")
                PCControl.restart_pc()

        # -- 3. FILE OPERATIONS INTENT --
        elif intent == "file_operation":
            path     = params.get("path", "")
            dest     = params.get("destination", "")
            keyword  = params.get("keyword", "")
            old_path = params.get("old_path", "")
            new_path = params.get("new_path", "")
            content  = params.get("content", "")

            if action == "open_downloads":
                FileManager.open_downloads_folder()
                self.speak("Opening your Downloads folder, Sir.", post_action="enter_wake_mode")

            elif action == "open_folder":
                ok, result = FileManager.open_folder(path)
                if ok:
                    self.speak(f"Opening folder {os.path.basename(result)}, Sir.", post_action="enter_wake_mode")
                else:
                    self.speak(f"Sorry Sir, I could not find the folder '{path}'.", post_action="enter_wake_mode")

            elif action == "open_specific_file":
                ok, result = FileManager.open_specific_file(path)
                if ok:
                    self.speak(f"Opening file {os.path.basename(result)}, Sir.", post_action="enter_wake_mode")
                else:
                    self.speak(f"Sorry Sir, I could not find the file '{path}'.", post_action="enter_wake_mode")

            elif action == "open_recent":
                recent = FileManager.get_recent_files(limit=3)
                if recent:
                    names = ", ".join(os.path.basename(f) for f in recent)
                    self.speak(f"Your most recent files are: {names}.", post_action="enter_wake_mode")
                else:
                    self.speak("No recent files found, Sir.", post_action="enter_wake_mode")

            elif action == "create_file":
                ok, result = FileManager.create_file(path or "untitled.txt", content)
                if ok:
                    self.speak(f"File {os.path.basename(result)} created on Desktop, Sir.", post_action="enter_wake_mode")
                else:
                    self.speak(f"Sorry Sir, I could not create the file. {result}", post_action="enter_wake_mode")

            elif action == "create_folder":
                ok, result = FileManager.create_folder(path or "New Folder")
                if ok:
                    self.speak(f"Folder {os.path.basename(result)} created on Desktop, Sir.", post_action="enter_wake_mode")
                else:
                    self.speak(f"Sorry Sir, I could not create the folder. {result}", post_action="enter_wake_mode")

            elif action == "delete_file":
                ok, result = FileManager.delete_file(path)
                if ok:
                    self.speak(f"File {os.path.basename(result)} deleted, Sir.", post_action="enter_wake_mode")
                else:
                    self.speak(f"Sorry Sir, I could not find or delete the file '{path}'.", post_action="enter_wake_mode")

            elif action == "delete_folder":
                ok, result = FileManager.delete_folder(path)
                if ok:
                    self.speak(f"Folder {os.path.basename(result)} deleted, Sir.", post_action="enter_wake_mode")
                else:
                    self.speak(f"Sorry Sir, I could not find or delete the folder '{path}'.", post_action="enter_wake_mode")

            elif action == "rename_file_or_folder":
                ok, result = FileManager.rename_file_or_folder(old_path, new_path)
                if ok:
                    self.speak(f"Renamed to {os.path.basename(result)}, Sir.", post_action="enter_wake_mode")
                else:
                    self.speak(f"Sorry Sir, I could not rename '{old_path}'. {result}", post_action="enter_wake_mode")

            elif action == "move_file":
                ok, result = FileManager.move_file_or_folder(path, dest)
                if ok:
                    self.speak(f"Moved {os.path.basename(result)} to {dest}, Sir.", post_action="enter_wake_mode")
                else:
                    self.speak(f"Sorry Sir, I could not move '{path}' to '{dest}'. {result}", post_action="enter_wake_mode")

            elif action == "copy_file":
                ok, result = FileManager.copy_file(path)
                if ok:
                    self.speak(f"Copied {os.path.basename(result)} to clipboard, Sir.", post_action="enter_wake_mode")
                else:
                    self.speak(f"Sorry Sir, I could not find '{path}' to copy.", post_action="enter_wake_mode")

            elif action == "paste_file":
                ok, result = FileManager.paste_file(dest or "desktop")
                if ok:
                    self.speak(f"Pasted file to {dest}, Sir.", post_action="enter_wake_mode")
                else:
                    self.speak(f"Sorry Sir, I could not paste. {result}", post_action="enter_wake_mode")

            elif action == "search_files":
                results = FileManager.search_files(keyword)
                if results:
                    count = len(results)
                    first = os.path.basename(results[0])
                    loc   = os.path.dirname(results[0])
                    self.speak(
                        f"Sir, I found {count} match{'es' if count > 1 else ''} for '{keyword}'. "
                        f"The first one is {first} in {os.path.basename(loc)}.",
                        post_action="enter_wake_mode"
                    )
                else:
                    self.speak(f"No files matching '{keyword}' were found, Sir.", post_action="enter_wake_mode")

            elif action == "search_documents":
                results = FileManager.search_documents_by_content(keyword)
                if results:
                    count = len(results)
                    first = os.path.basename(results[0])
                    self.speak(
                        f"Sir, I found {count} document{'s' if count > 1 else ''} containing '{keyword}'. "
                        f"The first one is {first}.",
                        post_action="enter_wake_mode"
                    )
                else:
                    self.speak(f"No documents containing '{keyword}' were found, Sir.", post_action="enter_wake_mode")

            elif action == "list_folder":
                ok, entries = FileManager.list_folder_contents(path)
                if ok and entries:
                    count = len(entries)
                    preview = ", ".join(entries[:5])
                    more = f" and {count - 5} more" if count > 5 else ""
                    self.speak(
                        f"Sir, {os.path.basename(path)} contains {count} item{'s' if count > 1 else ''}. "
                        f"Including: {preview}{more}.",
                        post_action="enter_wake_mode"
                    )
                elif ok:
                    self.speak(f"The folder '{path}' is empty, Sir.", post_action="enter_wake_mode")
                else:
                    self.speak(f"Sorry Sir, I could not find the folder '{path}'.", post_action="enter_wake_mode")

            elif action == "organize_files":
                ok, msg = FileManager.organize_files_automatically(path or "downloads")
                if ok:
                    self.speak(f"Sir, {msg}", post_action="enter_wake_mode")
                else:
                    self.speak(f"Sorry Sir, I could not organize the folder. {msg}", post_action="enter_wake_mode")

            else:
                self.speak(f"Sorry Sir, I don't know how to perform the file action '{action}'.", post_action="enter_wake_mode")


        # -- 4. ALARMS & REMINDERS INTENT --
        elif intent == "alarm_reminder":
            if action == "set_reminder":
                rem_text = params.get("text", "")
                trig_time_str = params.get("trigger_time", "")
                
                try:
                    trigger_dt = datetime.fromisoformat(trig_time_str)
                    result_msg = self.reminder_service.add_reminder(rem_text, trigger_dt)
                    self.speak(result_msg, post_action="enter_wake_mode")
                except Exception as e:
                    logger.error(f"Error setting reminder: {e}")
                    self.speak("Sorry Sir, I could not parse the time for the reminder.", post_action="enter_wake_mode")
            
            elif action == "delete_reminder":
                keyword = params.get("keyword", "")
                result_msg = self.reminder_service.delete_reminder(keyword)
                self.speak(result_msg, post_action="enter_wake_mode")
                
            elif action == "list_reminders":
                result_msg = self.reminder_service.list_reminders()
                self.speak(result_msg, post_action="enter_wake_mode")
                
            elif action == "set_alarm":
                time_hhmm = params.get("time_hhmm", "")
                label = params.get("label", "Alarm")
                result_msg = self.reminder_service.add_alarm(time_hhmm, label)
                self.speak(result_msg, post_action="enter_wake_mode")
                
            elif action == "delete_alarm":
                time_hhmm = params.get("time_hhmm", "")
                result_msg = self.reminder_service.delete_alarm(time_hhmm)
                self.speak(result_msg, post_action="enter_wake_mode")
                
            elif action == "stop_alarm":
                result_msg = self.reminder_service.stop_alarm()
                self.speak(result_msg, post_action="enter_wake_mode")

        # -- 5. EMAIL INTENT --
        elif intent == "email":
            if action == "send_email":
                to_email = params.get("to_email", "")
                
                if not to_email:
                    self.speak("Who should I send the email to, Sir?", post_action="enter_command_mode")
                    return
                
                # Multi-turn trigger: Ask what to write
                self.is_waiting_for_input = True
                self.pending_action = {
                    "action": "send_email",
                    "params": {"to_email": to_email}
                }
                self.speak("What should I write?", post_action="enter_command_mode")
                
            elif action == "read_emails":
                details = EmailService.read_recent_emails(limit=3)
                self.speak(details, post_action="enter_wake_mode")

        # -- 6. WEATHER INTENT --
        elif intent == "weather":
            city = params.get("city", "")
            report = WeatherService.get_weather(city)
            self.speak(report, post_action="enter_wake_mode")

        # -- 7. NEWS INTENT --
        elif intent == "news":
            country = params.get("country", "")
            report = NewsService.get_news_headlines(country)
            self.speak(report, post_action="enter_wake_mode")

        # -- 8. VOICE TYPING START INTENT --
        elif intent == "voice_typing":
            if action == "start_typing":
                self.speak("Starting voice typing mode. Dictate your text. Say 'stop voice typing' to exit.", post_action="enter_typing_mode")

        # -- 9. CHAT ASSISTANT INTENT (FALLBACK) --
        else:
            self.status_changed.emit("Thinking...")
            try:
                # Query Gemini
                response = self.gemini.chat_response(original_text, self.chat_history)
                # Update Chat history
                self.chat_history.append({"role": "user", "content": original_text})
                self.chat_history.append({"role": "model", "content": response})
                # Limit history to latest 10 turns
                if len(self.chat_history) > 20:
                    self.chat_history = self.chat_history[-20:]
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                response = "Sorry Sir, I wasn't able to reach my AI service right now."
                
            self.speak(response, post_action="enter_wake_mode")
