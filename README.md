# J.A.R.V.I.S. Desktop Assistant

> **Just A Rather Very Intelligent System** — A production-ready Python voice assistant for Windows.

Say **"Hey Jarvis"** → wait for *"Yes Sir, I'm listening."* → speak your command.

---

## ✅ All Working Voice Commands

---

### 🗂️ File Operations

```
create a file named notes.txt
create a new file report.txt
create folder named Projects
create a new folder Work
open downloads folder
open folder Documents
open folders document
open file notes.txt
open report.pdf
open budget.xlsx
move notes.txt to Desktop
move report.pdf to Downloads
move budget.xlsx to Documents
rename notes.txt to backup.txt
rename folder Work to Office
delete file temp.txt
delete folder Old Backup
search files for budget
find files for report
list desktop
list downloads
list documents
show contents of documents
copy file notes.txt
paste to Desktop
paste to Downloads
show recent files
organize downloads
organize desktop
organize documents
```

---

### 🖥️ System Applications

```
open Notepad
open Calculator
open Command Prompt
open cmd
open File Explorer
open Control Panel
open Settings
open Camera
open Chrome
open Google Chrome
open VS Code
open Visual Studio Code
```

---

### ⚙️ PC Hardware Control

```
volume up
increase volume
volume down
decrease volume
mute
unmute
increase brightness
brighter
decrease brightness
dim
take screenshot
WiFi on
enable WiFi
turn on WiFi
WiFi off
disable WiFi
turn off WiFi
Bluetooth on
enable Bluetooth
turn on Bluetooth
Bluetooth off
disable Bluetooth
turn off Bluetooth
lock PC
lock computer
sleep
restart
reboot
shutdown
shut down
```

---

### 🌤️ Weather

```
weather in Pune
what is the weather in Mumbai
what's the weather today in Delhi
tell me the weather report of London
temperature in New York
weather forecast for Paris
how is the weather in Bangalore
tell me the weather of Chennai
```

---

### 📰 News

```
news
latest news
give me headlines
what's in the news
```

---

### ⏰ Alarms and Reminders

```
remind me to call Rahul at 6 PM
remind me to take medicine in 30 minutes
list reminders
show reminders
delete reminder call
set alarm for 08:30
set alarm for 7am
stop alarm
delete alarm for 08:30
```

---

### 📧 Email

```
send email to john@example.com
read emails
check emails
```

---

### ⌨️ Voice Typing

```
start voice typing
start typing
stop voice typing
stop dictation
```

---

### 💬 General AI Conversation

```
who are you
what can you do
hello
hi
hey
thank you
why is the sky blue
tell me a joke
help me write a Python function
what is artificial intelligence
```

---

## 📁 Folder Shortcuts

These words work as folder names in any file command:

```
desktop     →  C:\Users\<you>\Desktop
downloads   →  C:\Users\<you>\Downloads
documents   →  C:\Users\<you>\Documents
pictures    →  C:\Users\<you>\Pictures
videos      →  C:\Users\<you>\Videos
music       →  C:\Users\<you>\Music
```

---

## 📂 Organize Files — What Goes Where

When you say *"organize downloads"*, files are sorted into subfolders:

```
Images/       →  .jpg  .jpeg  .png  .gif  .bmp  .webp  .svg
Documents/    →  .pdf  .doc  .docx  .xls  .xlsx  .ppt  .pptx  .txt  .csv  .md
Audio/        →  .mp3  .wav  .aac  .flac  .ogg  .m4a
Video/        →  .mp4  .mkv  .avi  .mov  .wmv  .webm
Archives/     →  .zip  .rar  .7z  .tar  .gz
Executables/  →  .exe  .msi  .bat  .cmd  .ps1
Code/         →  .py  .js  .ts  .html  .css  .json  .xml  .java  .cpp
Others/       →  everything else
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
```

Edit `.env` and fill in your details:

```env
GEMINI_API_KEY=AIzaSy...your_key_here
SENDER_EMAIL=your_gmail@gmail.com
SENDER_PASSWORD=your_gmail_app_password
DEFAULT_CITY=Pune
NEWS_COUNTRY=in
WAKE_WORD=hey jarvis
```

---

## 🚀 How to Run

```powershell
python -m jarvis.main
```

---

## 🏗️ Project Structure

```
d:\lasttry\
├── .env
├── .env.example
├── requirements.txt
├── README.md
└── jarvis/
    ├── main.py
    ├── config/
    │   └── settings.py
    ├── ui/
    │   ├── theme.py
    │   └── floating_panel.py
    ├── core/
    │   ├── assistant.py
    │   └── command_parser.py
    ├── voice/
    │   ├── audio_listener.py
    │   ├── tts_engine.py
    │   └── speak_subprocess.py
    ├── services/
    │   ├── gemini_service.py
    │   ├── weather_service.py
    │   ├── news_service.py
    │   ├── email_service.py
    │   └── reminder_service.py
    ├── automation/
    │   ├── system_apps.py
    │   ├── pc_control.py
    │   ├── file_manager.py
    │   └── voice_typing.py
    └── utils/
        └── logger.py
```

---

## 💡 Tips

```
- All commands work offline without a Gemini API key
- Gemini API is only used for free-form chat conversation
- Check logs/jarvis.log if a command fails
- Smart file search covers Desktop, Downloads, Documents, Pictures, Videos, Music
- You don't need to know the full file path — just say the filename
```

---

## 🔧 Requirements

```
Windows 10 or 11 (64-bit)
Python 3.10 or higher
Microphone (for voice input)
Speaker or Headphones (for voice output)
Google Gemini API key — optional, works offline too
```
