# Hand Counter Workshop

A small Python app that uses **OpenCV** and **MediaPipe Hand Landmarker** (Tasks API) to track one hand and count fingers (0–5) in real time.

## Official MediaPipe references

This project follows Google’s current **Hand Landmarker** flow (not the removed legacy `mediapipe.solutions` API):

- [Hand landmarks detection guide for Python](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python) — `HandLandmarker`, `RunningMode.VIDEO`, `detect_for_video`, `mp.Image`, model path
- [Hand Landmarker overview](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/index) — capabilities and bundled models
- [Setup guide for Python](https://ai.google.dev/mediapipe/solutions/setup_python) — supported Python and `pip` versions
- [Example notebook (Colab)](https://colab.research.google.com/github/googlesamples/mediapipe/blob/main/examples/hand_landmarker/python/hand_landmarker.ipynb)

## Features

- Real-time hand tracking via Hand Landmarker (Tasks API).
- Finger counting (thumb by horizontal compare; other fingers by tip vs. PIP height).
- On-screen count and word; optional terminal output.

## Prerequisites

- **Python 3.9–3.12** (range [supported by MediaPipe Tasks for Python](https://ai.google.dev/mediapipe/solutions/setup_python); use one of these for reliable installs).
- **pip 20.3+** (`python -m pip install --upgrade pip` if needed).
- A webcam.

## Install and run

From this directory:

```bash
python -m pip install -r requirements.txt
python hand_counter.py
```

The first run downloads Google’s **`hand_landmarker.task`** model (about 8 MB) into this folder next to `hand_counter.py`. If the automatic download fails (for example SSL on some macOS Python installs), install [`curl`](https://curl.se/) and run the script again; it retries with `curl`.

## Troubleshooting: Camera (macOS)

If you see `Error: Could not open webcam`:

1. **System Settings** → **Privacy & Security** → **Camera**
2. Enable the app that runs Python (Terminal, iTerm, VS Code, Cursor, etc.)

## Usage

- Show 0–5 fingers toward the camera to update the count.
- Press **q** or **Esc** while the video window is focused to quit.

## Project files

- `hand_counter.py` — webcam loop, Hand Landmarker, drawing.
- `hand_logic.py` — finger count from 21 landmarks.
- `requirements.txt` — `opencv-python`, `mediapipe`.
