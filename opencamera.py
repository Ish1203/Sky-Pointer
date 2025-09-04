import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from screen_brightness_control import set_brightness

# Initialize mediapipe Hands
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

# Screen size
screen_width, screen_height = pyautogui.size()

# Camera setup (auto-detect)
cam_index = -1
cap = None
for i in range(3):
    test_cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if test_cap.isOpened():
        cam_index = i
        cap = test_cap
        print(f"✅ Camera opened on index {i}")
        break

if cam_index == -1 or cap is None:
    print("❌ No camera found!")
    exit()

cap.set(3, 640)
cap.set(4, 480)
time.sleep(1)  # Give camera time to warm up

# Audio setup
try:
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume.iid, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
except Exception as e:
    print(f"⚠ Audio control error: {e}")
    volume = None

# Variables for state tracking
prev_x, prev_y = 0, 0
smoothening = 5
dragging = False
last_click_time = 0

# FPS tracking
pTime = time.time()

# Helper functions
def fingersUp(lmList):
    fingers = []
    fingers.append(1 if lmList[4][0] > lmList[3][0] else 0)  # Thumb
    for id in range(8, 21, 4):  # Index to pinky
        fingers.append(1 if lmList[id][1] < lmList[id - 2][1] else 0)
    return fingers

def findDistance(p1, p2):
    return np.hypot(p2[0] - p1[0], p2[1] - p1[1])

# Main loop
while True:
    success, img = cap.read()
    if not success:
        print("⚠ Frame grab failed, retrying...")
        continue

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    lmList = []

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append((cx, cy))
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    if lmList:
        fingers = fingersUp(lmList)

        # Mouse Move
        if fingers == [0, 1, 0, 0, 0]:
            x, y = lmList[8]
            screen_x = np.interp(x, (100, 540), (0, screen_width))
            screen_y = np.interp(y, (100, 380), (0, screen_height))
            curr_x = prev_x + (screen_x - prev_x) / smoothening
            curr_y = prev_y + (screen_y - prev_y) / smoothening
            pyautogui.moveTo(curr_x, curr_y)
            prev_x, prev_y = curr_x, curr_y

        # Left Click
        elif fingers == [0, 1, 1, 0, 0]:
            if findDistance(lmList[8], lmList[12]) < 30:
                pyautogui.click()
                time.sleep(0.2)

        # Right Click
        elif fingers == [1, 1, 0, 0, 0]:
            pyautogui.rightClick()
            time.sleep(0.3)

        # Double Click
        elif fingers == [0, 1, 1, 0, 0]:
            if findDistance(lmList[8], lmList[12]) > 40:
                pyautogui.doubleClick()
                time.sleep(0.3)

        # Scroll
        elif fingers == [0, 0, 0, 1, 0]:
            pyautogui.scroll(200)
            time.sleep(0.2)

        # Drag & Drop
        elif fingers == [1, 1, 0, 0, 0]:
            if findDistance(lmList[4], lmList[8]) < 40:
                if not dragging:
                    pyautogui.mouseDown()
                    dragging = True
            else:
                if dragging:
                    pyautogui.mouseUp()
                    dragging = False

        # Volume Control
        elif fingers == [1, 1, 1, 0, 0] and volume:
            dist = findDistance(lmList[4], lmList[8])
            vol = np.interp(dist, [30, 200], [-65.25, 0])
            volume.SetMasterVolumeLevel(vol, None)

        # Brightness Control
        elif fingers == [0, 0, 0, 0, 1]:
            dist = findDistance(lmList[4], lmList[20])
            bright = np.interp(dist, [30, 200], [0, 100])
            try:
                set_brightness(int(bright))
            except Exception as e:
                print(f"⚠ Brightness error: {e}")

        # Change Tab
        elif fingers == [1, 0, 0, 0, 1]:
            pyautogui.hotkey('ctrl', 'tab')
            time.sleep(0.3)

    # FPS display
    cTime = time.time()
    fps = 1 / (cTime - pTime)#FPS calculation
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("Hand Tracking", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("🛑 Exiting gesture control. Goodbye!")
        break

cap.release()
cv2.destroyAllWindows()