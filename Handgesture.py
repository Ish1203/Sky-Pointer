import cv2
import mediapipe as mp
import math

class HandDetector:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.7, trackCon=0.7):
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
        self.tipIds = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky

    def findHands(self, img, draw=True):
        """Detects hands and returns processed image and list of hands with landmarks."""
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        hands_data = []

        if self.results.multi_hand_landmarks:
            for i, handLms in enumerate(self.results.multi_hand_landmarks):
                lmList, xList, yList = [], [], []

                # Hand type (Right/Left)
                hand_type = self.results.multi_handedness[i].classification[0].label.lower()

                h, w, c = img.shape
                for id, lm in enumerate(handLms.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])
                    xList.append(cx)
                    yList.append(cy)

                if lmList:  # Safety check
                    xmin, xmax = min(xList), max(xList)
                    ymin, ymax = min(yList), max(yList)
                    bbox = (xmin, ymin, xmax, ymax)
                    center = ((xmin + xmax) // 2, (ymin + ymax) // 2)

                    hands_data.append({
                        'lmList': lmList,
                        'bbox': bbox,
                        'center': center,
                        'type': hand_type
                    })

                    if draw:
                        self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
                        cv2.rectangle(img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20),
                                      (0, 255, 0), 2)

        return img, hands_data

    def fingersUp(self, lmList, hand_type="right"):
        """Returns list of 5 integers: 1 if finger up, 0 if down."""
        fingers = []

        if not lmList or len(lmList) < 21:  # Safety check
            return [0, 0, 0, 0, 0]

        # Thumb
        if hand_type == "right":
            fingers.append(1 if lmList[self.tipIds[0]][1] < lmList[self.tipIds[0] - 1][1] else 0)
        else:  # Left hand
            fingers.append(1 if lmList[self.tipIds[0]][1] > lmList[self.tipIds[0] - 1][1] else 0)

        # Other fingers (Index, Middle, Ring, Pinky)
        for id in range(1, 5):
            fingers.append(1 if lmList[self.tipIds[id]][2] < lmList[self.tipIds[id] - 2][2] else 0)

        return fingers

    def findDistance(self, p1, p2, lmList, img=None, draw=True, r=10, t=3):
        """Finds distance between two points."""
        if not lmList or p1 >= len(lmList) or p2 >= len(lmList):
            return 0, img, [0, 0, 0, 0, 0, 0]

        x1, y1 = lmList[p1][1], lmList[p1][2]
        x2, y2 = lmList[p2][1], lmList[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if img is not None and draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]
