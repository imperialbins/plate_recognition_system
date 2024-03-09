from flask import Flask, render_template, url_for
from flask_socketio import SocketIO
import threading
import time
import subprocess
from google.cloud import vision
import os

# Set your Google Cloud credentials
# Make sure the path is correct and accessible
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/pi/plate_recognition_system/gcp-key.json'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

def capture_image(image_path="static/latest_image.jpg"):
    """Capture an image using libcamera-still and save it."""
    try:
        subprocess.run(["libcamera-still", "-o", image_path, "--timeout", "2000"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error capturing image: {e}")

def process_image_with_google_vision(image_path="static/latest_image.jpg"):
    """Process the captured image with Google Cloud Vision API to recognize text."""
    client = vision.ImageAnnotatorClient()
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    if texts:
        return texts[0].description.strip()
    else:
        return "No plate detected"

def capture_and_process_images():
    while True:
        capture_image()
        plate_number = process_image_with_google_vision()
        print(f"Detected Plate Number: {plate_number}")
        socketio.emit('new_plate_number', {'plate': plate_number})
        time.sleep(2)  # Refresh every 2 seconds

if __name__ == '__main__':
    t = threading.Thread(target=capture_and_process_images)
    t.daemon = True  # Daemonize thread
    t.start()
    socketio.run(app, host='0.0.0.0', debug=True)
