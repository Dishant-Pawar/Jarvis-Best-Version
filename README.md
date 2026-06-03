# J.A.R.V.I.S. Desktop Assistant

> **Just A Rather Very Intelligent System** — A production-ready Python voice assistant for Windows, built with PyQt6 and Google Gemini AI.

---

## 🚀 Quick Start

```powershell
# 1. Activate virtual environment
venv\Scripts\activate

# 2. Run Jarvis
python -m jarvis.main
```

Say **"Hey Jarvis"** → wait for *"Yes Sir, I'm listening."* → speak your command.

---

## ✅ All Working Voice Commands

### 🗂️ 1. File Operations

Say **"Hey Jarvis"** then speak any of the following:

| What You Say | What Jarvis Does |
|---|---|
| `"create a file named notes.txt"` | Creates `notes.txt` on your Desktop |
| `"create a new file report.txt"` | Creates `report.txt` on your Desktop |
| `"create folder named Projects"` | Creates `Projects/` folder on your Desktop |
| `"create a new folder Work"` | Creates `Work/` folder on your Desktop |
| `"open downloads folder"` | Opens Downloads in File Explorer |
| `"open folder Documents"` | Opens Documents folder in File Explorer |
| `"open folders document"` | Opens Documents folder (voice variation) |
| `"open file notes.txt"` | Opens `notes.txt` with its default app |
| `"open report.pdf"` | Opens `report.pdf` directly (auto-detects extension) |
| `"move notes.txt to Desktop"` | Moves file to Desktop |
| `"move report.pdf to Downloads"` | Moves file to Downloads |
| `"move budget.xlsx to Documents"` | Moves file to Documents |
| `"rename notes.txt to backup.txt"` | Renames the file |
| `"rename folder Work to Office"` | Renames a folder |
| `"delete file temp.txt"` | Deletes the file (searches common folders) |
| `"delete folder Old Backup"` | Deletes the entire folder |
| `"search files for budget"` | Searches Desktop/Downloads/Documents/Pictures/Videos/Music |
| `"find files for report"` | Same as search |
| `"list desktop"` | Lists all items on Desktop by voice |
| `"list downloads"` | Lists all items in Downloads |
| `"show contents of documents"` | Lists all items in Documents |
| `"copy file notes.txt"` | Copies file to internal clipboard |
| `"paste to Desktop"` | Pastes clipboard file to Desktop |
| `"paste to Downloads"` | Pastes clipboard file to Downloads |
| `"show recent files"` | Reads out your 3 most recently modified files |
| `"organize downloads"` | Auto-sorts Downloads into Images/Documents/Audio/Video/Archives/Code |
| `"organize desktop"` | Auto-sorts Desktop by file type |

> **Smart Search**: Jarvis automatically looks for files across Desktop, Downloads, Documents, Pictures, Videos, and Music — you don't need to know the full path.

---

### 🖥️ 2. System Applications

| What You Say | What Jarvis Does |
|---|---|
| `"open Notepad"` | Opens Notepad |
| `"open Calculator"` | Opens Calculator |
| `"open Command Prompt"` / `"open cmd"` | Opens Command Prompt |
| `"open File Explorer"` | Opens File Explorer |
| `"open Control Panel"` | Opens Control Panel |
| `"open Settings"` | Opens Windows Settings |
| `"open Camera"` | Opens Camera app |
| `"open Chrome"` / `"open Google Chrome"` | Opens Google Chrome |
| `"open VS Code"` / `"open Visual Studio Code"` | Opens VS Code |

---

### ⚙️ 3. PC Hardware Control

