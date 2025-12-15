import cv2
import requests
import os
import socket
from datetime import datetime

# Server Config
SERVER_URL = "http://127.0.0.1:5000/api/upload_evidence"
SAVE_DIR = "logs"

def get_device_id():
    # Returns the system hostname as Device ID
    return socket.gethostname()


def get_timestamp():
    #Returns current timestamp in required format
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def log(message):
    #Prints timestamped logs
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

# Main Agent

def capture_image():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    filename = f"evidence_{get_timestamp()}.jpg"
    filepath = os.path.join(SAVE_DIR, filename)

    cam = cv2.VideoCapture(1)

    if not cam.isOpened():
        log("Camera Error: Unable to access webcam")
        return None

    log("Camera Sensor: INITIALIZED (Index 0)")
    ret, frame = cam.read()
    cam.release()

    if not ret:
        log("Capture Status: FAILED")
        return None

    cv2.imwrite(filepath, frame)
    log("Capture Status: SUCCESS")
    log(f"Local Storage: {os.path.abspath(filepath)}")

    return filepath


def upload_image(filepath):
    try:
        files = {"image": open(filepath, "rb")}
        data = {
            "device_id": get_device_id(),
            "timestamp": get_timestamp()
        }

        log("Uploading payload to Server...")
        response = requests.post(SERVER_URL, files=files, data=data)

        log(f"Server Response: {response.status_code}")
    except Exception as e:
        log(f"Upload Failed: {e}")


if __name__ == "__main__":
    log("--- Fortify Agent Started ---")

    image_path = capture_image()
    if image_path:
        upload_image(image_path)