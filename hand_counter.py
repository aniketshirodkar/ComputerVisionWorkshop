"""
How to install dependencies:
pip install opencv-python mediapipe

How to run:
python hand_counter.py
"""

import cv2  # For video capture and image processing
import mediapipe as mp  # For hand landmark detection
import hand_logic  # Import finger counting logic and mapping

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
                
                # Use logic from the separate file
                count = hand_logic.count_fingers(hand_landmarks)
                word = hand_logic.FINGER_WORDS.get(count, "NONE")
                
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
