import os
import json
import time
from datetime import datetime, timedelta
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from jarvis.utils.logger import logger
from jarvis.config.settings import LOG_DIR

class SchedulerWorker(QThread):
    # Signals
    reminder_triggered = pyqtSignal(str)  # Emits reminder text
    alarm_triggered = pyqtSignal(int, str)  # Emits (alarm_id, label)
    tick = pyqtSignal()

    def __init__(self, service):
        super().__init__()
        self.service = service
        self.running = True

    def run(self):
        logger.info("Scheduler polling thread started.")
        while self.running:
            self.tick.emit()
            now = datetime.now()
            
            # Check reminders
            reminders_changed = False
            for r in self.service.reminders:
                if not r.get("triggered", False):
                    try:
                        r_time = datetime.fromisoformat(r["time"])
                        if now >= r_time:
                            logger.info(f"Triggering reminder: {r['text']}")
                            r["triggered"] = True
                            self.reminder_triggered.emit(r["text"])
                            reminders_changed = True
                    except Exception as e:
                        logger.error(f"Error checking reminder time: {e}")

            # Clean up triggered reminders to keep list small
            if reminders_changed:
                self.service.reminders = [r for r in self.service.reminders if not r.get("triggered", False)]
                self.service.save_data()

            # Check alarms
            time_str = now.strftime("%H:%M")
            for a in self.service.alarms:
                # Alarms trigger based on HH:MM match
                if a["time"] == time_str:
                    # Trigger once per minute maximum
                    last_trigger = a.get("last_triggered_date", "")
                    today_str = now.strftime("%Y-%m-%d")
                    if last_trigger != today_str:
                        logger.info(f"Triggering alarm {a['id']}: {a['label']}")
                        a["last_triggered_date"] = today_str
                        self.service.save_data()
                        self.alarm_triggered.emit(a["id"], a["label"])

            # Poll once per second
            time.sleep(1.0)

        logger.info("Scheduler polling thread stopped.")


class ReminderService(QObject):
    reminder_alert = pyqtSignal(str)
    alarm_alert = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.data_file = LOG_DIR / "scheduler_data.json"
        self.reminders = []
        self.alarms = []
        self.ringing_alarm_id = None
        
        self.load_data()

        # Start Scheduler Thread
        self.worker = SchedulerWorker(self)
        self.worker.reminder_triggered.connect(self._on_reminder_triggered)
        self.worker.alarm_triggered.connect(self._on_alarm_triggered)
        self.worker.start()

    def load_data(self):
        """Load reminders and alarms from persistent storage."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.reminders = data.get("reminders", [])
                    self.alarms = data.get("alarms", [])
                    logger.info("Scheduler data loaded successfully.")
                    return
            except Exception as e:
                logger.error(f"Failed to load scheduler data: {e}")
        
        self.reminders = []
        self.alarms = []

    def save_data(self):
        """Save reminders and alarms to persistent storage."""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "reminders": self.reminders,
                    "alarms": self.alarms
                }, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save scheduler data: {e}")

    def add_reminder(self, text: str, trigger_time: datetime) -> str:
        """Add a new reminder at a specific datetime."""
        reminder_id = int(time.time() * 1000)
        time_iso = trigger_time.isoformat()
        
        self.reminders.append({
            "id": reminder_id,
            "text": text,
            "time": time_iso,
            "triggered": False
        })
        self.save_data()
        
        time_display = trigger_time.strftime("%I:%M %p on %Y-%m-%d")
        msg = f"Reminder set for '{text}' at {time_display}."
        logger.info(msg)
        return msg

    def delete_reminder(self, keyword: str) -> str:
        """Delete reminder(s) containing the keyword in their description."""
        initial_len = len(self.reminders)
        self.reminders = [r for r in self.reminders if keyword.lower() not in r["text"].lower()]
        
        if len(self.reminders) < initial_len:
            self.save_data()
            msg = f"Deleted reminder matching '{keyword}'."
        else:
            msg = f"No reminder found matching '{keyword}'."
        
        logger.info(msg)
        return msg

    def list_reminders(self) -> str:
        """Return a string listing all active reminders."""
        active = [r for r in self.reminders if not r.get("triggered", False)]
        if not active:
            return "You have no active reminders."
            
        lines = []
        for r in active:
            r_time = datetime.fromisoformat(r["time"])
            time_str = r_time.strftime("%I:%M %p on %Y-%m-%d")
            lines.append(f"'{r['text']}' at {time_str}")
            
        return "Your active reminders are: " + "; ".join(lines)

    def add_alarm(self, time_hhmm: str, label: str = "Alarm") -> str:
        """Add a recurring daily alarm (time format: HH:MM, e.g. '08:30')."""
        # Validate HH:MM format
        try:
            datetime.strptime(time_hhmm, "%H:%M")
        except ValueError:
            return "Invalid alarm time format. Use HH:MM in 24-hour format."

        alarm_id = int(time.time() * 1000)
        self.alarms.append({
            "id": alarm_id,
            "time": time_hhmm,
            "label": label,
            "last_triggered_date": ""
        })
        self.save_data()
        
        # Display as 12-hour format
        t_obj = datetime.strptime(time_hhmm, "%H:%M")
        time_display = t_obj.strftime("%I:%M %p")
        msg = f"Alarm '{label}' set for {time_display} daily."
        logger.info(msg)
        return msg

    def delete_alarm(self, time_hhmm: str) -> str:
        """Delete alarm set at a specific HH:MM time."""
        initial_len = len(self.alarms)
        self.alarms = [a for a in self.alarms if a["time"] != time_hhmm]
        
        if len(self.alarms) < initial_len:
            self.save_data()
            msg = f"Deleted alarm for {time_hhmm}."
        else:
            msg = f"No alarm found at {time_hhmm}."
            
        logger.info(msg)
        return msg

    def stop_alarm(self) -> str:
        """Silence the currently ringing alarm."""
        if self.ringing_alarm_id is not None:
            logger.info(f"Stopping ringing alarm ID: {self.ringing_alarm_id}")
            self.ringing_alarm_id = None
            return "Alarm stopped."
        return "There is no alarm active or ringing right now."

    def _on_reminder_triggered(self, text: str):
        logger.info(f"Reminder triggered callback: {text}")
        self.reminder_alert.emit(f"Reminder: {text}")

    def _on_alarm_triggered(self, alarm_id: int, label: str):
        logger.info(f"Alarm triggered callback: ID={alarm_id}, label={label}")
        self.ringing_alarm_id = alarm_id
        self.alarm_alert.emit(f"Alarm '{label}' is ringing!")

    def shutdown(self):
        """Gracefully stop the scheduler thread."""
        self.worker.running = False
        self.worker.wait()
