# Deep dive: how `hand_tracker.py` works

This page is **optional reading**. In the workshop we only have time for a quick tour; if you want a **deeper, high-level** explanation of the functions and how the pieces fit together, use this as a reference while you read the code.

It skips basic Python syntax (imports, simple loops) and focuses on **geometry**, **MediaPipe landmarks**, and **why** the thumb is handled differently from the other fingers.

---

## Pipeline in one sentence

**MediaPipe** outputs **21 normalized 2D landmarks** per hand on each video frame. Our code **interprets** those numbers to estimate how many fingers are “up,” maps that integer to a **word** (via a dictionary), and **draws** the skeleton plus on-screen text on the webcam image.

---

## Landmark indices (MediaPipe hand)

Each landmark has `.x` and `.y` in **normalized** coordinates from **0 to 1** (relative to image width and height). In this app, **smaller `y` means higher on the screen**—so “finger up” often means the tip has a **smaller `y`** than the joint below it (for the four fingers).

| Index | Role (short) |
|------|----------------|
| 0 | Wrist |
| 2, 3, 4 | Thumb: MCP, IP, tip |
| 5–8 | Index finger chain (MCP … tip) |
| 9–12 | Middle |
| 13–16 | Ring |
| 17–20 | Pinky |

**Thumb logic** uses landmarks **2, 3, 4** and the line from **wrist (0)** to **index tip (8)**.  
**The other four fingers** compare **tip** vs **PIP** indices: (8 vs 6), (12 vs 10), (16 vs 14), (20 vs 18).

---

## Geometry helpers (why the thumb is special)

### `_angle_deg_at_b(ax, ay, bx, by, cx, cy)`

**What it computes:** The angle at point **B** between the segments **A→B** and **C→B**, in **degrees**.

**How:** Form vectors `v1 = A − B` and `v2 = C − B`, take their lengths `n1`, `n2`. If either length is essentially zero, return `0.0` to avoid dividing by zero. Otherwise use the dot product: the cosine of the angle is `(v1·v2)/(n1*n2)`, clamp that cosine to **[-1, 1]** (floating-point error can otherwise break `acos`), then `acos` → radians → degrees.

**Why we care:** We use this at the **thumb IP joint** (landmarks 2–3–4) to measure how “open” the thumb is when deciding if it counts as extended.

---

### `_side_of_line(ax, ay, bx, by, px, py)`

**What it computes:** A **scalar** related to the 2D cross product \((B - A) \times (P - A)\). The **sign** tells which **side** of the directed line **A→B** the point **P** lies on.

**Why we care:** The thumb moves **sideways** as well as up/down. Comparing only “tip above knuckle” is unreliable. We ask whether the **thumb tip** and **thumb MCP** lie on the **same side** of the line from **wrist to index tip**—if the tip crosses to the “palm” side, we treat the thumb as **tucked**, not extended.

---

### `THUMB_IP_MIN_DEG`

A **constant** (degrees). After the palm-side check, the IP angle must be **greater than** this value for the thumb to count as extended. If your build feels too strict or too loose, this is the main number to experiment with.

---

### `_thumb_extended(landmarks)`

**Inputs:** `landmarks` — list of 21 landmarks (each has `.x`, `.y`).

**Steps (conceptually):**

1. **`ang_ip`** — Angle at landmark **3** with neighbors **2** and **4** (thumb MCP–IP–tip). A folded thumb keeps this angle small.
2. **`s2`, `s4`** — Side-of-line test for landmark **2** and **4** vs line **0 → 8** (wrist to index tip). If those signs differ enough and indicate **opposite sides** of the line (`s4 * s2 < 0`), the thumb tip has crossed toward the palm → return **not** extended.
3. **`eps`** — Tiny threshold so we do not jitter when points are almost on the line.
4. **Final check:** If the palm logic did not veto, thumb is extended if `ang_ip > THUMB_IP_MIN_DEG`.

