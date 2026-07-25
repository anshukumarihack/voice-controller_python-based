# Offline Voice Command Desktop Assistant

> Desktop automation powered by **Vosk offline speech recognition** and **PyAutoGUI**.

---

## Overview

This repository implements an offline desktop voice assistant that listens for a wake word, performs speech recognition locally with Vosk, and executes commands across multiple categories.

Key features:
- Offline Vosk ASR for speech recognition
- Command dispatching via `CommandDispatcher`
- Optional tray UI via `python main.py --tray`
- Accuracy logging in `logs/accuracy_log.csv`
- Timing benchmark results in `benchmarks/results.csv`

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add a Vosk model

Place one of the supported model folders under `models/`.
The assistant prefers:
- `models/vosk-model-small-en-in`
- `models/vosk-model-small-en-us`

If neither preferred folder exists, it loads the first `vosk-model*` directory it finds.

Example:

```bash
mkdir models
# Download and extract a model into models/
# Example URL:
# https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.22.zip
```

### 3. Run the assistant

```bash
python main.py
```

Or launch with the tray UI:

```bash
python main.py --tray
```

### Easy launch script

Create a small script so anyone can start the assistant without typing the command every time.

Windows (`run_assistant.bat`):

```bat
@echo off
cd /d "%~dp0"
python main.py
pause
```

macOS / Linux (`run_assistant.sh`):

```bash
#!/usr/bin/env bash
cd "$(dirname "$0")"
python3 main.py
```

Make the shell script executable:

```bash
chmod +x run_assistant.sh
```

---

## Usage

The assistant uses a wake-word gate. Speak a wake word first, then speak your command.

Common wake words include:
- `hey assistant`
- `ok assistant`
- `assistant`
- `hey`
- `hello`

---

## Command Categories

### App Launcher
- `open chrome`
- `launch vs code`
- `start spotify`
- `open file manager`
- `open terminal`

### File Operations
- `create file report.txt`
- `delete file old.txt`
- `open folder downloads`
- `rename data.csv to backup.csv`

### Web Search
- `search for python tutorials`
- `youtube lo-fi music`
- `weather in Chennai`
- `wikipedia quantum computing`
- `directions to airport`

### System Control
- `volume up` / `volume down`
- `mute` / `unmute`
- `set volume 50`
- `brightness up`
- `lock screen`
- `shutdown`

### Media Control
- `play` / `pause`
- `next song` / `previous song`
- `fast forward`

### Window Management
- `minimize`
- `maximize`
- `close window`
- `new tab`
- `switch window`

### Clipboard
- `copy` / `paste` / `cut`
- `undo` / `redo`
- `read clipboard`

### Screenshot
- `take a screenshot`
- `capture screen`

### Typing
- `type hello world`
- `press enter`
- `press escape`

### Calendar / Time
- `what time is it`
- `what is today\'s date`
- `set timer 5 minutes`
- `open calendar`

### Calculator
- `what is 42 times 7`
- `calculate 100 divided by 4`
- `compute 15 plus 27`

---

## Performance

From `benchmarks/results.csv`:
- Total benchmark entries: **10**
- Average voice command execution time: **0.091 s**
- Average manual task time: **3.200 s**
- Average time reduction: **96.8%**
- Command success rate: **90%**

Accuracy logs are written to `logs/accuracy_log.csv` after every command attempt.

---

## Offline ASR

Speech recognition is handled locally with Vosk. No internet connection is required once the model files are downloaded.

---

## Model detection

`assistant.py` now auto-detects available Vosk models inside `models/` and prefers:
- `models/vosk-model-small-en-in`
- `models/vosk-model-small-en-us`

If neither preferred folder is available, it loads the first detected `vosk-model*` directory.

---

## Project structure

```text
voice_assistant/
├── assistant.py               # Core ASR + command dispatch loop
├── main.py                    # Entry point
├── commands/                  # Command category handlers
├── models/                    # Vosk model folders
├── requirements.txt
├── ui/                        # Tray UI implementation
├── utils/                     # Noise filtering and audio feedback
├── logs/                      # Accuracy log
└── benchmarks/                # Timing benchmark output
```

---

## Extending the assistant

1. Create a new command module in `commands/`.
2. Subclass `BaseCommand` and implement `execute(self, text)`.
3. Add the new command class to the handler list in `commands/dispatcher.py`.
