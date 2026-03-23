# Hand tracking workshop

A small Python project using **OpenCV** and **MediaPipe Hand Landmarker** (Tasks API). **Starter:** a single file, `hand_tracker.py` — live webcam wireframe plus thumb helpers for later counting. **Code-along:** add finger counting and word mapping in the same file. Instructors use `workshop_instructor_reference.py` (keep private; do not share with participants if you use it as a cheat sheet).

## Official MediaPipe references

This project follows Google’s current **Hand Landmarker** flow (not the removed legacy `mediapipe.solutions` API):

- [Hand landmarks detection guide for Python](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python) — `HandLandmarker`, `RunningMode.VIDEO`, `detect_for_video`, `mp.Image`, model path
- [Hand Landmarker overview](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/index) — capabilities and bundled models
- [Setup guide for Python](https://ai.google.dev/mediapipe/solutions/setup_python) — supported Python and `pip` versions
- [Example notebook (Colab)](https://colab.research.google.com/github/googlesamples/mediapipe/blob/main/examples/hand_landmarker/python/hand_landmarker.ipynb)

## Features

- Real-time hand tracking via Hand Landmarker (Tasks API).
- Starter: wireframe overlay only.
- After the code-along: finger counting (thumb uses robust checks in `hand_tracker.py`; other fingers by tip vs. PIP height) and customizable words/sign-style mappings.

## Prerequisites

- **Python 3.9–3.12** (range [supported by MediaPipe Tasks for Python](https://ai.google.dev/mediapipe/solutions/setup_python); newer Python often works too if `pip` can install `mediapipe`).
- **pip 20.3+** (see below).
- A webcam.

---

## 1. Python

**Python** is the language runtime. You need a recent **Python 3** installed.

### Check if Python is already installed

Open a terminal (macOS/Linux) or Command Prompt / PowerShell (Windows) and run:

```bash
python3 --version
```

On some Windows setups the command is `python` instead of `python3`:

```bash
python --version
```

You should see something like `Python 3.9.x` or higher. **Use the same command** (`python3` or `python`) for every step below.

### Install or upgrade Python

If the command is missing or the version is **below 3.9**:

| Platform | What to do |
|----------|------------|
| **Any OS** | Download an installer from [python.org/downloads](https://www.python.org/downloads/). On Windows, check **“Add python.exe to PATH”** (or similar) during setup. |
| **macOS** (Homebrew) | `brew install python@3.12` (or another 3.9+ formula), then use the path Homebrew prints, or ensure `python3` is on your `PATH`. |
| **Linux** (Debian/Ubuntu) | `sudo apt update && sudo apt install python3 python3-pip python3-venv` |

After installing, open a **new** terminal and run the version check again.

---

## 2. pip

**pip** is Python’s package installer. It is included with most Python 3 installs.

### Check pip

```bash
python3 -m pip --version
```

On Windows, if you use `python` for Python:

```bash
python -m pip --version
```

You should see a pip version and a path that matches your Python. If this fails, reinstall Python from [python.org](https://www.python.org/downloads/) and enable pip in the installer.

### Upgrade pip (recommended)

```bash
python3 -m pip install --upgrade pip
```

(Use `python` instead of `python3` on Windows if that matches how you run Python.)

---

## 3. Install this project and run

In a terminal, go to the folder that contains `hand_tracker.py` and `requirements.txt`:

```bash
cd path/to/ComputerVisionWorkshop
```

Install the libraries listed in `requirements.txt`:

```bash
python3 -m pip install -r requirements.txt
```

Start the starter app:

```bash
python3 hand_tracker.py
```

Again, use `python` instead of `python3` everywhere if that is what works on your machine.

### If `pip install` is blocked (common on macOS/Linux system Pythons)

Your OS may forbid installing into the system Python. Pick one:

- **Per-user install:**  
  `python3 -m pip install --user -r requirements.txt`

- **Project virtual environment** (recommended for isolation):  
  `python3 -m venv .venv`  
  `source .venv/bin/activate`  
  `python -m pip install -r requirements.txt`  
  `python hand_tracker.py`  

On Windows activation: `.venv\Scripts\activate`

The first run downloads Google’s **`hand_landmarker.task`** model (about 8 MB) next to `hand_tracker.py`. If the automatic download fails (for example SSL on some macOS Python installs), install [`curl`](https://curl.se/) and run the script again; it retries with `curl`.

---

## Troubleshooting: Camera (macOS)

If you see `Error: Could not open webcam`:

1. **System Settings** → **Privacy & Security** → **Camera**
2. Enable the app that runs Python (Terminal, iTerm, VS Code, Cursor, etc.)

## Usage

- **Starter:** run `hand_tracker.py` and show your hand; you should see the skeleton overlay.
- **After the code-along:** show 0–5 fingers (or your custom poses) to update count/words.
- Press **q** or **Esc** while the video window is focused to quit.

## Project files

- `hand_tracker.py` — participant starter: webcam loop, Hand Landmarker, wireframe drawing, and thumb helpers; counting and words are added during the workshop.
- `workshop_instructor_reference.py` — instructor-only copy-paste / teaching notes (optional; omit from participant bundles if you prefer).
- `requirements.txt` — `opencv-python`, `mediapipe`.
