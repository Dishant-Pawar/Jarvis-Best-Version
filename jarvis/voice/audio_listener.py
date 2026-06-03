import time
import speech_recognition as sr
from PyQt6.QtCore import QThread, pyqtSignal
from jarvis.utils.logger import logger
from jarvis.config.settings import WAKE_WORD


def _is_wake_word(text: str) -> bool:
    """Check if text contains the wake word, with fuzzy matching for common misrecognitions."""
    text_l = text.lower().strip()

    # Exact substring match first
    if WAKE_WORD in text_l:
        return True

    # Split wake word into parts (e.g. "hey jarvis" -> ["hey", "jarvis"])
    wake_parts = WAKE_WORD.split()
    if len(wake_parts) < 2:
        return False

    keyword = wake_parts[-1]  # "jarvis"

    # Common misrecognitions of "jarvis"
    fuzzy_variants = [
        keyword,            # jarvis
        keyword[:3],        # jar
        keyword[:4],        # jarv
        "jervis", "javis", "jarves", "jarbis", "jarbus",
        "travis", "jarwis", "service", "jarvish",
    ]

    # Check if any variant appears
    for variant in fuzzy_variants:
        if variant in text_l:
            return True

    return False

class AudioListener(QThread):
    status_changed = pyqtSignal(str)  # "idle", "listening_wake", "listening_command", "listening_typing", "processing"
    wake_word_detected = pyqtSignal()
    command_detected = pyqtSignal(str)
    dictation_detected = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = True
        self.paused = False
        self.mode = "wake"  # "wake", "command", "typing"
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.8
        self.recognizer.pause_threshold = 1.0
        self.recognizer.energy_threshold = 300  # Higher floor to ignore ambient noise
        self.recognizer.operation_timeout = None

    def set_mode(self, mode: str):
        """Set the mode: 'wake', 'command', or 'typing'."""
        self.mode = mode
        self._update_status_signal()
        logger.info(f"AudioListener mode set to: {mode}")

    def pause_listening(self):
        """Pause listening (typically when speaking or processing is active)."""
        self.paused = True
        self.status_changed.emit("idle")
        logger.debug("AudioListener paused listening.")

    def resume_listening(self):
        """Resume listening in the current mode."""
        self.paused = False
        self._update_status_signal()
        logger.debug("AudioListener resumed listening.")

    def stop_listening(self):
        """Stop the background listener thread thread-safely."""
        self.running = False
        self.paused = True
        self.wait()

    def _update_status_signal(self):
        if self.paused:
            self.status_changed.emit("idle")
        elif self.mode == "wake":
            self.status_changed.emit("listening_wake")
        elif self.mode == "command":
            self.status_changed.emit("listening_command")
        elif self.mode == "typing":
            self.status_changed.emit("listening_typing")

    def run(self):
        """Background thread main loop."""
        logger.info("Speech Recognition AudioListener Thread starting...")
        
        try:
            mic = sr.Microphone()
        except Exception as e:
            err_msg = f"Failed to initialize PyAudio / Microphone: {e}"
            logger.error(err_msg)
            self.error_occurred.emit("Microphone error. Check connection.")
            self.status_changed.emit("idle")
            return

        # We use a fixed threshold or let the dynamic threshold adjust from a higher base
        # to prevent ambient fan noise from constantly triggering the recognizer.
        self.recognizer.energy_threshold = 400

        while self.running:
            if self.paused:
                time.sleep(0.2)
                continue

            self._update_status_signal()

            try:
                # Capture audio from the mic
                # Short timeout so we check self.running / self.paused periodically
                # phrase_time_limit prevents listening to excessively long audio inputs
                with mic as source:
                    audio = self.recognizer.listen(source, timeout=3.0, phrase_time_limit=10.0)

                # Check if we got paused or stopped during audio capture
                if not self.running or self.paused:
                    continue

                self.status_changed.emit("processing")
                logger.info("Speech detected, processing audio...")

                # Use standard Google speech-to-text (free API)
                text = self.recognizer.recognize_google(audio).strip()
                logger.info(f"Speech Recognized: \"{text}\"")

                if not text:
                    self._update_status_signal()
                    continue

                if self.mode == "wake":
                    # Look for the wake phrase with fuzzy matching
                    if _is_wake_word(text):
                        logger.info(f"Wake word detected in: '{text}'")
                        self.wake_word_detected.emit()
                    else:
                        logger.debug(f"Ignored: wake word not in '{text.lower()}'")
                        self._update_status_signal()

                elif self.mode == "command":
                    self.command_detected.emit(text)

                elif self.mode == "typing":
                    self.dictation_detected.emit(text)

            except sr.WaitTimeoutError:
                # Normal timeout when silence is detected
                continue
            except sr.UnknownValueError:
                # Speech was heard but not recognized — cooldown to avoid rapid-fire retries
                logger.debug("Speech heard but could not be parsed.")
                self._update_status_signal()
                time.sleep(0.5)
            except sr.RequestError as e:
                logger.error(f"Speech recognition service request error: {e}")
                self.error_occurred.emit("Speech recognition service error.")
                time.sleep(1.0)
            except Exception as e:
                logger.error(f"Error in speech listening loop: {e}")
                time.sleep(0.5)

        logger.info("Speech Recognition AudioListener Thread terminated.")
