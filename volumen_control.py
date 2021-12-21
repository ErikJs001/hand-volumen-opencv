# Erik Josías González Lucas  - 21 | Dic | 2021

# Hand Tracking
import cv2
import time
import numpy as np
import hand_tracking as ht

# Distancia
import math

# Volumen
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Definimos el ancho y el alto de la camara y se lo asignamos
wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = ht.handDetector(detectionCon = 0.7)


# VOLUMEN
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Obtenemos el rango del volumen y definimos valores para el sonido
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = np.interp(volume.GetMasterVolumeLevel(), [-95, 0], [400, 150])
volPer = np.interp(volume.GetMasterVolumeLevel(), [-95, 0], [0, 100])



while True:
    ret, img = cap.read()
    # Mandamos el img al módulo para que dibuje las líneas
    img = detector.findHands(img)
    # Obtenemos las posiciones
    lmList = detector.findPositions(img, draw=False)

    # Dibujamos circulos en el pulgar y en el índice y una línea entre ellos
    if len(lmList) != 0:
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 7, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 7, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 7, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)

        # Hand Range 50 - 300
        # Volumen Range -95 - 0
        vol = np.interp(length, [50, 300], [minVol, maxVol])
        volBar = np.interp(length, [50, 300], [400, 150])
        volPer = np.interp(length, [50, 300], [0, 100])
        volume.SetMasterVolumeLevel(vol, None)

        # Si es menos de 50, punto verde en medio
        if length < 50:
            cv2.circle(img, (cx, cy), 7, (0, 255, 0), cv2.FILLED) 

    # Barra del porcentaje del sonido
    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                1, (0, 255, 0), 3)

    # Calculamos segundos para los fps
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    # Contador de FPS
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)


    # Se muestra la pantalla y con 'q' la podemos cerrar
    cv2.imshow("image", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
            break

# Terminamos la captura y destruimos todas las ventanas
cap.release()
cv2.destroyAllWindows()