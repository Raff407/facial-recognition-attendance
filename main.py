import os
import pickle
import cv2
import face_recognition
import cvzone
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

import config

# Credentials and project URLs are loaded from .env (see config.py)
cred = credentials.Certificate(config.FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred, config.firebase_options())

bucket = storage.bucket()  # Get the bucket

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 640)
cap.set(4, 480)

# Check if the camera is opened correctly
if not cap.isOpened():
    print("Error: Camera not detected!")
    exit()

# background image
img_background = cv2.imread(config.BACKGROUND_PATH)

#importing mode files into list
folderModePath = config.MODES_DIR
modePathList = sorted(os.listdir(folderModePath))  # sorted so mode order is deterministic
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
# print(len(imgModeList))

# Load the encoding file
print("Loading Encode File ...")
file = open(config.ENCODINGS_PATH, 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)
print("Encoded File Loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []

# Read frames from the camera
while True:
    sucess, frame = cap.read()

    # Resize the frame to improve performance
    imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)  # Resize the image to 1/4 of its size
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)  # Convert the image to RGB, OpenCV uses BGR instead of RGB

    # Find the face locations and encode the faces and compare them with the known faces
    faceCurFrame = face_recognition.face_locations(imgS)  # Find the face locations in the current frame
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)  # Encode the faces in the current frame

    img_background[162:162 + 480, 55:55 + 640] = frame
    img_background[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)  # Compare the faces
            faceDistance = face_recognition.face_distance(encodeListKnown, encodeFace)  # Calc distance between faces
            # print("matches: ", matches)
            # print("faceDistance: ", faceDistance)

            matchIndex = np.argmin(faceDistance)  # Get the index of the face with the minimum distance
            # print("matchIndex: ", matchIndex) # Print the index of the face with the minimum distance - 0

            if matches[matchIndex]:
                # print("Known Face Detected")
                # print(studentIds[matchIndex])
                y1, x2, y2, x1 = faceLoc  # Get face locations - Very weird mapping
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4  # Resize faceloc to match the OG frame 0.25
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1  # Get the bounding box of the face
                img_background = cvzone.cornerRect(img_background, bbox, rt=0)
                id = studentIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(img_background, "Loading", (300, 250), 2, 2, offset=20, border=1)
                    cv2.imshow("Face Attendance", img_background)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:

            if counter == 1:
                # Get Data
                studentInfo = db.reference(f"Students/{id}").get()
                print(studentInfo)
                # Get Image from Storage
                blob = bucket.get_blob(f'Images/{id}.png')
                if blob is not None:
                    blob_data = blob.download_as_string()
                    array = np.frombuffer(blob_data, np.uint8)
                    imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)
                    # Resize the image to the correct dimensions
                    imgStudent = cv2.resize(imgStudent, (216, 216))
                    # Update data of attendance:
                    datetimeObject = datetime.strptime(studentInfo["last_attendance_time"], "%Y-%m-%d %H:%M:%S")
                    secondsElapsed = (datetime.now() - datetimeObject).total_seconds()  # Calculate the time difference
                    print(secondsElapsed)
                    if secondsElapsed > 30:
                        ref = db.reference(f"Students/{id}")
                        studentInfo["Attendance"] += 1
                        ref.child("Attendance").set(studentInfo["Attendance"])
                        ref.child("last_attendance_time").set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    else:
                        modeType = 3
                        counter = 0
                        img_background[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                # else:
                #     print("File not found in the specified path.")
                #     # Use a placeholder image
                #     imgStudent = np.zeros((216, 216, 3), dtype=np.uint8)
                #     #update data of attendance:
                #     # ref = db.reference(f"Students/{id}")
                #     # studentInfo["Attendance"] += 1
                #     # ref.child("Attendance").set(studentInfo["Attendance"])


            if modeType != 3:

                # Displaying the student info
                if 10 < counter <= 20:  # Displaying the student info
                    modeType = 2  # Attendance Mode

                img_background[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <= 10:
                    cv2.putText(img_background, str(studentInfo["Attendance"]), (861, 125),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(img_background, str(studentInfo["Subjects"]), (1006, 550),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(img_background, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(img_background, str(studentInfo["Standing"]), (910, 625),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(img_background, str(studentInfo["Year"]), (1025, 625),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(img_background, str(studentInfo["Starting Year"]), (1125, 625),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['Name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(img_background, str(studentInfo['Name']), (808 + offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    img_background[175:175 + 216, 909:909 + 216] = imgStudent

                counter += 1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    img_background[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0


    # Display the frame
    cv2.imshow("Camera Test", frame)
    cv2.imshow("Face Attendance", img_background)
    if not sucess:
        print("Error: Couldn't capture frame from camera.")
        break

    # Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
