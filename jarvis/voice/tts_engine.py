import os
import sys
import queue
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from jarvis.utils.logger import logger

# Path to the isolated TTS subprocess script
_SPEAK_SCRIPT = os.path.join(os.path.dirname(__file__), "speak_subprocess.py")
# Python interpreter inside the venv
_PYTHON_EXE = sys.executable


def _speak_out_of_process(text: str, timeout: int = 120) -> bool:
    """
    Speak text in a completely isolated subprocess.
    This avoids ANY COM/Qt conflicts that pyttsx3 has when running inside a Qt app.
    """
    try:
        safe_text = text.strip()
        result = subprocess.run(
            [_PYTHON_EXE, _SPEAK_SCRIPT, safe_text],
            timeout=timeout,
            capture_output=False,  # let audio play directly
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        logger.error("TTS subprocess timed out.")
    except Exception as e:
        logger.error(f"TTS subprocess error: {e}")
    return False


def _speak_via_powershell(text: str, timeout: int = 120) -> bool:
    """Last-resort PowerShell SAPI5 TTS fallback."""
    try:
        safe_text = text.replace("'", "").replace('"', "").replace("\n", " ")
        ps_cmd = (
            f'powershell -Command "Add-Type -AssemblyName System.Speech; '
            f'$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
            f'$s.Rate = 1; $s.Volume = 100; $s.Speak(\'{safe_text}\')"'
        )
        result = subprocess.run(ps_cmd, shell=True, timeout=timeout)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        logger.error("PowerShell TTS timed out.")
    except Exception as e:
        logger.error(f"PowerShell TTS error: {e}")
    return False


class TTSWorker(QThread):
    started_speaking = pyqtSignal(str)
    finished_speaking = pyqtSignal(str)

    def __init__(self, rate: int = 175):
        super().__init__()
        self.speech_queue = queue.Queue()
        self.running = True
        self.rate = rate

    def speak(self, text: str):
        """Enqueue text to be spoken."""
        if text and text.strip():
            self.speech_queue.put(text)
            logger.debug(f"TTSWorker queued: {text[:60]}")

    def stop_speaking(self):
        """Drain the queue and signal the worker to stop."""
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except queue.Empty:
                break
        self.running = False
        self.speech_queue.put(None)  # sentinel
        self.wait()

    def run(self):
        """Worker loop: speak each queued item in an isolated subprocess."""
        logger.info("TTSWorker thread started (subprocess mode).")
        while self.running:
            try:
                text = self.speech_queue.get(timeout=0.5)
                if text is None:
                    break

                logger.info(f"TTS Speaking ({len(text)} chars): {text[:80]}...")
                self.started_speaking.emit(text)

                # Primary: run in an isolated subprocess (no Qt/COM conflict)
                spoken = _speak_out_of_process(text)

                if not spoken:
                    logger.warning("Subprocess TTS failed, trying PowerShell fallback...")
                    spoken = _speak_via_powershell(text)

                if not spoken:
                    logger.error(f"All TTS methods failed for: {text[:60]}")

                self.finished_speaking.emit(text)
                self.speech_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"TTSWorker loop error: {e}")

        logger.info("TTSWorker thread terminated.")


class TTSEngine(QObject):
    started = pyqtSignal(str)
    finished = pyqtSignal(str)

    def __init__(self, rate: int = 175):
        super().__init__()
        self.worker = TTSWorker(rate=rate)
        self.worker.started_speaking.connect(self.started.emit)
        self.worker.finished_speaking.connect(self.finished.emit)
        self.worker.start()
        logger.info("TTSEngine started (subprocess-isolated mode).")

    def speak(self, text: str):
        """Thread-safe: enqueue text for speech."""
        if text and text.strip():
            self.worker.speak(text)

    def shutdown(self):
        """Stop the worker thread cleanly."""
        self.worker.stop_speaking()
        logger.info("TTSEngine shut down.")
