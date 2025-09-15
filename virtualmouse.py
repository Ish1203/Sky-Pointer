import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
import math
import datetime
import os
import threading
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import screen_brightness_control as sbc
from luffy import luffy_main   # Import Luffy assistant

# -------------------- Setup --------------------
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=2)
mpDraw = mp.solutions.drawing_utils

screen_width, screen_height = pyautogui.size()

# Camera setup
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
time.sleep(1)

# Audio setup
try:
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
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
gesture_label = ""
luffy_active = False   # Track if Luffy is running

# Screenshot folder
screenshot_folder = "screenshots"
os.makedirs(screenshot_folder, exist_ok=True)

# -------------------- Helper Functions --------------------
def fingersUp(lmList):
    fingers = []
    fingers.append(1 if lmList[4][0] > lmList[3][0] else 0)  # Thumb
    for id in range(8, 21, 4):
        fingers.append(1 if lmList[id][1] < lmList[id-2][1] else 0)
    return fingers

def findDistance(p1, p2):
    return np.hypot(p2[0]-p1[0], p2[1]-p1[1])

def take_screenshot():
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.png")
    filepath = os.path.join(screenshot_folder, filename)
    pyautogui.screenshot(filepath)
    print(f"📸 Screenshot saved: {filepath}")

def draw_finger_overlay(img, fingers):
    h, w, _ = img.shape
    x0, y0 = w - 200, 20
    cv2.rectangle(img, (x0, y0), (x0+180, y0+150), (50,50,50), -1)
    cv2.putText(img, "Fingers:", (x0+10, y0+20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)
    labels = ["Thumb","Index","Middle","Ring","Pinky"]
    for i, label in enumerate(labels):
        color = (0,255,0) if fingers[i]==1 else (100,100,100)
        cv2.putText(img, label, (x0+10, y0+50+i*20),
                    cv2.FONT_HERSHEY_SIMPLEX,0.5,color,2)

# -------------------- Main Loop --------------------
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
                cx, cy = int(lm.x*w), int(lm.y*h)
                lmList.append((cx,cy))
            lmLists.append(lmList)
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    gesture_label = ""
    for i, lmList in enumerate(lmLists):
        if not lmList:
            continue
        fingers = fingersUp(lmList)

        # ---------------- Right Hand Controls ---------------- #
        if i == 0:
            if fingers == [0,1,0,0,0]:  # Cursor move
                x, y = lmList[8]
                screen_x = np.interp(x,(100,540),(0,screen_width))
                screen_y = np.interp(y,(100,380),(0,screen_height))
                curr_x = prev_x + (screen_x - prev_x)/smoothening
                curr_y = prev_y + (screen_y - prev_y)/smoothening
                pyautogui.moveTo(curr_x,curr_y)
                prev_x, prev_y = curr_x, curr_y
                gesture_label = "Cursor Move"

            elif fingers == [0,1,1,0,0]:  # Left click
                dist = findDistance(lmList[8], lmList[12])
                if dist<30:
                    pyautogui.click()
                    gesture_label = "Left Click"
                    time.sleep(0.2)

            elif fingers == [1,1,0,0,0]:  # Right click
                pyautogui.rightClick()
                gesture_label = "Right Click"
                time.sleep(0.3)

            elif fingers == [0,0,0,0,0]:  # Drag
                if not dragging:
                    pyautogui.mouseDown()
                    dragging = True
                    gesture_label = "Drag Mode"
            elif dragging and fingers != [0,0,0,0,0]:
                pyautogui.mouseUp()
                dragging = False

            elif fingers == [0,0,0,1,0]:  # Scroll up
                pyautogui.scroll(200)
                gesture_label = "Scroll Up"
                time.sleep(0.2)

            elif fingers == [0,0,0,1,1]:  # Scroll down
                pyautogui.scroll(-200)
                gesture_label = "Scroll Down"
                time.sleep(0.2)

            elif fingers == [1,0,0,0,1]:  # Screenshot
                take_screenshot()
                gesture_label = "Screenshot"
                time.sleep(0.5)

            elif fingers == [1,0,0,1,1]:  # Tab Change
                pyautogui.hotkey('ctrl','tab')
                gesture_label = "Tab Change"
                time.sleep(0.3)

            elif fingers == [0,0,0,0,1]:  # Brightness
                dist = findDistance(lmList[4], lmList[20])
                bright = np.interp(dist,[30,200],[0,100])
                try:
                    sbc.set_brightness(int(bright))
                    gesture_label = "Brightness Control"
                except Exception as e:
                    print(f"⚠️ Brightness error: {e}")

            elif fingers == [0,1,1,1,0] and not luffy_active:  # NEW Gesture → Activate Luffy
                luffy_active = True
                threading.Thread(target=luffy_main, daemon=True).start()
                gesture_label = "Luffy Activated"
                time.sleep(0.5)

        # ---------------- Left Hand Controls ---------------- #
        if i == 1 and volume:
            if fingers[0]==0 and fingers[1]==1 and fingers[2]==1:  # Volume
                y = lmList[9][1]
                vol = np.interp(y,[100,380],[1.0,0.0])
                volume.SetMasterVolumeLevelScalar(vol,None)
                current_volume_percent = int(vol*100)
                gesture_label = "Volume Control"

            elif fingers == [1,1,1,1,1]:
                pyautogui.hotkey('win','d')
                gesture_label = "Minimize All"
                time.sleep(0.5)

            elif fingers == [0,1,1,1,1]:
                pyautogui.hotkey('win','up')
                gesture_label = "Maximize"
                time.sleep(0.5)

            elif fingers == [1,0,1,0,1]:
                pyautogui.hotkey('ctrl','w')
                gesture_label = "Close Tab"
                time.sleep(0.3)

        draw_finger_overlay(img, fingers)

    # ---------------- Display ----------------
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img,f'FPS: {int(fps)}',(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2)
    cv2.putText(img,f'Vol: {current_volume_percent}%',(10,70),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
    if gesture_label:
        cv2.putText(img,f'{gesture_label}',(10,110),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),2)

    cv2.imshow("Hand Tracking", img)
    if cv2.waitKey(1) & 0xFF==ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
