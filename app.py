import os
import json
import cv2
import numpy as np
import face_recognition
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

UPLOAD_FOLDER = "images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load voter data
with open("voter_data.json", "r") as file:
    VOTER_DATA = json.load(file)

# Dictionary to store reference encodings
reference_encodings = {}
image_folder = "images"


def load_reference_encodings():
    """Loads and encodes reference images for verification."""
    for file in os.listdir(image_folder):
        if file.endswith(".jpg") or file.endswith(".png"):
            image_path = os.path.join(image_folder, file)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                reference_encodings[file] = encodings[0]
                print(f"✅ Loaded encoding for: {file}")
            else:
                print(f"⚠️ Warning: No face detected in {file}")

    if not reference_encodings:
        raise ValueError("❌ No faces detected in any reference image!")


def get_camera():
    """Opens webcam using OpenCV."""
    return cv2.VideoCapture(0, cv2.CAP_DSHOW)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/capture", methods=["GET", "POST"])
def capture():
    """Captures an image for registration."""
    if request.method == "GET":
        return render_template("capture.html")

    index = request.form.get("index")
    name = request.form.get("name")

    if not index or not name:
        return jsonify({"error": "Index and Name are required"}), 400

    cap = get_camera()
    captured_images = []

    for i in range(1, 4):  # Capture three images
        ret, frame = cap.read()
        if not ret:
            cap.release()
            return jsonify({"error": "Failed to capture image from webcam!"})

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        if face_locations:
            top, right, bottom, left = face_locations[0]
            face_crop = frame[top:bottom, left:right]
            filename = f"{index}_{name}_front_{i}.jpg"
            full_path = os.path.join(UPLOAD_FOLDER, filename)
            cv2.imwrite(full_path, face_crop)
            captured_images.append(filename)
        else:
            cap.release()
            return jsonify({"error": f"No face detected in image {i}, try again!"})

    cap.release()
    return render_template("verify.html", name=name, index=index)


@app.route("/verify_live", methods=["POST"])
def verify_live():
    """Capture an image from the webcam and verify it."""
    global reference_encodings  # Ensure we use the global reference_encodings

    data = request.json
    user_name = data.get("name")
    index = data.get("index")

    if not user_name or not index:
        return jsonify({"error": "Name and Index are required"}), 400

    # Check if the name matches the index in voter data
    try:
        voter_info = VOTER_DATA[int(index) - 1]
        if voter_info["name"].strip().lower() != user_name.strip().lower():
            return jsonify({"match": False, "error": "Name does not match records"})
    except (ValueError, IndexError):
        return jsonify({"match": False, "error": "Invalid voter index"})

    # Reload encodings every time before verification
    reference_encodings.clear()
    load_reference_encodings()  # Reload latest images

    # Open webcam using OpenCV
    cap = get_camera()
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return jsonify({"match": False, "error": "Failed to capture image"})

    # Convert frame to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect faces in the frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    if not face_encodings:
        return jsonify({"match": False, "error": "No face detected"})

    # Try to match the face with reference images
    matched = False
    for encoding in face_encodings:
        for filename, ref_encoding in reference_encodings.items():
            # Check if the filename matches the current index
            if filename.startswith(f"{index}_"):
                match = face_recognition.compare_faces([ref_encoding], encoding, tolerance=0.4)
                if match[0]:
                    matched = True
                    break
        if matched:
            break

    if matched:
        return jsonify({"match": True, "name": user_name})
    else:
        return jsonify({"match": False, "error": "Face does not match our records"})



@app.route("/success")
def success():
    """Displays success message after verification."""
    name = request.args.get("name", "User")
    return render_template("success.html", name=name)



if __name__ == "__main__":
    load_reference_encodings()  # Load encodings before starting the app
    app.run(debug=True)