| What You Say | What Jarvis Does |
|---|---|
| `"volume up"` / `"increase volume"` | Increases system volume by 10% |
| `"volume down"` / `"decrease volume"` | Decreases system volume by 10% |
| `"mute"` | Mutes audio |
| `"unmute"` | Unmutes audio |
| `"increase brightness"` / `"brighter"` | Increases display brightness by 15% |
| `"decrease brightness"` / `"dim"` | Decreases display brightness by 15% |
| `"take screenshot"` / `"take screen shot"` | Saves screenshot to Desktop as `Screenshot_TIMESTAMP.png` |
| `"WiFi on"` / `"enable WiFi"` / `"turn on WiFi"` | Enables Wi-Fi adapter |
| `"WiFi off"` / `"disable WiFi"` / `"turn off WiFi"` | Disables Wi-Fi adapter |
| `"Bluetooth on"` / `"enable Bluetooth"` | Enables Bluetooth |
| `"Bluetooth off"` / `"disable Bluetooth"` | Disables Bluetooth |
| `"lock PC"` / `"lock computer"` | Locks the workstation |
| `"sleep"` | Puts PC to sleep |
| `"restart"` / `"reboot"` | Restarts PC |
| `"shutdown"` / `"shut down"` | Shuts down PC |

---

### 🌤️ 4. Weather

| What You Say | What Jarvis Does |
|---|---|
| `"weather in Pune"` | Reads weather report for Pune |
| `"what is the weather in Mumbai"` | Reads weather for Mumbai |
| `"what's the weather today in Delhi"` | Reads current weather |
| `"tell me the weather report of London"` | Reads full weather report |
| `"temperature in New York"` | Reads temperature for New York |
| `"weather forecast for Paris"` | Reads weather forecast |

---

### 📰 5. News

| What You Say | What Jarvis Does |
|---|---|
| `"news"` | Reads latest top news headlines |
| `"latest news"` | Reads top headlines |
| `"give me headlines"` | Reads news |
| `"what's in the news"` | Reads news |

---

### ⏰ 6. Alarms & Reminders

| What You Say | What Jarvis Does |
|---|---|
| `"remind me to call Rahul at 6 PM"` | Sets reminder for 6:00 PM today |
| `"remind me to take medicine in 30 minutes"` | Sets reminder 30 min from now |
| `"list reminders"` / `"show reminders"` | Reads all active reminders |
| `"delete reminder call"` | Deletes reminder matching keyword |
| `"set alarm for 08:30"` | Sets alarm at 08:30 |
| `"set alarm for 7am"` | Sets alarm at 07:00 |
| `"stop alarm"` | Stops the currently ringing alarm |
| `"delete alarm for 08:30"` | Removes a scheduled alarm |

---

### 📧 7. Email

| What You Say | What Jarvis Does |
|---|---|
| `"send email to john@example.com"` | Starts email flow → Jarvis asks for message body |
| `"read emails"` / `"check emails"` | Reads recent email subjects from inbox |

> **How email sending works:**
> 1. Say `"send email to john@example.com"`
> 2. Jarvis asks: *"What should I write?"*
> 3. Dictate your message
> 4. Jarvis sends the email automatically

---

### ⌨️ 8. Voice Typing (Dictation Mode)

| What You Say | What Jarvis Does |
|---|---|
| `"start voice typing"` / `"start typing"` | Enters dictation mode — everything you say is typed into the active window |
| `"stop voice typing"` / `"stop dictation"` | Exits dictation mode |

> Click on any text field (Notepad, browser, etc.) first, then activate voice typing.

---

### 💬 9. General AI Conversation

Say anything not matching the above commands and Jarvis will answer using Gemini AI:

- *"Who are you?"*
- *"What can you do?"*
- *"Why is the sky blue?"*
- *"Help me write a Python function"*
- *"Tell me a joke"*
- *"Hello"* / *"Hi"* / *"Thank you"*

---

## 📁 Folder Aliases (use in any file command)

These words are understood as folder shortcuts:

| You Say | Maps To |
|---|---|
| `desktop` | `C:\Users\<you>\Desktop` |
| `downloads` | `C:\Users\<you>\Downloads` |
| `documents` | `C:\Users\<you>\Documents` |
| `pictures` | `C:\Users\<you>\Pictures` |
| `videos` | `C:\Users\<you>\Videos` |
| `music` | `C:\Users\<you>\Music` |

---

## 📂 Organize Files — Category Map

When you say *"organize downloads"*, files are sorted into:

