"""
Workshop starter: live webcam hand tracking with a simple wireframe overlay.

Includes **thumb handling** helpers (IP angle + wrist→index line) so finger counting
behaves well for both hands when you add it in the code-along.

Uses MediaPipe Hand Landmarker (Tasks API).

Docs (Google AI Edge):
  https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python

Python setup:
  https://ai.google.dev/mediapipe/solutions/setup_python

Install:  python -m pip install -r requirements.txt
Run:      python hand_tracker.py

First run downloads ``hand_landmarker.task`` next to this script.
"""

import math
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
)
MODEL_FILENAME = "hand_landmarker.task"

# OpenCV camera index: 0 = first device. Change to 1, 2, … if the wrong camera opens.
CAMERA_INDEX = 1


def _angle_deg_at_b(ax, ay, bx, by, cx, cy):
    """Angle ABC at vertex B (degrees), range [0, 180]."""
    v1x, v1y = ax - bx, ay - by
    v2x, v2y = cx - bx, cy - by
    n1 = math.hypot(v1x, v1y)
    n2 = math.hypot(v2x, v2y)
    if n1 < 1e-9 or n2 < 1e-9:
        return 0.0
    dot = max(-1.0, min(1.0, (v1x * v2x + v1y * v2y) / (n1 * n2)))
    return math.degrees(math.acos(dot))


def _side_of_line(ax, ay, bx, by, px, py):
    """Signed distance to line A→B (2D cross product); sign = which side of the line P is on."""
    return (bx - ax) * (py - ay) - (by - ay) * (px - ax)


# Min angle (degrees) at thumb IP joint (2–3–4) when thumb is not tucked by the palm line check.
THUMB_IP_MIN_DEG = 118.0


def _thumb_extended(landmarks):
    """
    Thumb counts as "up" only if:
    1) The IP joint angle (2–3–4) is open enough, and
    2) The thumb tip (4) has not crossed to the palm side of the line wrist (0) → index
       tip (8) (index chain …5–6–7–8).

    Palm tuck uses thumb MCP (2), not middle MCP (9): comparing tip (4) to (9) is not
    symmetric for left vs right hand in image space. Points (2) and (4) are both on the
    thumb; extended thumb keeps (4) on the same side of line 0→8 as (2); tucked into the
    palm moves (4) to the opposite side from (2). That holds for both hands.
    """
    lm = landmarks
    ang_ip = _angle_deg_at_b(
        lm[2].x, lm[2].y, lm[3].x, lm[3].y, lm[4].x, lm[4].y
    )

    # Line wrist (0) → index tip (8).
    s2 = _side_of_line(lm[0].x, lm[0].y, lm[8].x, lm[8].y, lm[2].x, lm[2].y)
    s4 = _side_of_line(lm[0].x, lm[0].y, lm[8].x, lm[8].y, lm[4].x, lm[4].y)

    eps = 5e-5
    if abs(s4) >= eps and abs(s2) >= eps:
        # Opposite sides of line 0→8 from thumb MCP ⇒ tip crossed into palm (tucked).
        if (s4 * s2) < 0:
            return False

    return ang_ip > THUMB_IP_MIN_DEG

FINGER_WORDS = {
    0: "HELLO",
    1: "WORLD",
    2: "FROM",
    3: "AGGIE",
    4: "CODING",
    5: "CLUB",
}


def count_fingers(landmarks):
    """
    Counts how many fingers are up based on hand landmarks.

    Args:
        landmarks: Sequence of 21 MediaPipe normalized landmarks (index 0–20),
            each with .x and .y (Tasks API: list of NormalizedLandmark).
    """
    fingers = []

    fingers.append(1 if _thumb_extended(landmarks) else 0)

    # Other fingers: tip above PIP on screen (smaller y) means extended
    # Tips: 8 (Index), 12 (Middle), 16 (Ring), 20 (Pinky)
    # PIPs: 6 (Index), 10 (Middle), 14 (Ring), 18 (Pinky)
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]

    for tip, pip in zip(tips, pips):
        if landmarks[tip].y < landmarks[pip].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return sum(fingers)

def _draw_hand_landmarks(
    bgr_image: np.ndarray,
    landmarks: list,
    connections: list,
    *,
    line_color: tuple[int, int, int] = (0, 255, 0),
    point_color: tuple[int, int, int] = (0, 0, 255),
    line_thickness: int = 2,
    point_radius: int = 3,
) -> None:
    """Draw normalized hand landmarks on a BGR frame (OpenCV).

    Recent mediapipe wheels omit ``tasks.python.vision.drawing_utils``; this
    replaces ``draw_landmarks`` for the workshop.
    """
    h, w = bgr_image.shape[:2]

    def _px(lm) -> tuple[int, int]:
        return int(lm.x * w), int(lm.y * h)

    for conn in connections:
        a = _px(landmarks[conn.start])
        b = _px(landmarks[conn.end])
        cv2.line(bgr_image, a, b, line_color, line_thickness)

    for lm in landmarks:
        cv2.circle(bgr_image, _px(lm), point_radius, point_color, -1)


def _ensure_model(model_path: Path) -> Path:
    if model_path.is_file():
        return model_path
    print(f"Downloading hand landmarker model to {model_path} ...")
    try:
        urllib.request.urlretrieve(MODEL_URL, model_path)
    except urllib.error.URLError:
        subprocess.run(
            ["curl", "-fsSL", "-o", str(model_path), MODEL_URL],
            check=True,
        )
    return model_path


def main():
    script_dir = Path(__file__).resolve().parent
    model_path = _ensure_model(script_dir / MODEL_FILENAME)

    BaseOptions = mp.tasks.BaseOptions
    HandLandmarker = mp.tasks.vision.HandLandmarker
    HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
    RunningMode = mp.tasks.vision.RunningMode
    HandLandmarksConnections = mp.tasks.vision.HandLandmarksConnections

    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(model_path)),
        running_mode=RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.7,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    landmarker = HandLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"Error: Could not open camera index {CAMERA_INDEX}.")
        return

    print("Hand tracker running. Press 'q' or 'ESC' to exit.")

    start_s = time.time()

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame = np.ascontiguousarray(rgb_frame)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        timestamp_ms = int((time.time() - start_s) * 1000)
        results = landmarker.detect_for_video(mp_image, timestamp_ms)

        if results.hand_landmarks:
            for hand_landmarks in results.hand_landmarks:
                _draw_hand_landmarks(
                    frame,
                    hand_landmarks,
                    HandLandmarksConnections.HAND_CONNECTIONS,
                )

        cv2.imshow("Hand Tracker", frame)
        

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    landmarker.close()


if __name__ == "__main__":
    main()
