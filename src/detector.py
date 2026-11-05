import base64
import hashlib
import io
import os
import sys
import threading

import cv2
import numpy as np
import tensorflow as tf
from PIL import ExifTags, Image

# ===========================
# CONFIG
# ===========================
# Works from source and from a PyInstaller bundle
BASE_DIR = getattr(sys, "_MEIPASS", None) and os.path.join(sys._MEIPASS, "src") or os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "oak_wilt_3.h5")
STATIC_DIR = os.path.join(BASE_DIR, "static")

IMG_SIZE = 256
THUMB_WIDTH = 600
VIEW_WIDTH = 2400  # enlarged viewer: sharp enough to zoom, small enough to pass to the UI quickly

_model = None
model_lock = threading.Lock()


def get_model():
    global _model
    with model_lock:
        if _model is None:
            _model = tf.keras.models.load_model(MODEL_PATH)
        return _model


# ===========================
# HELPER FUNCTIONS
# ===========================
def classify_prediction(confidence):
    confidence = confidence * 100
    if confidence > 99.5:
        return "THIS PICTURE HAS OAK WILT"
    elif 90 < confidence <= 99.5:
        return "HIGH CHANCE OF OAK WILT"
    elif 70 < confidence <= 90:
        return "CHANGES OF COLORS ON TREE LEAVES"
    else:
        return "Not an Oak Wilt"


def convert_to_degrees(value):
    d, m, s = value
    return float(d) + (float(m) / 60.0) + (float(s) / 3600.0)


def get_gps_data(img_bytes):
    try:
        img = Image.open(io.BytesIO(img_bytes))
        exif_data = img._getexif()
        if not exif_data:
            return None
        for tag, value in exif_data.items():
            decoded = ExifTags.TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = ExifTags.GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]
                if "GPSLatitude" in gps_data and "GPSLongitude" in gps_data:
                    lat = convert_to_degrees(gps_data["GPSLatitude"])
                    lon = convert_to_degrees(gps_data["GPSLongitude"])
                    if gps_data.get("GPSLatitudeRef") != "N":
                        lat = -lat
                    if gps_data.get("GPSLongitudeRef") != "E":
                        lon = -lon
                    return [lat, lon]
    except Exception:
        pass
    return None


def process_image(img_bytes):
    img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid image")

    # Small JPEG thumbnail for display; the full-size image is never kept
    thumbnail = jpeg_data_url(img, THUMB_WIDTH, 85)

    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE)).astype(np.float32) / 255.0
    model = get_model()
    with model_lock:
        prediction = float(model(np.expand_dims(img, axis=0), training=False)[0][0])

    return {
        "classification": classify_prediction(prediction),
        "confidence": prediction * 100,
        "gps": get_gps_data(img_bytes),
        "thumbnail": thumbnail,
    }


def jpeg_data_url(img, max_width, quality):
    """Downscale `img` to at most `max_width` wide and return it as a JPEG data URL."""
    h, w = img.shape[:2]
    if w > max_width:
        img = cv2.resize(img, (max_width, int(h * max_width / w)), interpolation=cv2.INTER_AREA)
    _, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return "data:image/jpeg;base64," + base64.b64encode(buf.tobytes()).decode("ascii")


def view_image(path):
    """Larger copy of the image on disk for the zoomable viewer."""
    # Read bytes ourselves: cv2.imread can't open non-ASCII paths on Windows
    with open(path, "rb") as f:
        img = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid image")
    return jpeg_data_url(img, VIEW_WIDTH, 90)


def file_id(img_bytes):
    return hashlib.md5(img_bytes).hexdigest()
