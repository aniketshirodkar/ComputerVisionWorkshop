"""
How to install dependencies:
pip install opencv-python mediapipe

How to run:
python hand_counter.py
"""

import cv2  # For video capture and image processing
import mediapipe as mp  # For hand landmark detection

# Mapping from count to words
FINGER_WORDS = {
    0: "NONE",
    1: "ONE",
    2: "TWO",
    3: "THREE",
    4: "FOUR",
    5: "FIVE",
}

def count_fingers(hand_landmarks):
    """
    Counts how many fingers are up based on hand landmarks.
    Logic: For most fingers, check if tip is above the PIP joint.
    For the thumb, check if tip is to the side of the IP joint.
    """
    fingers = []
    
    # MediaPipe landmarks for finger tips and joints
    # Thumb: 4 (Tip), 3 (IP)
    # Index: 8 (Tip), 6 (PIP)
    # Middle: 12 (Tip), 10 (PIP)
    # Ring: 16 (Tip), 14 (PIP)
    # Pinky: 20 (Tip), 18 (PIP)
    
    # Thumb logic: compare x-coordinates (assuming right hand in selfie view)
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # 4 Fingers logic: compare y-coordinates (tip < pip means finger is up)
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    
    for tip, pip in zip(tips, pips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return sum(fingers)

def main():
    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )

    # Open Webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Hand Counter Running... Press 'q' or 'ESC' to exit.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Flip image for selfie view
        frame = cv2.flip(frame, 1)
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        count = 0
        word = "NONE"

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks on the frame
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Count fingers
                count = count_fingers(hand_landmarks)
                word = FINGER_WORDS.get(count, "NONE")
                
                # Print to terminal
                print(f"Count: {count}, Word: {word}")

        # Display info on video frame
        cv2.putText(frame, f"Fingers: {count}", (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Word: {word}", (10, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Show the video
        cv2.imshow("Hand Counter", frame)

        # Exit on 'q' or ESC
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    hands.close()

if __name__ == "__main__":
    main()
