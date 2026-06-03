# J.A.R.V.I.S. Desktop Assistant

JARVIS (Just A Rather Very Intelligent System) is a complete, production-ready Python-based desktop assistant. Built with PyQt6 and integrated with the Google Gemini API, it provides system app launching, PC hardware controls, reminders, alarms, email automation, file operations, news/weather reports, and continuous wake-word listening.

---

## Key Features

*   **Modern Floating UI**: Frameless, translucent dark glassmorphism widget that floats "always on top" with custom paint event audio waveform animations corresponding to Jarvis' active state.
*   **Voice Control & Continuous Listening**: Uses background thread listeners to continuously capture speech. Wake word **"Hey Jarvis"** automatically triggers voice input capture.
*   **AI Chat & Command Parsing**: Uses Gemini API to parse natural language commands into structured JSON calls and engages in contextual conversation.
*   **Offline/Keyless Fallback Mode**: If your internet is down or the Gemini API key is missing, Jarvis automatically activates local rule-based intent parsing and fallback speech responses so the assistant remains functional.
*   **Advanced PC Controls**: System volume up/down/mute, display brightness, screen captures, network adapter toggles (Wi-Fi, Bluetooth), locking PC, and power options (Sleep, Restart, Shutdown).
*   **File Manager System**: Hands-free file/folder creations, deletions, renames, search, copy/paste clipboard operations, recent documents viewer, and an automatic directory organizer sorting documents, media, and executables.
*   **Daily Scheduling Utilities**: Persistent alarm settings and text-to-speech reminder scheduling that survives application restarts.
*   **Email & Communication**: Send SMTP emails and fetch recent mailbox headings using IMAP, with interactive voice prompting for missing parameters (e.g. email body).
*   **Voice Typing (Dictation Mode)**: Dictates voice input directly as keyboard strokes into the active focused window.

---

## Directory Structure

```
jarvis/
├── requirements.txt            # System dependencies
├── README.md                   # Installation & usage document
├── .env.example                # Example configurations
└── jarvis/
    ├── __init__.py
    ├── main.py                 # Application startup script & global crash handler
    ├── config/
    │   ├── __init__.py
    │   └── settings.py         # Path configs, .env loader, and defaults
    ├── ui/
    │   ├── __init__.py
    │   ├── theme.py            # Glassmorphism styling and QSS specifications
    │   └── floating_panel.py   # Floating QWidget UI & custom Waveform painter
    ├── core/
    │   ├── __init__.py
    │   ├── assistant.py        # Central state machine orchestrator
    │   └── command_parser.py   # Intent extraction router
    ├── voice/
    │   ├── __init__.py
    │   ├── audio_listener.py   # Background continuous microphone listener
    │   └── tts_engine.py       # Background queue-based Speech synthesis
    ├── services/
    │   ├── __init__.py
    │   ├── gemini_service.py   # Gemini API connector & fallback rules
    │   ├── weather_service.py  # wttr.in weather client
    │   ├── news_service.py     # Google News XML/RSS crawler
    │   ├── email_service.py    # SMTP/IMAP wrappers & email simulator
    │   └── reminder_service.py # Alarm & reminder thread scheduler
    ├── automation/
    │   ├── __init__.py
    │   ├── system_apps.py      # App launching utilities (Registry + standard paths)
    │   ├── pc_control.py       # Volume, brightness, shell and power functions
    │   ├── file_manager.py     # File I/O operations & auto-organizer
    │   └── voice_typing.py     # Active window typing simulation
    └── utils/
        ├── __init__.py
        └── logger.py           # Logging system writing to console & jarvis.log
```

---

## Requirements & Prerequisites

1.  **Python 3.10+** (64-bit recommended for Windows compatibility).
2.  **PyAudio (Microphone Input)**:
    *   Installing PyAudio on Windows requires portaudio binaries. You can install it directly via pip (`pip install pyaudio`).
    *   If pip fails to compile PyAudio, install it using precompiled wheels:
        1. Download the PyAudio wheel matching your Python version from [Unofficial Windows Binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) or direct python wheels repository.
        2. Run: `pip install PyAudio-xxx.whl`.
