# import cv2
# import os
# import face_recognition
#
# # Create upload folder if not exists
# upload_folder = "images"
# os.makedirs(upload_folder, exist_ok=True)
#
# # Initialize webcam
# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#
# # Ask user for details
# index = input("Enter your index number: ")
# name = input("Enter your name: ")
#
# # Capture three front-face images
# captured_images = []
#
# for i in range(1, 4):  # Capture three images
#     input(f"Press Enter to capture front image {i}...")
#     ret, frame = cap.read()
#
#     if ret:
#         # Convert frame to RGB (face_recognition expects RGB images)
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#
#         # Detect face locations
#         face_locations = face_recognition.face_locations(rgb_frame)
#
#         if face_locations:
#             top, right, bottom, left = face_locations[0]  # Take the first detected face
#
#             # Crop the face
#             face_crop = frame[top:bottom, left:right]
#
#             # Save the cropped face
#             filename = f"{upload_folder}/{index}_{name}_front_{i}.jpg"
#             cv2.imwrite(filename, face_crop)
#             captured_images.append(filename)
#             print(f"Saved: {filename}")
#         else:
#             print("No face detected, try again!")
#
# # Release the camera
# cap.release()
# cv2.destroyAllWindows()
#
# print("Three front images captured successfully!")



from flask import Flask, render_template, request, jsonify
import cv2
import os
import face_recognition

app = Flask(__name__)

UPLOAD_FOLDER = "images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_camera():
    return cv2.VideoCapture(0, cv2.CAP_DSHOW)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/capture", methods=["POST"])
def capture():
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
            filename = f"{UPLOAD_FOLDER}/{index}_{name}_front_{i}.jpg"
            cv2.imwrite(filename, face_crop)
            captured_images.append(filename)
        else:
            cap.release()
            return jsonify({"error": f"No face detected in image {i}, try again!"})

    cap.release()
    return jsonify({"message": "Images captured successfully!", "files": captured_images})

@app.route("/shutdown")
def shutdown():
    return "Camera released!"

if __name__ == "__main__":
    app.run(debug=True)


