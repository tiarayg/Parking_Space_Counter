import cv2
import pickle

# =========================
# UKURAN PARKIR
# =========================

# Vertical parking
widthV, heightV = 70, 150

# Horizontal parking
widthH, heightH = 150, 70

# =========================
# LOAD DATA
# =========================

try:
    with open('CarParkPos1', 'rb') as f:
        posList = pickle.load(f)
except:
    posList = []

# =========================
# MOUSE FUNCTION
# =========================

def mouseClick(events, x, y, flags, params):

    # LEFT CLICK = Vertical Slot
    if events == cv2.EVENT_LBUTTONDOWN:
        posList.append((x, y, 'V'))

    # MIDDLE CLICK = Horizontal Slot
    if events == cv2.EVENT_MBUTTONDOWN:
        posList.append((x, y, 'H'))

    # RIGHT CLICK = Delete Slot
    if events == cv2.EVENT_RBUTTONDOWN:

        for i, pos in enumerate(posList):

            x1, y1, mode = pos

            # Tentukan ukuran berdasarkan mode
            if mode == 'V':
                w, h = widthV, heightV
            else:
                w, h = widthH, heightH

            # Cek apakah klik berada di dalam kotak
            if x1 < x < x1 + w and y1 < y < y1 + h:
                posList.pop(i)
                break

    # Simpan data
    with open('CarParkPos1', 'wb') as f:
        pickle.dump(posList, f)

# =========================
# MAIN LOOP
# =========================

while True:

    img = cv2.imread('carParkImg2.png')

    img = cv2.resize(img, (1280, 720))

    # Gambar semua slot
    for pos in posList:

        x, y, mode = pos

        # Pilih ukuran sesuai orientasi
        if mode == 'V':
            w, h = widthV, heightV
        else:
            w, h = widthH, heightH

        # Warna kotak
        color = (255, 0, 255)

        # Draw rectangle
        cv2.rectangle(
            img,
            (x, y),
            (x + w, y + h),
            color,
            2
        )

        # Tampilkan mode
        cv2.putText(
            img,
            mode,
            (x + 5, y + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

    cv2.imshow("Image", img)

    cv2.setMouseCallback("Image", mouseClick)

    key = cv2.waitKey(1)

    # Tekan R untuk reset semua
    if key == ord('r'):
        posList = []

        with open('CarParkPos1', 'wb') as f:
            pickle.dump(posList, f)

    # Tekan Q untuk keluar
    if key == ord('q'):
        break

cv2.destroyAllWindows()