3.  **Windows OS**: Specifically designed and optimized for Windows APIs (using `winshell`, `pywin32`, and PowerShell wrappers).

---

## Installation Steps

1.  Clone or navigate to the JARVIS root folder (`d:\lasttry`).
2.  Create a virtual environment:
    ```powershell
    python -m venv venv
    ```
3.  Activate the virtual environment:
    ```powershell
    venv\Scripts\activate
    ```
4.  Install requirements:
    ```powershell
    pip install -r requirements.txt
    ```
5.  Configure your environment:
    *   Duplicate `.env.example` and rename it to `.env`.
    *   Open `.env` and fill in your details:
        ```env
        GEMINI_API_KEY=AIzaSy...your_gemini_api_key_here
        SENDER_EMAIL=your_real_gmail_address@gmail.com
        SENDER_PASSWORD=your_gmail_app_password
        DEFAULT_CITY=London
        NEWS_COUNTRY=us
        ```

---

## How to Run

Execute the package main script inside your virtual environment:

```powershell
python -m jarvis.main
```

Upon startup, the panel will appear floating above your windows. You will hear: *"Jarvis is online and ready, Sir."*

---

## Core Voice Commands Reference

To activate JARVIS, say **"Hey Jarvis"**. Once you hear **"Yes Sir, I'm listening."**, speak one of the following commands:

### 1. System Applications
*   *Open Notepad* / *Launch Notepad*
*   *Open Calculator*
*   *Open Command Prompt* / *Open Cmd*
*   *Open File Explorer*
*   *Open Control Panel*
*   *Open Settings*
*   *Open Camera*
*   *Open Google Chrome* / *Launch Chrome*
*   *Open VS Code*

### 2. Hardware & PC Control
*   *Volume Up* / *Increase volume* (adjusts system volume +10%)
*   *Volume Down* / *Decrease volume* (adjusts system volume -10%)
*   *Mute Audio* / *Unmute Audio*
*   *Brightness Increase* / *Increase brightness* (+15%)
*   *Brightness Decrease* / *Decrease brightness* (-15%)
*   *Take Screenshot* (saves a full capture onto your Desktop as `Screenshot_TIMESTAMP.png`)
*   *Wi-Fi On* / *Wi-Fi Off*
*   *Bluetooth On* / *Bluetooth Off*
*   *Lock PC* / *Lock computer*
*   *Sleep Mode* / *Put PC to sleep*
*   *Restart PC* (warns and restarts PC in 10 seconds)
*   *Shutdown PC* (warns and shuts down PC in 10 seconds)

### 3. Advanced AI Capabilities
*   *What's the weather today?* / *What is the weather in Paris?*
*   *Tell me latest news* / *Give me headlines*
*   *Set Reminder* -> *"Remind me to call Rahul at 6 PM"* (relative times are parsed by Gemini)
*   *List Reminders* / *Delete Reminder matching 'call'*
*   *Set Alarm for 08:30* / *Stop Alarm* / *Delete Alarm for 08:30*
*   *Send email to john@example.com* -> Jarvis asks: *"What should I write?"* -> Dictate body -> Sends.
*   *Read email details* / *Check recent emails*
*   *Start voice typing* / *Start typing* (converts all spoken sentences directly to active cursor keystrokes. Say *"Stop voice typing"* to exit).
*   *General AI conversation*: Ask questions like *"Who are you?"*, *"Why is the sky blue?"*, or *"Help me write a Python function"*.

---

## Under the Hood (Developer Notes)

*   **Thread Safety**: The TTS Engine runs in its own thread managing queue processing. Background speech listening is executed inside a `QThread`. Communication between the UI, the speech engine, and the listener is completed through Qt's thread-safe Signal & Slot mechanisms.
*   **Windows COM Initialization**: Windows Speech APIs (`pyttsx3`) and shell links (`winshell`) use COM interface bindings. These require active initialization using `pythoncom.CoInitialize()` when launched in background worker threads. This has been fully configured inside `tts_engine.py`, `pc_control.py`, `file_manager.py`, and `reminder_service.py` to prevent thread crashes.
*   **State Machine Coordinator**: Located in `jarvis/core/assistant.py`. It guarantees that speech listeners are fully deactivated during active TTS audio playback, eliminating self-hearing loops.
