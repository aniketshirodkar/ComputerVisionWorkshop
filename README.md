# Hand Counter Workshop

A simple Python application that uses OpenCV and MediaPipe to track a single hand and count the number of fingers held up (0–5) in real-time.

## Features
- Real-time hand tracking using MediaPipe.
- Finger counting logic (Index, Middle, Ring, Pinky based on joint height; Thumb based on width).
- Visual feedback on the video frame (Count and Words).
- Terminal output of results.

## Prerequisites
- **Python 3.12** is recommended for best compatibility with MediaPipe on modern systems.
- A working webcam.

## Getting Started

### 1. Clone or Navigate to the Project
Open your terminal and enter the project directory:

### 2. Create a Virtual Environment
It is recommended to use a virtual environment to avoid library conflicts:
```bash
/usr/local/bin/python3.12 -m venv venv
```

### 3. Activate the Virtual Environment
- **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```
- **Windows:**
  ```cmd
  venv\Scripts\activate
  ```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
```bash
python hand_counter.py
```

## Troubleshooting: Camera Permissions (macOS)
If you encounter an error saying `Error: Could not open webcam`, macOS might be blocking camera access for your Terminal or IDE.
1. Open **System Settings**.
2. Go to **Privacy & Security** > **Camera**.
3. Ensure the toggle is **ON** for your Terminal (e.g., Terminal, iTerm2) or your Code Editor (e.g., VS Code).

## Usage & Controls
- **Fingers 0–5:** Hold up your hand in front of the camera to see the count.
- **Exit:** Press **'q'** or **ESC** while the video window is focused to close the application.
- **Deactivate Venv:** When finished, type `deactivate` in your terminal to exit the virtual environment.

## Project Structure
- `hand_counter.py`: The main Python script.
- `requirements.txt`: List of required Python libraries.
- `README.md`: This instruction file.
