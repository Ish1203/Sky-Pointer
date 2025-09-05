import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from screen_brightness_control import set_brightness
import datetime
import os

# Initialize mediapipe Hands (2 hands)
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=2)
mpDraw = mp.solutions.drawing_utils

# Screen size
screen_width, screen_height = pyautogui.size()

# Camera setup
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
time.sleep(1)

# Audio setup
try:
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume.iid, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
except Exception as e:
    print(f"⚠️ Audio control error: {e}")
    volume = None

# Variables
prev_x, prev_y = 0, 0
smoothening = 5
dragging = False
pTime = time.time()
current_volume_percent = 0

# Screenshot folder
screenshot_folder = "screenshots"
os.makedirs(screenshot_folder, exist_ok=True)

# Helper functions
def fingersUp(lmList):
    fingers = []
    fingers.append(1 if lmList[4][0] > lmList[3][0] else 0)  # Thumb
    for id in range(8, 21, 4):  # Index to pinky
        fingers.append(1 if lmList[id][1] < lmList[id - 2][1] else 0)
    return fingers

def findDistance(p1, p2):
    return np.hypot(p2[0] - p1[0], p2[1] - p1[1])

def take_screenshot():
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.png")
    filepath = os.path.join(screenshot_folder, filename)
    pyautogui.screenshot(filepath)
    print(f"📸 Screenshot saved: {filepath}")

# Main loop
while True:
    success, img = cap.read()
    if not success:
        continue

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    lmLists = []
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            lmList = []
            h, w, c = img.shape
            for id, lm in enumerate(handLms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append((cx, cy))
            lmLists.append(lmList)
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    for i, lmList in enumerate(lmLists):
        if not lmList:
            continue

        fingers = fingersUp(lmList)

        # ---------------- Right Hand Controls ---------------- #
        if i == 0:  # Assume first hand is right
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
            elif fingers == [0, 1, 1, 0, 0] and findDistance(lmList[8], lmList[12]) < 30:
                pyautogui.click()
                time.sleep(0.2)

            # Drag & Drop / Right Click
            elif fingers == [1, 1, 0, 0, 0]:
                dist = findDistance(lmList[4], lmList[8])
                if dist < 40 and not dragging:
                    pyautogui.mouseDown()
                    dragging = True
                elif dist > 60 and dragging:
                    pyautogui.mouseUp()
                    dragging = False
                else:
                    pyautogui.rightClick()
                    time.sleep(0.3)

            # Scroll
            elif fingers == [0, 0, 0, 1, 0]:
                pyautogui.scroll(200)
                time.sleep(0.2)

            # Screenshot
            elif fingers == [1, 1, 1, 1, 1]:
                take_screenshot()
                time.sleep(0.5)

        # ---------------- Left Hand Controls ---------------- #
        if i == 1:  # Assume second hand is left
            # Volume Control
            if fingers == [1, 1, 1, 0, 0] and volume:
                dist = findDistance(lmList[4], lmList[8])  # Thumb–Index
                vol = np.interp(dist, [30, 200], [-65.25, 0])
                currentVol = volume.GetMasterVolumeLevel()
                newVol = currentVol + (vol - currentVol) / 5
                volume.SetMasterVolumeLevel(newVol, None)

                # Convert dB to percentage
                volRange = volume.GetVolumeRange()
                minVol, maxVol = volRange[0], volRange[1]
                currentVol = volume.GetMasterVolumeLevel()
                current_volume_percent = int(np.interp(currentVol, [minVol, maxVol], [0, 100]))

            # Brightness Control
            elif fingers == [0, 0, 0, 0, 1]:
                dist = findDistance(lmList[4], lmList[20])
                bright = np.interp(dist, [30, 200], [0, 100])
                try:
                    set_brightness(int(bright))
                except Exception as e:
                    print(f"⚠️ Brightness error: {e}")

            # Minimize All
            elif fingers == [1, 1, 1, 1, 1]:
                pyautogui.hotkey('win', 'd')
                time.sleep(0.5)

            # Maximize
            elif fingers == [0, 1, 1, 1, 1]:
                pyautogui.hotkey('win', 'up')
                time.sleep(0.5)

            # Close Tab
            elif fingers == [1, 0, 1, 0, 1]:
                pyautogui.hotkey('ctrl', 'w')
                time.sleep(0.3)

            # Change Tab
            elif fingers == [1, 0, 0, 0, 1]:
                pyautogui.hotkey('ctrl', 'tab')
                time.sleep(0.3)

    # FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Volume %
    if volume:
        cv2.putText(img, f'Vol: {current_volume_percent}%', (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Hand Tracking (2 Hands)", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
