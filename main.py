import cv2
import pickle
import cvzone
import numpy as np
import datetime

# ==========================================
# VIDEO 1
# ==========================================

cap1 = cv2.VideoCapture('carPark.mp4')

with open('CarParkPos', 'rb') as f:
    posList1 = pickle.load(f)

# UKURAN ASLI VIDEO 1
width1, height1 = 107, 48

slotStatus1 = {str(pos): False for pos in posList1}

# ==========================================
# VIDEO 2
# ==========================================

cap2 = cv2.VideoCapture('carPark2.mp4')

with open('CarParkPos1', 'rb') as f:
    posList2 = pickle.load(f)

# UKURAN VIDEO 2
widthV, heightV = 88, 165
widthH, heightH = 165, 88

slotStatus2 = {str(pos): False for pos in posList2}

# ==========================================
# WINDOW SIZE
# ==========================================

cv2.namedWindow("Parkiran 1", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Parkiran 1", 900, 600)

cv2.namedWindow("Parkiran 2", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Parkiran 2", 900, 600)

# ==========================================
# MINIMAP
# ==========================================

def drawMiniMap(img, posList, slotStatus):

    if not posList:
        return

    imgH, imgW = img.shape[:2]

    scale = 0.13

    allX = [p[0] for p in posList]
    allY = [p[1] for p in posList]

    parkW = max(allX) + 200
    parkH = max(allY) + 200

    mapW = int(parkW * scale) + 20
    mapH = int(parkH * scale) + 30

    mapX = imgW - mapW - 10
    mapY = imgH - mapH - 10

    overlay = img.copy()

    cv2.rectangle(
        overlay,
        (mapX, mapY),
        (mapX + mapW, mapY + mapH),
        (20, 20, 20),
        -1
    )

    cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)

    cv2.rectangle(
        img,
        (mapX, mapY),
        (mapX + mapW, mapY + mapH),
        (180, 180, 180),
        1
    )

    cv2.putText(
        img,
        'Denah Parkir',
        (mapX + 5, mapY + 14),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.35,
        (200, 200, 200),
        1
    )

    for pos in posList:

        # VIDEO 2
        if len(pos) == 3:

            x, y, mode = pos

            if mode == 'V':
                w, h = widthV, heightV
            else:
                w, h = widthH, heightH

        # VIDEO 1
        else:

            x, y = pos
            w, h = width1, height1

        mx = mapX + 5 + int(x * scale)
        my = mapY + 18 + int(y * scale)

        mw = max(int(w * scale), 4)
        mh = max(int(h * scale), 3)

        color = (0, 0, 200) if slotStatus[str(pos)] else (0, 200, 0)

        cv2.rectangle(img, (mx, my), (mx + mw, my + mh), color, -1)

        cv2.rectangle(img, (mx, my), (mx + mw, my + mh), (50, 50, 50), 1)

# ==========================================
# CHECK VIDEO 1
# ==========================================

def checkParkingSpace1(img, imgPro):

    spaceCounter = 0

    for pos in posList1:

        x, y = pos

        imgCrop = imgPro[y:y + height1, x:x + width1]

        count = cv2.countNonZero(imgCrop)

        if count < 900:

            color = (0, 255, 0)
            thickness = 5

            spaceCounter += 1

            slotStatus1[str(pos)] = False

        else:

            color = (0, 0, 255)
            thickness = 2

            slotStatus1[str(pos)] = True

        cv2.rectangle(
            img,
            pos,
            (pos[0] + width1, pos[1] + height1),
            color,
            thickness
        )

        cvzone.putTextRect(
            img,
            str(count),
            (x, y + height1 - 3),
            scale=1,
            thickness=2,
            offset=0,
            colorR=color
        )

    cvzone.putTextRect(
        img,
        f'Free: {spaceCounter}/{len(posList1)}',
        (100, 50),
        scale=3,
        thickness=5,
        offset=20,
        colorR=(0, 200, 0)
    )

# ==========================================
# CHECK VIDEO 2
# ==========================================

def checkParkingSpace2(img, imgPro):

    spaceCounter = 0

    for pos in posList2:

        x, y, mode = pos

        if mode == 'V':
            w, h = widthV, heightV
        else:
            w, h = widthH, heightH

        imgCrop = imgPro[y:y + h, x:x + w]

        count = cv2.countNonZero(imgCrop)

        if count < 1500:

            color = (0, 255, 0)
            thickness = 5

            spaceCounter += 1

            slotStatus2[str(pos)] = False

        else:

            color = (0, 0, 255)
            thickness = 2

            slotStatus2[str(pos)] = True

        cv2.rectangle(
            img,
            (x, y),
            (x + w, y + h),
            color,
            thickness
        )

        cvzone.putTextRect(
            img,
            str(count),
            (x, y + h - 3),
            scale=1,
            thickness=2,
            offset=0,
            colorR=color
        )

    cvzone.putTextRect(
        img,
        f'Free: {spaceCounter}/{len(posList2)}',
        (100, 50),
        scale=3,
        thickness=5,
        offset=20,
        colorR=(0, 200, 0)
    )

# ==========================================
# PROCESS VIDEO 1
# ==========================================

def processFrame1(cap):

    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    success, img = cap.read()

    if not success:
        return None, None

    # VIDEO 1 TIDAK DIRESIZE

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)

    imgThreshold = cv2.adaptiveThreshold(
        imgBlur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        25,
        16
    )

    imgMedian = cv2.medianBlur(imgThreshold, 5)

    kernel = np.ones((3, 3), np.uint8)

    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    return img, imgDilate

# ==========================================
# PROCESS VIDEO 2
# ==========================================

def processFrame2(cap):

    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    success, img = cap.read()

    if not success:
        return None, None

    # RESIZE KHUSUS VIDEO 2
    img = cv2.resize(img, (1280, 720))

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)

    imgThreshold = cv2.adaptiveThreshold(
        imgBlur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        25,
        16
    )

    imgMedian = cv2.medianBlur(imgThreshold, 5)

    kernel = np.ones((3, 3), np.uint8)

    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    return img, imgDilate

# ==========================================
# MAIN LOOP
# ==========================================

while True:

    # ======================================
    # VIDEO 1
    # ======================================

    img1, imgDilate1 = processFrame1(cap1)

    if img1 is not None:

        checkParkingSpace1(img1, imgDilate1)

        # MINIMAP
        drawMiniMap(img1, posList1, slotStatus1)

        # TIMESTAMP
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cv2.putText(
            img1,
            now,
            (10, img1.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        # TITLE
        cv2.putText(
            img1,
            "Parkiran 1",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 0),
            2
        )

        cv2.imshow("Parkiran 1", img1)

    # ======================================
    # VIDEO 2
    # ======================================

    img2, imgDilate2 = processFrame2(cap2)

    if img2 is not None:

        checkParkingSpace2(img2, imgDilate2)

        # MINIMAP
        drawMiniMap(img2, posList2, slotStatus2)

        # TIMESTAMP
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cv2.putText(
            img2,
            now,
            (10, img2.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        # TITLE
        cv2.putText(
            img2,
            "Parkiran 2",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 0),
            2
        )

        cv2.imshow("Parkiran 2", img2)

    # ======================================
    # EXIT
    # ======================================

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap1.release()
cap2.release()

cv2.destroyAllWindows()