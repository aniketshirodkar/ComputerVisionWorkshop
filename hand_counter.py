"""
Hand counter using MediaPipe Hand Landmarker (Tasks API).

Docs (Google AI Edge):
  https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python

Python setup (supported versions, pip):
  https://ai.google.dev/mediapipe/solutions/setup_python

Install:  python -m pip install -r requirements.txt
Run:      python hand_counter.py

First run downloads the bundled hand_landmarker.task model next to this script.
"""

import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

import hand_logic

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
)
MODEL_FILENAME = "hand_landmarker.task"

# OpenCV camera index: 0 = first device. Change to 1, 2, … if the wrong camera opens (e.g. OBS).
CAMERA_INDEX = 1


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

    print("Hand Counter Running... Press 'q' or 'ESC' to exit.")

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

        count = 0
        word = "NONE"

        if results.hand_landmarks:
            for hand_landmarks in results.hand_landmarks:
                _draw_hand_landmarks(
                    frame,
                    hand_landmarks,
                    HandLandmarksConnections.HAND_CONNECTIONS,
                )
                count = hand_logic.count_fingers(hand_landmarks)
                word = hand_logic.FINGER_WORDS.get(count, "NONE")
                print(f"Count: {count}, Word: {word}")

        cv2.putText(
            frame,
            f"Fingers: {count}",
            (10, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        cv2.putText(
            frame,
            f"Word: {word}",
            (10, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        cv2.imshow("Hand Counter", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    landmarker.close()


if __name__ == "__main__":
    main()
