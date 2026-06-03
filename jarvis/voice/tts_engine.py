import queue
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from jarvis.utils.logger import logger

class TTSWorker(QThread):
    started_speaking = pyqtSignal(str)
    finished_speaking = pyqtSignal(str)

    def __init__(self, voice_id=None, rate=185):
        super().__init__()
        self.queue = queue.Queue()
        self.running = True
        self.voice_id = voice_id
        self.rate = rate

    def speak(self, text: str):
        """Enqueue text to be spoken."""
        if text and text.strip():
            self.queue.put(text)

    def stop_speaking(self):
        """Clear remaining speeches and stop the worker."""
        # Drain queue
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
                self.queue.task_done()
            except queue.Empty:
                break
        self.running = False
        self.queue.put(None)  # Sentinel to exit loop
        self.wait()

    def run(self):
        """Thread main loop initializing COM and pyttsx3."""
        # COM initialization is mandatory for SAPI5 in python threads
        import pythoncom
        import pyttsx3
        
        pythoncom.CoInitialize()
        try:
            logger.info("Initializing TTS Engine in background thread...")
            engine = pyttsx3.init()
            
            # Configure voice speed
            engine.setProperty('rate', self.rate)
            
            # Select voice if specified, else search for a standard voice
            voices = engine.getProperty('voices')
            if self.voice_id:
                engine.setProperty('voice', self.voice_id)
            elif voices:
                # Try to use a female voice (often index 1 on Windows) or default index 0
                selected_voice = voices[0].id
                for voice in voices:
                    if "zira" in voice.name.lower() or "hazel" in voice.name.lower() or "female" in voice.name.lower():
                        selected_voice = voice.id
                        break
                engine.setProperty('voice', selected_voice)

            logger.info(f"TTS Engine configured. Selected Voice: {engine.getProperty('voice')}")

            while self.running:
                try:
                    # Block on queue for up to 0.5s
                    text = self.queue.get(timeout=0.5)
                    if text is None:
                        break
                    
                    self.started_speaking.emit(text)
                    logger.debug(f"TTS Speaking: {text}")
                    engine.say(text)
                    engine.runAndWait()
                    self.finished_speaking.emit(text)
                    self.queue.task_done()
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Error in TTS playback loop: {e}")
        except Exception as e:
            logger.critical(f"Failed to initialize TTS engine: {e}")
        finally:
            pythoncom.CoUninitialize()
            logger.info("TTS Worker thread terminated and COM uninitialized.")


class TTSEngine(QObject):
    started = pyqtSignal(str)
    finished = pyqtSignal(str)

    def __init__(self, voice_id=None, rate=185):
        super().__init__()
        self.worker = TTSWorker(voice_id, rate)
        self.worker.started_speaking.connect(self.started.emit)
        self.worker.finished_speaking.connect(self.finished.emit)
        self.worker.start()

    def speak(self, text: str):
        """Thread-safe speak function."""
        self.worker.speak(text)

    def shutdown(self):
        """Properly stops the background speaker thread."""
        self.worker.stop_speaking()