**Takeaway:** The thumb uses **geometry** tuned for **mirrored webcam** and **both hands**; the other fingers use a simpler rule (below).

---

## Vocabulary and counting

### `FINGER_WORDS`

A Python **dictionary**: keys are **finger counts** (here **0–5**), values are **strings** shown on screen (words, phrases, or labels you choose for your workshop). You can change the strings; keep keys aligned with what `count_fingers` returns.

In the main loop, **`FINGER_WORDS.get(count, "NONE")`** returns the word for `count`, or **`"NONE"`** if the key is missing—so the UI always has a sensible fallback.

---

### `count_fingers(landmarks)`

**Goal:** Return an integer **0–5** = number of fingers considered “up.”

**Thumb:** `1` if `_thumb_extended(landmarks)` else `0` — uses the special logic above.

**Index, middle, ring, pinky:** For each finger, compare **tip** `y` to **PIP** `y`. If **`landmarks[tip].y < landmarks[pip].y`**, the tip is **higher on the screen** than the joint → treat as extended (`1`), else `0`.

**Return:** Sum of those six bits → **0–5**.

**Takeaway:** Four fingers share one simple **image-space** rule; the **thumb** needs the extra helpers because it does not move like the others.

---

## Drawing and program setup (brief)

### `_draw_hand_landmarks`

Converts normalized `(x, y)` to pixel coordinates, draws the **hand connection** lines, then the **points**. This is how you get the **wireframe** overlay.

### `_ensure_model`

Downloads the **`.task`** model file the first time you run the app (if it is not already next to the script).

### `main()` — MediaPipe and video

- **`HandLandmarker`** in **VIDEO** mode: **`detect_for_video`** expects a **monotonic** timestamp in milliseconds—we use elapsed time since capture started.
- **`cv2.flip(frame, 1)`** mirrors the image horizontally so it feels like a **selfie** view.

---

## Main loop (after you add counting and the HUD)

Typical structure:

```text
        count = 0
        word = "NONE"

        if results.hand_landmarks:
            for hand_landmarks in results.hand_landmarks:
                _draw_hand_landmarks(...)
                count = count_fingers(hand_landmarks)
                word = FINGER_WORDS.get(count, "NONE")

        cv2.putText(... "Fingers: {count}" ...)
        cv2.putText(... "Word: {word}" ...)
        cv2.imshow("Hand Tracker", frame)
```

| Piece | Role |
|--------|------|
| `count = 0`, `word = "NONE"` | **Defaults** when no hand is detected, so the overlay does not show stale values from the last frame. |
| `if results.hand_landmarks` | Only process when the model sees at least one hand. |
| `for hand_landmarks in ...` | The API can return multiple hands; with `num_hands=1` you usually see one. |
| `_draw_hand_landmarks` | Draw the skeleton **before** overlay text so everything is visible. |
| `count_fingers` / `FINGER_WORDS.get` | Compute count and look up the string. |
| `cv2.putText` | Draw **green** labels at fixed positions on the frame. |
| `cv2.imshow` | Show the final image—call this **after** drawing text on `frame`. |

**Optional:** A `print` inside the loop can log count and word to the **terminal** for debugging; it can print very often (every frame).

---

## Suggested reading order in the source file

1. Constants and **`main()`** — how the camera and landmarker run.  
2. **`_draw_hand_landmarks`** — how normalized points become pixels.  
3. **`_angle_deg_at_b`**, **`_side_of_line`**, **`_thumb_extended`** — thumb geometry.  
4. **`FINGER_WORDS`** and **`count_fingers`** — from landmarks to a count and a label.  
5. The **`while`** loop — tie detection, drawing, counting, and HUD together.

---

## Related files

- **`README.md`** — setup, run instructions, camera troubleshooting.  
- **`hand_tracker.py`** — the code this document describes (starter plus whatever you add in the workshop).
