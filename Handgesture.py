import cv2
import mediapipe as mp
import math
import numpy as np


class handDetector:
    def _init_(self, mode=False, maxHands=1, detectionCon=0.7, trackCon=0.7):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]
        self.lmList = []
        self.bbox = []
        self.results = None   # ✅ Prevent AttributeError if findHands not called yet

        # For smoothing
        self.plocX, self.plocY = 0, 0
        self.clocX, self.clocY = 0, 0
        self.smoothening = 5  # higher = smoother, slower

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(
                        img, handLms, self.mpHands.HAND_CONNECTIONS
                    )
        return img

    def findPosition(self, img, handNo=0, draw=True):
        xList, yList = [], []
        self.lmList = []
        self.bbox = []

        if self.results and self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 4, (255, 0, 255), cv2.FILLED)

            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            self.bbox = (xmin, ymin, xmax, ymax)

            if draw:
                cv2.rectangle(img, (xmin - 20, ymin - 20),
                              (xmax + 20, ymax + 20),
                              (0, 255, 0), 2)
        return self.lmList, self.bbox

    def fingersUp(self):
        fingers = []
        if not self.lmList:
            return fingers

        # Thumb (⚠ works best for right hand — left hand may flip)
        if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Other fingers
        for id in range(1, 5):
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def findDistance(self, p1, p2, img, draw=True, r=10, t=3):
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]

    def smoothMouse(self, x, y, screenW, screenH, camW=640, camH=480, frameR=50):
        """Map hand coords to screen with smoothing (no hardcoded resolution)."""
        xMapped = np.interp(x, (frameR, camW - frameR), (0, screenW))
        yMapped = np.interp(y, (frameR, camH - frameR), (0, screenH))

        # Smooth movement
        self.clocX = self.plocX + (xMapped - self.plocX) / self.smoothening
        self.clocY = self.plocY + (yMapped - self.plocY) / self.smoothening
        self.plocX, self.plocY = self.clocX, self.clocY

        return self.clocX, self.clocY