# capture_process.py
import os
from google.cloud import vision
import subprocess
import io

def capture_image():
    image_path = 'current_plate.jpg'
    subprocess.run(['libcamera-still', '-o', image_path], check=True)
    return image_path

def recognize_text(image_path):
    client = vision.ImageAnnotatorClient()

    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if texts:
        return texts[0].description.strip()
    else:
        return "No text found"

def capture_and_process():
    image_path = capture_image()
    plate_text = recognize_text(image_path)
    print(f"Detected plate: {plate_text}")  # For debugging
    return plate_text
