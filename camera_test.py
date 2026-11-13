"""Development Stage One - webcam smoke test.

Checks that the UI background loads and that OpenCV can open the webcam and
display frames. Press 'q' to quit.
"""
import cv2

import config

img_background = cv2.imread(config.BACKGROUND_PATH)

if img_background is None:
    print("Error: Image not found. Check the path!")
else:
    print("Image loaded successfully!")

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

if not cap.isOpened():
    print("Error: Camera not detected!")
    exit()

while True:
    success, img = cap.read()
    if not success:
        print("Error: Couldn't capture frame from camera.")
        break
    cv2.imshow("Webcam", img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
