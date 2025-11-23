# 🚗 Driver Drowsiness & Yawning Detection System

A **real-time Driver Drowsiness and Yawning Detection System** built using **OpenCV**, **MediaPipe**, and **Python**.  
The system continuously monitors the driver’s **eyes and mouth** using a webcam to detect **fatigue or yawning**.  
If drowsiness is detected, it **plays an alarm**, **captures a screenshot**, and optionally **sends a WhatsApp alert with the driver’s location and image** via **Twilio** and **Cloudinary**.

---

## 🧠 Features

✅ Real-time face & eye tracking using MediaPipe  
✅ Detects **eye closure (EAR)** and **yawning (MAR)**  
✅ Plays an **alarm** when drowsiness or yawning is detected  
✅ Automatically captures **screenshots** inside `/alert/`  
✅ Sends **WhatsApp alert with location + screenshot**  
✅ Displays **live detection overlay** on the video feed  
✅ Fully configurable detection sensitivity  
✅ Compatible with **Windows, macOS, and Linux**

---

## 🧰 1️⃣ Prerequisites

| Tool | Version | Notes |
|------|----------|-------|
| **Python** | 3.8 → 3.11 | ✅ Recommended: 3.10.11 |
| **pip** | Latest | `python -m pip install --upgrade pip` |
| **Microsoft C++ Build Tools** | Required | Needed for OpenCV/MediaPipe on Windows |
| **Webcam** | Any | Built-in or USB camera |
| **OS** | Windows 10/11, macOS, Linux | Fully tested ✅ |

---

## ⚙️ 2️⃣ Install Python

Download **Python 3.10.x (64-bit)** from 👉 [python.org/downloads](https://www.python.org/downloads/)

During installation:
- ✅ Check **“Add Python to PATH”**
- ✅ Check **“Install for all users”**

Verify installation:

```bash
python --version
Expected output:

nginx
Copy code
Python 3.10.11
🧱 3️⃣ Create & Activate Virtual Environment
Navigate to your project directory:

bash
Copy code
cd C:\Users\<yourname>\Downloads\drowsiness_project
Create a new environment:

bash
Copy code
python -m venv venv310
Activate the environment:

Windows:

bash
Copy code
venv310\Scripts\activate


You should now see (venv310) appear in your terminal.

📦 4️⃣ Install Dependencies
🔹 Option 1 — From requirements.txt
bash
Copy code
pip install --upgrade pip
pip install -r requirements.txt
🔹 Option 2 — Manual installation
bash
Copy code
pip install opencv-python==4.12.0.88
pip install mediapipe==0.10.9
pip install numpy==2.2.6
pip install playsound==1.2.2
pip install python-dotenv==1.0.1
pip install pygame==2.6.1
pip install twilio==9.2.3
pip install geopy geocoder cloudinary requests
pip install psutil  {for task (proccess)termination}

🧪 5️⃣ Verify Installation
bash
Copy code
python -c "import cv2, mediapipe, numpy, pygame; print('✅ All dependencies working!')"
Expected output:

css
Copy code
✅ All dependencies working!
🧩 6️⃣ Project Structure
bash
Copy code
drowsiness_project/
│
├── alert/                      # Stores alarm & screenshots
│   ├── alert.wav               # Alarm sound file
│   └── screenshot_*.jpg        # Auto-captured images
│
├── driver_drowsiness.py        # Main detection script
├── utils.py                    # EAR, MAR, Twilio, Cloudinary, Location logic
├── ui_app.py                   # Optional GUI launcher
├── .env                        # Twilio + Cloudinary credentials
├── requirements.txt            # Dependencies list
├── log.txt                     # Detection event log
└── README.md                   # This file
🔑 7️⃣ Configure Environment Variables
Create a file named .env in your project root with the following content:

env
Copy code
# Twilio WhatsApp Configuration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_WHATSAPP_TO=whatsapp:+91XXXXXXXXXX

# Optional custom message
ALERT_MESSAGE=Driver is feeling drowsy! Immediate attention required.

# Cloudinary Configuration
CLOUD_NAME=your_cloud_name
CLOUD_API_KEY=your_cloud_api_key
CLOUD_API_SECRET=your_cloud_api_secret
🔹 How to Get Twilio Credentials
Go to https://www.twilio.com/console

Verify your phone number for WhatsApp sandbox.

Copy Account SID, Auth Token, and sandbox WhatsApp number.

Add them to .env.

🔹 How to Get Cloudinary Keys
Go to https://cloudinary.com/console

Create a free account.

Copy your:

Cloud Name

API Key

API Secret

Add them to .env.

📍 8️⃣ Accurate Location Detection Setup
The project uses multiple fallback APIs for high accuracy:

Priority	API	Description
1️⃣	geopy + geocoder	Detects GPS/IP-based approximate coordinates
2️⃣	ipapi.co	City-level precision (recommended)
3️⃣	ipinfo.io	Final fallback if others fail

🌍 Note: Accuracy depends on your Internet Provider (IP-based geolocation is typically 90–95% accurate).

🚀 9️⃣ Run the Project
Activate your environment:

bash
Copy code
venv310\Scripts\activate
Run the detection system:

bash
Copy code
python ui_app.py
🎥 A webcam window will open automatically.

Event	Description	Action
👁️ Eyes closed (EAR < threshold)	Drowsiness detected	🔴 Red warning + Alarm
🫢 Yawning (MAR > threshold)	Fatigue detected	🔔 Alarm plays
💤 Unresponsive > 4s	Critical alert	📸 Screenshot + WhatsApp message with location & image

Press Q anytime to quit safely.

🔊 🔟 Customize Detection Sensitivity
Open driver_drowsiness.py and adjust these parameters:

Variable	Description	Default
DROWSY_THRESHOLD_EAR	Eye closure sensitivity	0.25
YAWN_THRESHOLD_MAR	Yawn sensitivity	0.6
DROWSY_TIME_LIMIT	Seconds before triggering alert	4
ALARM_INTERVAL	Minimum time between alerts (sec)	15

To change alarm sound:
👉 Replace alert.wav inside /alert with your preferred audio file.

📁 11️⃣ Log & Screenshot Output
Every event is logged inside log.txt:

yaml
Copy code
[2025-10-31 20:47:54] ALERT: DROWSY | EAR=0.221 | MAR=0.000
Screenshots are automatically saved to:

bash
Copy code
alert/screenshot_YYYYMMDD_HHMMSS.jpg
⚙️ 12️⃣ Troubleshooting
Issue	Cause	Fix
ModuleNotFoundError: cv2	OpenCV missing	pip install opencv-python
mediapipe install fails	Python 3.12 not supported	Use Python 3.10
No sound/alarm	Missing alert.wav	Add/replace file
Webcam not opening	Camera blocked	Allow camera access
No face detection	Poor lighting	Increase ambient light
WhatsApp alert not sending	Invalid Twilio SID/Auth	Recheck .env
Cloudinary upload failed	Invalid key or secret	Recheck .env
Location missing	Network or API blocked	Retry on stable Internet

💬 Author
👨‍💻 Kritika Bunkar
📍 Satna, India
🌐 Inspired by next-gen road safety innovation

🧩 Optional: Launch with GUI
If your project includes a GUI interface:

bash
Copy code
python ui_app.py
This opens a Start/Stop control panel for easy use.

❤️ Stay Safe — Smart Driving with AI Assistance
yaml
Copy code

---

Would you like me to also create the corresponding `requirements.txt` file (✅ verified exact versions) for this updated setup?






venv310\Scripts\activate
python ui_app.py