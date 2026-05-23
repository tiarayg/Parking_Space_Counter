import cv2

cap = cv2.VideoCapture('carPark2.mp4')

success, frame = cap.read()

if success:

    # SAMAKAN ukuran
    frame = cv2.resize(frame, (1280, 720))

    cv2.imwrite('carParkImg2.png', frame)

    print("Frame berhasil disimpan!")

cap.release()