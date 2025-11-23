# main.py
import cv2
import mediapipe as mp
import time
import os
import threading
import queue
import numpy as np
from datetime import datetime
from playsound import playsound
from utils import (
    eye_aspect_ratio,
    mouth_aspect_ratio,
    log_event,
    get_current_location,
    upload_image_to_cloudinary,
    send_whatsapp_alert
)
import cloudinary  

DROWSY_THRESHOLD_EAR = 0.25
YAWN_THRESHOLD_MAR = 0.6
DROWSY_TIME_LIMIT = 4       
ALARM_INTERVAL = 20          


mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
MOUTH_INDICES = [13, 14, 78, 308]


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Cannot open webcam")

last_alert_time = 0
drowsy_start = None
alert_triggered = False
alarm_flag = False  

screenshot_q = queue.Queue()


def screenshot_worker():
    while True:
        frame, timestamp = screenshot_q.get()
        try:
            os.makedirs("alert", exist_ok=True)
            path = os.path.join("alert", f"screenshot_{timestamp}.jpg")

        
            _, enc = cv2.imencode(".jpg", frame)
            with open(path, "wb") as f:
                f.write(enc.tobytes())
            print("Saved screenshot:", path)

            img_url = None
            try:
                img_url = upload_image_to_cloudinary(path)
            except Exception as e:
                print("Upload error:", e)

            loc = get_current_location()
            loc_msg = ""
            if loc:
                loc_msg = f"\n📍 Location: {loc.get('city','')}, {loc.get('region','')}, {loc.get('country','')}\n🌐 {loc.get('map_url')}"
            time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"⚠️ DRIVER DROWSINESS ALERT\nTime: {time_str}{loc_msg}"

            send_whatsapp_alert(message, image_url=img_url)
        except Exception as e:
            print("Screenshot worker exception:", e)
        finally:
            screenshot_q.task_done()

threading.Thread(target=screenshot_worker, daemon=True).start()


def alarm_loop():
    while True:
        if alarm_flag:
            try:
                playsound("alert.wav")
            except Exception:
                pass
        else:
            time.sleep(0.1)


threading.Thread(target=alarm_loop, daemon=True).start()


try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Frame not read. Exiting.")
            break

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if results.multi_face_landmarks:
            
            landmarks = results.multi_face_landmarks[0].landmark
            pts = [(int(p.x * w), int(p.y * h)) for p in landmarks]

            ear = eye_aspect_ratio(pts, LEFT_EYE, RIGHT_EYE)
            mar = mouth_aspect_ratio(pts, MOUTH_INDICES)

            # Display EAR/MAR
            cv2.putText(frame, f"EAR: {ear:.2f}", (10, h - 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"MAR: {mar:.2f}", (10, h - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            if ear < DROWSY_THRESHOLD_EAR:
                if drowsy_start is None:
                    drowsy_start = time.time()
                    alert_triggered = False

                elapsed = time.time() - drowsy_start
                cv2.putText(frame, f"😴 DROWSY ({elapsed:.1f}s)", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 3)

                if elapsed >= DROWSY_TIME_LIMIT and not alert_triggered:
                    # Mark alarm flag ON
                    alarm_flag = True

                    
                    ts = time.strftime("%Y%m%d_%H%M%S")
                    screenshot_q.put((frame.copy(), ts))

                    # log
                    log_event("ALERT: DROWSY", ear, mar)
                    alert_triggered = True
                    last_alert_time = time.time()
            else:
                
                drowsy_start = None
                if alert_triggered:
                    alert_triggered = False
                if alarm_flag:
                    alarm_flag = False
              
                cv2.putText(frame, "🙂 AWAKE", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 3)

            
            if mar > YAWN_THRESHOLD_MAR:
                cv2.putText(frame, "🫢 YAWNING", (10, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 128, 0), 3)

        else:
            
            drowsy_start = None
            if alarm_flag:
                alarm_flag = False

        cv2.imshow("Driver Drowsiness Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except KeyboardInterrupt:
    pass
finally:
    cap.release()
    cv2.destroyAllWindows()
