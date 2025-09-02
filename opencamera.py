import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math
import screen_brightness_control as sbc

# Camera settings
wCam, hCam = 640, 480
frameR = 100
smoothening = 5

cap = None
for cam_index in [0, 1, 2]:
    cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
    cap.set(3, wCam)
    cap.set(4, hCam)
    if cap.isOpened():
        print(f"Camera opened on index {cam_index}")
        break

if cap is None or not cap.isOpened():
    print("Could not open any camera.")
    exit()

# MediaPipe
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

# System variables
plocX, plocY = 0, 0
clocX, clocY = 0, 0
screenW, screenH = pyautogui.size()
dragging = False
multi_selecting = False
tab_switched = False

# Volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol, maxVol = volRange[0], volRange[1]

# Detect fingers
def fingersUp(lmList):
    tipIds = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb
    if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers
    for id in range(1, 5):
        if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers

while True:
    success, img = cap.read()
    if not success:
        print("Failed to read frame.")
        break

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    lmList = []

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

    if lmList:
        fingers = fingersUp(lmList)
        x1, y1 = lmList[8][1], lmList[8][2]   # Index tip
        x2, y2 = lmList[12][1], lmList[12][2] # Middle tip
        x0, y0 = lmList[4][1], lmList[4][2]   # Thumb tip
        x4, y4 = lmList[20][1], lmList[20][2] # Pinky tip
        x3, y3 = lmList[16][1], lmList[16][2] # Ring tip

        # Distance calculations
        pinch_distance = math.hypot(x1 - x0, y1 - y0)
        index_middle_dist = math.hypot(x1 - x2, y1 - y2)

        # -------------------- MOVE CURSOR --------------------
        if fingers == [0,1,0,0,0]:
            xM = np.interp(x1, (frameR, wCam - frameR), (0, screenW))
            yM = np.interp(y1, (frameR, hCam - frameR), (0, screenH))
            clocX = plocX + (xM - plocX) / smoothening
            clocY = plocY + (yM - plocY) / smoothening
            pyautogui.moveTo(clocX, clocY)
            plocX, plocY = clocX, clocY

        # -------------------- LEFT CLICK --------------------
        elif fingers == [0,1,1,0,0] and index_middle_dist < 40:
            pyautogui.click(button="left")
            time.sleep(0.3)

        # -------------------- RIGHT CLICK --------------------
        elif fingers == [1,1,0,0,0]:
            pyautogui.click(button="right")
            time.sleep(0.3)

        # -------------------- DOUBLE CLICK --------------------
        elif fingers == [0,1,1,0,0] and index_middle_dist > 50:
            pyautogui.doubleClick()
            time.sleep(0.3)

        # -------------------- SCROLL --------------------
        elif fingers == [0,0,0,1,0]:
            pyautogui.scroll(-50)
            time.sleep(0.2)

        # -------------------- DRAG & DROP --------------------
        elif pinch_distance < 40 and not dragging:
            pyautogui.mouseDown()
            dragging = True
        elif pinch_distance > 50 and dragging:
            pyautogui.mouseUp()
            dragging = False

               # -------------------- MULTIPLE SELECTION --------------------
        elif fingers == [0,1,1,0,0] and pinch_distance < 40:
            if not multi_selecting:
                pyautogui.keyDown("ctrl")
                multi_selecting = True
        elif multi_selecting:
            pyautogui.keyUp("ctrl")
            multi_selecting = False

        # -------------------- VOLUME CONTROL --------------------
        elif fingers == [1,1,0,0,0]:
            length = math.hypot(x1 - x0, y1 - y0)
            vol = np.interp(length, [30, 200], [minVol, maxVol])
            volume.SetMasterVolumeLevel(vol, None)

        # -------------------- BRIGHTNESS CONTROL --------------------
        elif fingers == [0,0,0,0,1]:
            brightness = np.interp(y4, [100, hCam-100], [100, 0])
            sbc.set_brightness(int(brightness))

        # -------------------- CHANGE TAB --------------------
        elif fingers == [1,0,0,0,1] and not tab_switched:
            pyautogui.hotkey("ctrl", "tab")
            tab_switched = True
            time.sleep(0.4)
        else:
            tab_switched = False

    cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 255, 0), 2)
    cv2.imshow("Gesture Controller", img)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
