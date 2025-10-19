"""
Smart Attendance System (Backend Simulation)
- Blink-based liveness check
- Attendance marked after 3 blinks
- Optimized for speed (resized frames)
- Stored in CSV
- Only recognizes known faces (distance threshold applied)
"""

import os
import csv
import cv2
import hashlib
import face_recognition
import numpy as np
from datetime import datetime
import getpass

# ----------------------------
# CONFIG & PATHS
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Script folder
KNOWN_FOLDER = os.path.join(BASE_DIR, "face_test/known")
USERS_FILE = os.path.join(BASE_DIR, "users.csv")
ATTENDANCE_FILE = os.path.join(BASE_DIR, "attendance.csv")

BLINK_THRESHOLD = 0.25        # EAR below this is considered a blink
REQUIRED_BLINKS = 3           # Blinks required to mark attendance
FRAME_SCALE = 0.5             # Resize frame to 50% for faster processing
FACE_DISTANCE_THRESHOLD = 0.5 # Max distance for recognition

# ----------------------------
# SECURITY FUNCTIONS
# ----------------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_default_user_if_missing():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["admin", hash_password("admin123")])
        print(f"[SETUP] Created default user -> {USERS_FILE}")

def load_users():
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    users[row[0]] = row[1]
    print(f"[DEBUG] Loaded users: {list(users.keys())}")
    return users

def login_prompt():
    users = load_users()
    while True:
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")
        if username in users and users[username] == hash_password(password):
            print(f"[SECURITY] Login successful. Welcome {username}!")
            return True
        else:
            print("[SECURITY] Login failed! Try again.")

# ----------------------------
# ATTENDANCE CSV
# ----------------------------
def ensure_attendance_file():
    if not os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE,"w",newline="") as f:
            writer=csv.writer(f)
            writer.writerow(["Name","Date","Time","Status"])
        print(f"[SETUP] Created attendance file -> {ATTENDANCE_FILE}")

def mark_attendance(name):
    now = datetime.now()
    with open(ATTENDANCE_FILE,"a",newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), "Present"])
    print(f"[ATTENDANCE] Marked {name} present at {now.strftime('%H:%M:%S')}")

# ----------------------------
# FACE UTILITIES
# ----------------------------
def load_known_faces(folder=KNOWN_FOLDER):
    encs,names=[],[]
    if not os.path.exists(folder):
        raise FileNotFoundError(f"Known folder not found: {folder}")
    for fname in os.listdir(folder):
        if fname.lower().endswith((".jpg",".jpeg",".png")):
            path=os.path.join(folder,fname)
            img=face_recognition.load_image_file(path)
            enc=face_recognition.face_encodings(img)
            if enc:
                encs.append(enc[0])
                names.append(os.path.splitext(fname)[0].capitalize())
            else:
                print(f"[WARN] No face encoding in {fname}, skipping.")
    return encs,names

def eye_aspect_ratio(eye_points):
    A = np.linalg.norm(np.array(eye_points[1]) - np.array(eye_points[5]))
    B = np.linalg.norm(np.array(eye_points[2]) - np.array(eye_points[4]))
    C = np.linalg.norm(np.array(eye_points[0]) - np.array(eye_points[3]))
    return (A + B) / (2.0 * C) if C != 0 else 1.0

# ----------------------------
# LIVENESS (BLINK) CHECK
# ----------------------------
_blink_history = {}  # Track blinks per student

def check_blink_liveness(face_name, face_landmarks):
    blink_detected = False
    if face_landmarks:
        lm = face_landmarks[0]
        left_eye = lm.get("left_eye", [])
        right_eye = lm.get("right_eye", [])
        if left_eye and right_eye and len(left_eye) >= 6 and len(right_eye) >= 6:
            ear = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0
            if ear < BLINK_THRESHOLD:
                blink_detected = True

    if face_name not in _blink_history:
        _blink_history[face_name] = 0

    if blink_detected:
        _blink_history[face_name] += 1

    return _blink_history[face_name] >= REQUIRED_BLINKS

# ----------------------------
# MAIN LOOP
# ----------------------------
def main():
    print("Users CSV path:", USERS_FILE)
    print("Attendance CSV path:", ATTENDANCE_FILE)

    create_default_user_if_missing()
    login_prompt()

    known_encodings, known_names = load_known_faces()
    if not known_encodings:
        print("[ERROR] No known faces loaded. Exiting.")
        return
    print(f"[INFO] Loaded faces: {known_names}")

    ensure_attendance_file()
    marked_names = set()

    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("[ERROR] Cannot open camera.")
        return
    print("[INFO] Camera opened. Press 'q' to quit.")

    try:
        while True:
            ret, frame = video_capture.read()
            if not ret: break

            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (0,0), fx=FRAME_SCALE, fy=FRAME_SCALE)
            rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_small)
            face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                name = "Unknown"
                color = (0,0,255)

                if known_encodings:
                    face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                    best_idx = np.argmin(face_distances)
                    if face_distances[best_idx] < FACE_DISTANCE_THRESHOLD:
                        name = known_names[best_idx]
                        landmarks = face_recognition.face_landmarks(rgb_small[top:bottom, left:right])
                        blink_passed = check_blink_liveness(name, landmarks)

                        # ----------------------------
                        # For testing without blinking, uncomment next line:
                        # blink_passed = True
                        # ----------------------------

                        if blink_passed and name not in marked_names:
                            mark_attendance(name)
                            marked_names.add(name)
                            color = (0,255,0)

                # Draw rectangle
                top_s, right_s, bottom_s, left_s = [int(x / FRAME_SCALE) for x in (top, right, bottom, left)]
                cv2.rectangle(frame, (left_s, top_s), (right_s, bottom_s), color, 2)
                cv2.putText(frame, name, (left_s, top_s-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            cv2.imshow("Smart Attendance System", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break

    finally:
        video_capture.release()
        cv2.destroyAllWindows()
        print("[INFO] Exiting. Attendance saved to", ATTENDANCE_FILE)

if __name__=="__main__":
    main()
