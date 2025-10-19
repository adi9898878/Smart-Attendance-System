import cv2
import face_recognition
import os
import numpy as np
import csv
from datetime import datetime

# ----------------------------
# Load known faces
# ----------------------------
known_encodings = []
known_names = []

known_folder = r"face_test/known"
for filename in os.listdir(known_folder):
    if filename.endswith((".jpg", ".jpeg", ".png")):
        image_path = os.path.join(known_folder, filename)
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)
        if encoding:
            known_encodings.append(encoding[0])
            known_names.append(os.path.splitext(filename)[0].capitalize())

# ----------------------------
# Attendance CSV setup
# ----------------------------
attendance_file = "attendance.csv"
# If file doesn't exist, create and add header
if not os.path.exists(attendance_file):
    with open(attendance_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Date", "Time"])

# Keep track of who has already been marked
marked_names = set()

# ----------------------------
# Open laptop camera
# ----------------------------
video_capture = cv2.VideoCapture(0)

if not video_capture.isOpened():
    print("❌ Cannot open camera")
    exit()

print("🎥 Camera started. Press 'q' to quit.")

while True:
    ret, frame = video_capture.read()
    if not ret:
        print("❌ Failed to grab frame")
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect faces
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.65)
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)

        if True in matches:
            best_match_index = np.argmin(face_distances)
            name = known_names[best_match_index]
            label = f"Recognized ✅ ({name})"
            color = (0, 255, 0)

            # Mark attendance if not already marked
            if name not in marked_names:
                now = datetime.now()
                date = now.strftime("%Y-%m-%d")
                time = now.strftime("%H:%M:%S")
                with open(attendance_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([name, date, time])
                marked_names.add(name)
                print(f"📝 Attendance marked for {name} at {time}")
        else:
            label = "Unknown ❌"
            color = (0, 0, 255)

        # Draw rectangle and label
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    # Show live camera feed
    cv2.imshow("Face Recognition & Attendance", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
