 
import cv2
import mediapipe as mp
import pyautogui
import time
import controls

pyautogui.FAILSAFE = True

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75
)

camera = cv2.VideoCapture(0)

def recognize_gesture(hand):
    p = hand.landmark

    index = p[8].y < p[6].y
    middle = p[12].y < p[10].y
    ring = p[16].y < p[14].y
    pinky = p[20].y < p[18].y

    thumb_up = p[4].y < p[3].y - 0.04
    thumb_down = p[4].y > p[3].y + 0.04

    count = sum([index, middle, ring, pinky])

    if count == 4:
        return "OPEN PALM"
    elif count == 1 and index:
        return "INDEX"
    elif count == 0 and thumb_up:
        return "THUMBS UP"
    elif count == 0 and thumb_down:
        return "THUMBS DOWN"
    elif count == 0:
        return "FIST"

    return "UNKNOWN"


print("AIRCOMMAND STARTED!")
print("Press Q to exit.")

candidate = None
stable_since = time.time()
last_action = 0
cooldown = 1.2
controls_enabled = True
last_gesture = None

previous_y = None
last_scroll_time = 0
scroll_threshold = 0.015

while True:
    success, frame = camera.read()

    if not success:
        print("Camera error!")
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    gesture = "NO HAND"
    current_y = None
    now = time.time()

    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]

        mp_draw.draw_landmarks(
            frame, hand, mp_hands.HAND_CONNECTIONS
        )

        gesture = recognize_gesture(hand)

        if gesture == "INDEX":
            current_y = hand.landmark[8].y

    if gesture != candidate:
        candidate = gesture
        stable_since = now

    stable = now - stable_since >= 0.35

    if stable and gesture != last_gesture:
        if now - last_action >= cooldown:

            if gesture == "FIST":
                controls_enabled = False
                print("SAFETY STOP - Controls disabled!")
                last_action = now

            elif gesture == "OPEN PALM":
                if not controls_enabled:
                    controls_enabled = True
                    print("Controls re-enabled!")
                else:
                    controls.play_pause()

                last_action = now

            elif controls_enabled:
                if gesture == "THUMBS UP":
                    controls.volume_up()
                    last_action = now

                elif gesture == "THUMBS DOWN":
                    controls.volume_down()
                    last_action = now

        last_gesture = gesture

    # Continuous scrolling using index finger movement
    if controls_enabled and stable and gesture == "INDEX":
        if previous_y is not None:
            movement = previous_y - current_y

            if abs(movement) > scroll_threshold:
                if now - last_scroll_time > 0.18:
                    if movement > 0:
                        pyautogui.scroll(2)
                        print("Scrolling UP")
                    else:
                        pyautogui.scroll(-2)
                        print("Scrolling DOWN")

                    last_scroll_time = now

        previous_y = current_y
    else:
        previous_y = None

    status = "ACTIVE" if controls_enabled else "STOPPED"

    cv2.putText(
        frame, "AIRCOMMAND", (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX, 0.9,
        (0, 255, 0), 2
    )

    cv2.putText(
        frame, "Gesture: " + gesture, (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7,
        (255, 255, 0), 2
    )

    cv2.putText(
        frame, "Status: " + status, (20, 110),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7,
        (0, 255, 0) if controls_enabled else (0, 0, 255),
        2
    )

    cv2.imshow("AIRCOMMAND - LAPTOP CONTROL", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
hands.close()
cv2.destroyAllWindows()
