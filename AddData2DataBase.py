import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import config

# Credentials and the database URL are loaded from .env (see config.py)
cred = credentials.Certificate(config.FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred, config.firebase_options(storage=False))

ref = db.reference("Students")

# Example records - the keys must match the image filenames in Images/
# (e.g. Images/1001.png). The names below are fictional placeholders.
data = {
    "1001":
        {
            "Name": "Alex Example",
            "Subjects": "Computer-Science",
            "Year": 13,
            "Attendance": 5,
            "Standing": "G",
            "last_attendance_time": "2024-03-07 00:54:34",
            "Starting Year": "2018"
        },
    "1002":
        {
            "Name": "Sam Sample",
            "Subjects": "Photography",
            "Year": 13,
            "Attendance": 3,
            "Standing": "B",
            "last_attendance_time": "2024-03-04 00:54:34",
            "Starting Year": "2018"
        },
}

for key, value in data.items():
    ref.child(key).set(value)
