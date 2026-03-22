import math

# Mapping from count to words
FINGER_WORDS = {
    0: "NONE",
    1: "ONE",
    2: "TWO",
    3: "THREE",
    4: "FOUR",
    5: "FIVE",
}


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
