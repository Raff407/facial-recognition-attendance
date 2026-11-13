"""Shared configuration for the attendance scripts.

All secrets and project-specific values are read from environment variables
(or a local ``.env`` file, which is git-ignored). Nothing sensitive is stored
in source control. See ``.env.example`` for the expected keys.
"""
import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Path to the Firebase service-account key (never commit this file)
FIREBASE_CREDENTIALS = os.getenv(
    "FIREBASE_CREDENTIALS", os.path.join(BASE_DIR, "serviceAccountKey.json")
)
FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")
FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET")

# Local paths
IMAGES_DIR = os.path.join(BASE_DIR, "Images")                # student photos (git-ignored)
RESOURCES_DIR = os.path.join(BASE_DIR, "Resources")
BACKGROUND_PATH = os.path.join(RESOURCES_DIR, "format.png")  # main UI background
MODES_DIR = os.path.join(RESOURCES_DIR, "Modes")             # right-hand status panels
ENCODINGS_PATH = os.path.join(BASE_DIR, "EncodedFile.p")     # face encodings (git-ignored)


def firebase_options(storage=True):
    """Return the options dict passed to ``firebase_admin.initialize_app``."""
    if not FIREBASE_DATABASE_URL:
        raise RuntimeError("FIREBASE_DATABASE_URL is not set - copy .env.example to .env")
    options = {"databaseURL": FIREBASE_DATABASE_URL}
    if storage:
        if not FIREBASE_STORAGE_BUCKET:
            raise RuntimeError("FIREBASE_STORAGE_BUCKET is not set - copy .env.example to .env")
        options["storageBucket"] = FIREBASE_STORAGE_BUCKET
    return options
