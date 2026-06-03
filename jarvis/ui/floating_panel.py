import sys
import random
import math
from PyQt6.QtWidgets import QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QPainter, QColor, QPen, QMouseEvent
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSlot

from jarvis.ui.theme import DARK_THEME_STYLE
from jarvis.core.assistant import Assistant

class WaveformWidget(QWidget):
    """Custom paint widget that renders a modern glowing audio waveform."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.status = "idle"
        self.phase = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_wave)
        self.timer.start(40)  # 25 FPS for smooth animation
        self.setObjectName("Waveform")

    def set_status(self, status: str):
        self.status = status
        self.update()

    def _update_wave(self):
        if self.status != "idle":
            self.phase += 1
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        mid_y = height // 2
        
        # Determine number of bars, color, and thickness based on state
        if self.status == "listening_wake":
            color = QColor(6, 182, 212, 220)  # cyan-500
            num_bars = 20
            bar_thickness = 3
        elif self.status == "listening_command":
            color = QColor(6, 182, 212, 255)  # brighter cyan
            num_bars = 24
            bar_thickness = 3
        elif self.status == "listening_typing":
            color = QColor(245, 158, 11, 240)  # amber-500
            num_bars = 24
            bar_thickness = 3
        elif self.status == "processing":
            color = QColor(168, 85, 247, 240)  # purple-500
            num_bars = 20
            bar_thickness = 3
        elif self.status == "speaking":
            color = QColor(34, 197, 94, 255)  # green-500
            num_bars = 28
            bar_thickness = 4
        else:  # idle
            color = QColor(148, 163, 184, 100)  # slate-400 with high opacity
            num_bars = 16
            bar_thickness = 2
            
        pen = QPen(color, bar_thickness, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        spacing = 5
        total_width = num_bars * bar_thickness + (num_bars - 1) * spacing
        start_x = (width - total_width) // 2
        
        for i in range(num_bars):
            x = start_x + i * (bar_thickness + spacing)
            
            # Amplitude algorithm per state
            if self.status == "idle":
                # Static tiny flutter
                amp = int(2 + math.sin(i * 0.5) * 1.5)
            elif self.status == "listening_wake":
                # Slow wave
                amp = int(10 + math.sin(self.phase * 0.15 + i * 0.4) * 8)
            elif self.status == "listening_command":
                # Active waves
                amp = int(12 + math.sin(self.phase * 0.25 + i * 0.5) * 10)
            elif self.status == "listening_typing":
                # Dictation waves
                amp = int(10 + math.cos(self.phase * 0.20 + i * 0.4) * 9)
            elif self.status == "processing":
                # Calm rhythmic pulse
                amp = int(6 + math.sin(self.phase * 0.1 + i * 0.2) * 4)
            elif self.status == "speaking":
                # High amplitude speech simulation
                random.seed(self.phase // 2 + i)
                amp = random.randint(4, height // 2 - 4)
            else:
                amp = 2
                
            painter.drawLine(x, mid_y - amp, x, mid_y + amp)


class FloatingPanel(QWidget):
    def __init__(self, assistant: Assistant):
        super().__init__()
        self.assistant = assistant
        self.drag_position = QPoint()

        # Configure Frameless, Always on Top, Translucent window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet(DARK_THEME_STYLE)
        
        # Dimensions
        self.setFixedSize(380, 200)

        # Setup GUI Elements
        self._init_ui()
        
        # Connect to Assistant Signals
        self.assistant.status_changed.connect(self._on_assistant_status_changed)
        self.assistant.speech_status_changed.connect(self._on_speech_status_changed)
        self.assistant.response_ready.connect(self._on_response_ready)
        self.assistant.error_occurred.connect(self._on_error_occurred)

        # Center in screen
        self.center_on_screen()

    def _init_ui(self):
        # Outer container Frame (for glassmorphism border styling)
        main_frame = QFrame(self)
        main_frame.setObjectName("MainFrame")
        main_frame.setGeometry(0, 0, self.width(), self.height())
        
        # Overall vertical layout inside frame
        main_layout = QVBoxLayout(main_frame)
        main_layout.setContentsMargins(15, 10, 15, 12)
        main_layout.setSpacing(6)

        # 1. Custom Title Bar Layout
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("J.A.R.V.I.S.", self)
        title_label.setObjectName("TitleLabel")
        
        self.min_btn = QPushButton("—", self)
        self.min_btn.setObjectName("ControlBtn")
        self.min_btn.clicked.connect(self.showMinimized)
        
        self.close_btn = QPushButton("✕", self)
        self.close_btn.setObjectName("ControlBtn")
        self.close_btn.setProperty("class", "close")
        self.close_btn.setObjectName("ControlBtnClose")
        self.close_btn.clicked.connect(self.close)

        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.min_btn)
        title_layout.addWidget(self.close_btn)
        main_layout.addLayout(title_layout)

        # Separator line
        sep = QFrame(self)
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: rgba(0, 240, 255, 30); max-height: 1px; border: none;")
        main_layout.addWidget(sep)

        # 2. Main Status and Waveform Row
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(12)

        # Round microphone button
        self.mic_btn = QPushButton(self)
        self.mic_btn.setObjectName("MicButton")
        self.mic_btn.setToolTip("Toggle Voice Assistant")
        self.mic_btn.clicked.connect(self._on_mic_toggle_clicked)
        self.mic_btn.setProperty("listening", "false")
        
        # Labels and waveform container
        status_column = QVBoxLayout()
        status_column.setSpacing(2)
        
        self.status_title = QLabel("System Standby", self)
        self.status_title.setObjectName("StatusLabel")
        self.status_title.setStyleSheet("font-weight: bold; color: #cbd5e1;")
        
        self.status_subtitle = QLabel("Wake word active", self)
        self.status_subtitle.setObjectName("StatusLabel")
        self.status_subtitle.setStyleSheet("color: #64748b; font-size: 10px;")
        
        # Audio waveform
        self.waveform = WaveformWidget(self)
        self.waveform.setFixedHeight(35)

        status_column.addWidget(self.status_title)
        status_column.addWidget(self.status_subtitle)
        status_column.addWidget(self.waveform)

        middle_layout.addWidget(self.mic_btn)
        middle_layout.addLayout(status_column)
        middle_layout.setStretch(1, 1)
        main_layout.addLayout(middle_layout)

        # Output label showing what Jarvis responds
        self.response_label = QLabel("Awaiting command...", self)
        self.response_label.setObjectName("ResponseLabel")
        self.response_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.response_label.setWordWrap(True)
        self.response_label.setFixedHeight(34)
        main_layout.addWidget(self.response_label)

        # 3. Action Button Bar (Start / Stop listening)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.start_btn = QPushButton("Start Listening", self)
        self.start_btn.setObjectName("ActionButton")
        self.start_btn.clicked.connect(self._on_start_listening_clicked)

        self.stop_btn = QPushButton("Stop Listening", self)
        self.stop_btn.setObjectName("ActionButton")
        self.stop_btn.clicked.connect(self._on_stop_listening_clicked)

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

    # --- DRAG & DROP WINDOW EVENTS ---

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    # --- UI ACTIONS ---

    def center_on_screen(self):
        screen = self.screen().availableGeometry()
        # Bottom-right corner placement like standard widgets, or center
        # Let's center it, slightly shifted down
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) - 80
        self.move(x, y)

    def closeEvent(self, event):
        # Gracefully stop assistant thread before exiting
        self.assistant.stop()
        event.accept()

    # --- SLOTS FOR ASSISTANT EMITTED SIGNALS ---

    @pyqtSlot(str)
    def _on_assistant_status_changed(self, status_msg: str):
        # Displays general log statements
        self.response_label.setText(status_msg)

    @pyqtSlot(str)
    def _on_speech_status_changed(self, speech_state: str):
        # Update waveform state
        self.waveform.set_status(speech_state)
        
        # Update labels and mic button styling based on speech state
        if speech_state == "idle":
            self.status_title.setText("System Standby")
            self.status_subtitle.setText("Click microphone to wake")
            self.mic_btn.setProperty("listening", "false")
        elif speech_state == "listening_wake":
            self.status_title.setText("Hey Jarvis")
            self.status_subtitle.setText("Waiting for wake word...")
            self.mic_btn.setProperty("listening", "false")
        elif speech_state == "listening_command":
            self.status_title.setText("Jarvis Listening")
            self.status_subtitle.setText("Speak your command, Sir...")
            self.mic_btn.setProperty("listening", "true")
        elif speech_state == "listening_typing":
            self.status_title.setText("Dictation Active")
            self.status_subtitle.setText("Typing into focused window...")
            self.mic_btn.setProperty("listening", "true")
        elif speech_state == "processing":
            self.status_title.setText("Processing")
            self.status_subtitle.setText("Decoding command...")
        elif speech_state == "speaking":
            self.status_title.setText("Speaking")
            self.status_subtitle.setText("Responding...")
            
        # Refresh stylesheet to apply dynamic properties like listening="true"
        self.mic_btn.style().unpolish(self.mic_btn)
        self.mic_btn.style().polish(self.mic_btn)

    @pyqtSlot(str)
    def _on_response_ready(self, response_text: str):
        self.response_label.setText(response_text)

    @pyqtSlot(str)
    def _on_error_occurred(self, error_msg: str):
        self.status_title.setText("System Error")
        self.status_subtitle.setText(error_msg)
        self.response_label.setText(f"Error: {error_msg}")

    # --- BUTTON CLICK HANDLERS ---

    def _on_mic_toggle_clicked(self):
        """Microphone button click toggles active wake/command listening or standby."""
        current_state = self.waveform.status
        if current_state == "idle":
            self.assistant.listener.set_mode("wake")
            self.assistant.listener.resume_listening()
        else:
            self.assistant.listener.pause_listening()

    def _on_start_listening_clicked(self):
        """Resume continuous listening."""
        self.assistant.listener.resume_listening()

    def _on_stop_listening_clicked(self):
        """Pause continuous listening."""
        self.assistant.listener.pause_listening()
