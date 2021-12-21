import cv2
import mediapipe as mp
import time

class handDetector():
    def __init__(self, mode=True, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode = self.mode, 
            max_num_hands = self.maxHands, 
            min_detection_confidence = self.detectionCon,
            min_tracking_confidence = self.trackCon)

        self.mp_drawing = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        self.results = self.hands.process(img_rgb)

        if self.results.multi_hand_landmarks is not None:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_drawing.draw_landmarks(
                        img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                    )

        return img

    def findPositions(self, img, handNo=0, draw=True):
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]

            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)

                lmList.append([id, cx, cy])

                if draw:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        return lmList 


def main():
    pTime = 0
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    detector = handDetector()

    while True:
        success, img = cap.read()
        frame = detector.findHands(img)
        lmList = detector.findPositions(img)
        
        # if len(lmList) != 0:
        #     print(lmList[4])

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(frame, str(int(fps)), (18, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        cv2.imshow("Image", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

if __name__ == "__main__":
    main()