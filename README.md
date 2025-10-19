🧠 Smart Attendance System (Simulation)

A fully simulated **Smart Attendance System** that combines **Face Recognition**, Geo-Fencing, and Cybersecurity — all in Python.
No hardware, Raspberry Pi, or external camera setup required — everything runs on your laptop.

---

🚀 Features

🎥 **Face Recognition Simulation** — detects known faces from stored images or video.
👁️ **Liveness Detection** — detects blinks to prevent spoofing (simulated).
📍 **Geo-Fencing** — simulates student location via mock GPS coordinates.
🔒 **Cybersecurity Layer** — password-protected dashboard using Flask and SHA256 hashing.
🧾 **Database Integration** — attendance stored in both CSV and SQLite.
⚠️ **Intrusion Detection** — logs unauthorized login attempts.
🧠 **Fully Offline Simulation** — no hardware dependencies.

---

🗂 Folder Structure

```
smart-attendance-system/
│
├── dataset/                 # Images for face recognition
├── logs/                    # Intrusion logs
│   └── intrusion_log.txt
├── attendance/
│   ├── attendance.db        # SQLite database
│   └── attendance.csv       # CSV attendance record
│
├── main.py                  # Core simulation (Face + Geo + Liveness)
├── app.py                   # Flask dashboard (Cybersecurity layer)
├── requirements.txt          # Dependencies
└── README.md
```

---

⚙️ Setup Instructions

1. Install Python 3.10+**
2. Install Dependencies**

   ```bash
   pip install opencv-python face_recognition flask geopy sqlite3
   ```
3. Run Simulation**

   ```bash
   python main.py
   ```
4. Start Flask Dashboard**

   ```bash
   python app.py
   ```
5. Access Dashboard**

   ```
   http://127.0.0.1:5000
   Username: admin
   Password: securepass123
   ```

---

🔐 Security Features

* SHA256-hashed admin password for secure login
* Intrusion detection logs (`intrusion_log.txt`) for failed login attempts
* Session-based access control in Flask
* Simulated secure database updates on each attendance mark

---

🧰 Simulation Logic

* When a student’s face is detected in the image feed → attendance is marked ✅
* If the simulated GPS location is outside the classroom → warning shown ⚠️
* Only students who blink three times pass the liveness check 👀
* Attendance is saved automatically in both `attendance.db` and `attendance.csv`

---

📈 Future Enhancements

 🔔 Email alerts for repeated failed logins
 ☁️ Cloud backup simulation
 📊 Analytics dashboard (attendance trends)
 🧩 Integration with biometric and IoT devices

---

🏆 Project Highlights

* 100% backend simulation (no hardware required)
* Demonstrates the fusion of AI, Cybersecurity, and IoT concepts
* Perfect for research, academic demonstrations, or prototype submissions

---

