import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

import config

# Firebase Database
# Credentials and project URLs are loaded from .env (see config.py)
cred = credentials.Certificate(config.FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred, config.firebase_options())

# Importing Student Images
folderPath = config.IMAGES_DIR
pathList = [p for p in os.listdir(folderPath) if p.lower().endswith((".png", ".jpg", ".jpeg"))]
print(pathList)
imgList = []
studentIDs = []

for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentID = os.path.splitext(path)[0]
    studentIDs.append(studentID)

    # Upload to Firebase Storage
    fileName = os.path.join(folderPath, path)
    bucket = storage.bucket()
    # Upload with just Images/ID.png format (matching what your main script expects)
    blob = bucket.blob(f'Images/{studentID}.png')
    blob.upload_from_filename(fileName)

    # print(path)
    # print(os.path.splitext(path)[0])
print(studentIDs)


def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList


print("Encoding Started ...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIDs]
print("Encoding Complete")

file = open(config.ENCODINGS_PATH, 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")
