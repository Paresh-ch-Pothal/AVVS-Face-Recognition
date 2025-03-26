# import cv2
# import face_recognition
# import threading
# import os
#
# # Load and encode multiple reference images
# reference_encodings = []
#
# image_folder = "images"  # Folder containing images
# for file in os.listdir(image_folder):
#     if file.endswith(".jpg") or file.endswith(".png"):
#         image_path = os.path.join(image_folder, file)
#         image = face_recognition.load_image_file(image_path)
#         encodings = face_recognition.face_encodings(image)
#
#         if encodings:  # Ensure the image contains a face
#             reference_encodings.append(encodings[0])
#
# if not reference_encodings:
#     raise ValueError("No faces detected in any reference image!")
#
# # Initialize webcam
# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#
# face_match = False
# counter = 0
#
# def check_face(frame):
#     global face_match
#     try:
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
#
#         for encoding in face_encodings:
#             matches = face_recognition.compare_faces(reference_encodings, encoding, tolerance=0.4)
#             face_match = any(matches)  # If any image matches, set face_match to True
#
#     except Exception as e:
#         face_match = False
#
# while True:
#     ret, frame = cap.read()
#     if ret:
#         if counter % 30 == 0:
#             threading.Thread(target=check_face, args=(frame.copy(),)).start()
#         counter += 1
#
#         text = "MATCH!" if face_match else "NO MATCH!"
#         color = (0, 255, 0) if face_match else (0, 0, 255)
#
#         cv2.putText(frame, text, (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 3)
#         cv2.imshow("Video", frame)
#
#         if face_match:  # Quit camera if a match is found
#             print("You are Verified")
#             break
#
#     key = cv2.waitKey(1)
#     if key == ord("q"):
#         break
#
# cap.release()
# cv2.destroyAllWindows()




# this is new one
#
# import cv2
# import face_recognition
# import threading
# import os
# import re
# import json
#
#
# with open("voter_data.json", "r") as file:
#     VOTER_DATA = json.load(file)
#
# # Load and encode multiple reference images
# reference_encodings = {}
# image_folder = "images"  # Folder containing images
#
# for file in os.listdir(image_folder):
#     if file.endswith(".jpg") or file.endswith(".png"):
#         image_path = os.path.join(image_folder, file)
#         image = face_recognition.load_image_file(image_path)
#         encodings = face_recognition.face_encodings(image)
#
#         if encodings:  # Ensure the image contains a face
#             reference_encodings[file] = encodings[0]  # Store with filename as key
#
# if not reference_encodings:
#     raise ValueError("No faces detected in any reference image!")
#
# # Initialize webcam
# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#
# face_match = False
# matched_image = None
# counter = 0
#
# def check_face(frame):
#     global face_match, matched_image
#     try:
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
#
#         for encoding in face_encodings:
#             for filename, ref_encoding in reference_encodings.items():
#                 match = face_recognition.compare_faces([ref_encoding], encoding, tolerance=0.4)
#                 if match[0]:  # If match is found
#                     face_match = True
#                     matched_image = filename  # Store matched image filename
#                     return
#
#     except Exception as e:
#         face_match = False
#         matched_image = None
#
# while True:
#     ret, frame = cap.read()
#     if ret:
#         if counter % 30 == 0:
#             threading.Thread(target=check_face, args=(frame.copy(),)).start()
#         counter += 1
#
#         text = "MATCH!" if face_match else "NO MATCH!"
#         color = (0, 255, 0) if face_match else (0, 0, 255)
#
#         cv2.putText(frame, text, (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 3)
#         cv2.imshow("Video", frame)
#
#         if face_match:  # Quit camera if a match is found
#             st=input("Enter Full Name Mentioned In The Adhar Card: ")
#             match = re.match(r"(\d+)_", matched_image)
#             extracted_number = int(match.group(1))
#             if VOTER_DATA[extracted_number - 1]["name"].strip().lower() == st.strip().lower():
#                 print(f"You are Verified")
#             break
#
#     key = cv2.waitKey(1)
#     if key == ord("q"):
#         break
#
# cap.release()
# cv2.destroyAllWindows()



# this is the flask part
from flask import Flask, render_template, request, jsonify
import os
import json
import face_recognition
import re
import cv2
import numpy as np

app = Flask(__name__)

UPLOAD_FOLDER = "images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load voter data
with open("voter_data.json", "r") as file:
    VOTER_DATA = json.load(file)

# Load and encode multiple reference images
reference_encodings = {}
image_folder = "images"

for file in os.listdir(image_folder):
    if file.endswith(".jpg") or file.endswith(".png"):
        image_path = os.path.join(image_folder, file)
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)

        if encodings:
            reference_encodings[file] = encodings[0]

if not reference_encodings:
    raise ValueError("No faces detected in any reference image!")

@app.route("/")
def index():
    return render_template("index2.html")

@app.route("/capture", methods=["POST"])
def capture():
    if "image" not in request.files:
        return jsonify({"error": "No image provided!"}), 400

    image_file = request.files["image"]
    image_np = np.frombuffer(image_file.read(), np.uint8)
    frame = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

    # Convert to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect faces
    face_locations = face_recognition.face_locations(rgb_frame, model="hog")
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    if not face_encodings:
        return jsonify({"error": "No face detected! Ensure good lighting and positioning."})

    # Match face
    matched_image = None
    for encoding in face_encodings:
        for filename, ref_encoding in reference_encodings.items():
            match = face_recognition.compare_faces([ref_encoding], encoding, tolerance=0.4)
            if match[0]:
                matched_image = filename
                break

    if matched_image:
        return jsonify({"match": True, "matched_image": matched_image})
    else:
        return jsonify({"match": False, "message": "Face detected, but no match found!"})

@app.route("/verify", methods=["POST"])
def verify():
    data = request.json
    user_name = data.get("name")
    matched_image = data.get("matched_image")

    if not user_name or not matched_image:
        return jsonify({"error": "Name and matched image are required"}), 400

    match = re.match(r"(\d+)_", matched_image)
    if match:
        extracted_number = int(match.group(1))
        if VOTER_DATA[extracted_number - 1]["name"].strip().lower() == user_name.strip().lower():
            return jsonify({"message": "✅ You are successfully verified!"})
        else:
            return jsonify({"error": "❌ Verification failed! Incorrect name."})
    else:
        return jsonify({"error": "Invalid image format"}), 400

if __name__ == "__main__":
    app.run(debug=True)