| Subfolder | File Types |
|---|---|
| `Images/` | `.jpg` `.jpeg` `.png` `.gif` `.bmp` `.webp` `.svg` |
| `Documents/` | `.pdf` `.doc` `.docx` `.xls` `.xlsx` `.ppt` `.pptx` `.txt` `.csv` `.md` |
| `Audio/` | `.mp3` `.wav` `.aac` `.flac` `.ogg` `.m4a` |
| `Video/` | `.mp4` `.mkv` `.avi` `.mov` `.wmv` `.webm` |
| `Archives/` | `.zip` `.rar` `.7z` `.tar` `.gz` |
| `Executables/` | `.exe` `.msi` `.bat` `.cmd` `.ps1` |
| `Code/` | `.py` `.js` `.ts` `.html` `.css` `.json` `.xml` `.java` `.cpp` |
| `Others/` | Everything else |

---

## 🏗️ Project Structure

```
d:\lasttry\
├── .env                        # Your API keys and settings
├── .env.example                # Template for .env
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── jarvis/
    ├── main.py                 # App startup & crash handler
    ├── config/
    │   └── settings.py         # Path configs, .env loader
    ├── ui/
    │   ├── theme.py            # Glassmorphism styles
    │   └── floating_panel.py   # Floating UI & waveform painter
    ├── core/
    │   ├── assistant.py        # Central state machine
    │   └── command_parser.py   # Intent routing
    ├── voice/
    │   ├── audio_listener.py   # Background microphone listener
    │   ├── tts_engine.py       # Text-to-speech engine (subprocess isolated)
    │   └── speak_subprocess.py # Isolated pyttsx3 speech process
    ├── services/
    │   ├── gemini_service.py   # Local-first intent parser + Gemini AI
    │   ├── weather_service.py  # wttr.in weather client
    │   ├── news_service.py     # Google News RSS crawler
    │   ├── email_service.py    # SMTP/IMAP wrappers
    │   └── reminder_service.py # Alarm & reminder scheduler
    ├── automation/
    │   ├── system_apps.py      # App launching utilities
    │   ├── pc_control.py       # Volume, brightness, power control
    │   ├── file_manager.py     # Full file/folder management
    │   └── voice_typing.py     # Keyboard stroke simulation
    └── utils/
        └── logger.py           # Logging to console & logs/jarvis.log
```

---

## ⚙️ Installation

```powershell
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
venv\Scripts\activate

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Copy and configure environment
copy .env.example .env
# Edit .env and fill in your keys
```

### `.env` Configuration

```env
GEMINI_API_KEY=AIzaSy...your_key_here
SENDER_EMAIL=your_gmail@gmail.com
SENDER_PASSWORD=your_gmail_app_password
DEFAULT_CITY=Pune
NEWS_COUNTRY=in
WAKE_WORD=hey jarvis
```

---

## 🔧 Requirements

- **Windows 10/11** (64-bit)
- **Python 3.10+**
- **Microphone** (for voice input)
- **Speaker/Headphones** (for voice output)
- **Google Gemini API key** (free at [aistudio.google.com](https://aistudio.google.com)) — *optional, works offline too*

---

## 💡 Tips

- **Offline mode**: All file, PC control, app, and weather commands work **without** a Gemini API key using the built-in local parser.
- **Gemini API** is only used for free-form conversation and natural-language time parsing (e.g. *"remind me in 5 minutes"*).
- **Log file**: Check `logs/jarvis.log` if a command fails — it shows exactly what Jarvis heard and why it failed.
- **Wake word variations**: Saying *"hey jar"* or similar will also trigger Jarvis if close enough to the wake word.

---

## 📝 Developer Notes

- **TTS isolation**: `pyttsx3` runs in a separate subprocess (`speak_subprocess.py`) to avoid COM/Qt thread conflicts on Windows.
- **Local-first parsing**: The intent parser runs rule-based matching first (instant, no API). Gemini is only called for chat and time-relative reminders.
- **Thread safety**: All UI↔backend communication uses Qt signals/slots across threads.
- **Log location**: `d:\lasttry\logs\jarvis.log`
