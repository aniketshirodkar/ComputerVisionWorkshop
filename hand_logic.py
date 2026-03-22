# Mapping from count to words
FINGER_WORDS = {
    0: "NONE",
    1: "ONE",
    2: "TWO",
    3: "THREE",
    4: "FOUR",
    5: "FIVE",
}


def count_fingers(landmarks):
    """
    Counts how many fingers are up based on hand landmarks.

    Args:
        landmarks: Sequence of 21 MediaPipe normalized landmarks (index 0–20),
            each with .x and .y (Tasks API: list of NormalizedLandmark).
    """
    fingers = []

    # Thumb logic: compare x-coordinates (assuming right hand in selfie view)
    # Landmark 4: Thumb Tip, Landmark 3: Thumb IP
    if landmarks[4].x < landmarks[3].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # 4 Fingers logic: compare y-coordinates (tip < pip means finger is up)
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
