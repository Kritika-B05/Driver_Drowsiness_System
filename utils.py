import os
import time
import datetime
import csv
import threading
import requests
import numpy as np
import geocoder
import cloudinary
import cloudinary.uploader
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

#twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")
TWILIO_WHATSAPP_TO = os.getenv("TWILIO_WHATSAPP_TO")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Cloudinary
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")
CLOUD_NAME = os.getenv("CLOUD_NAME")
CLOUD_API_KEY = os.getenv("CLOUD_API_KEY")
CLOUD_API_SECRET = os.getenv("CLOUD_API_SECRET")

if CLOUDINARY_URL:
    cloudinary.config(cloudinary_url=CLOUDINARY_URL, secure=True)
else:
    cloudinary.config(
        cloud_name=CLOUD_NAME,
        api_key=CLOUD_API_KEY,
        api_secret=CLOUD_API_SECRET,
        secure=True
    )

#EAR & MAR 
def eye_aspect_ratio(landmarks, left_idxs, right_idxs):
    def euclid(a, b): return np.linalg.norm(np.array(a) - np.array(b))
    left = [landmarks[i] for i in left_idxs]
    right = [landmarks[i] for i in right_idxs]
    left_ear = (euclid(left[1], left[5]) + euclid(left[2], left[4])) / (2.0 * euclid(left[0], left[3]) + 1e-8)
    right_ear = (euclid(right[1], right[5]) + euclid(right[2], right[4])) / (2.0 * euclid(right[0], right[3]) + 1e-8)
    return (left_ear + right_ear) / 2.0

def mouth_aspect_ratio(landmarks, mouth_idxs):
    def euclid(a, b): return np.linalg.norm(np.array(a) - np.array(b))
    top, bottom, left, right = [landmarks[i] for i in mouth_idxs]
    return euclid(top, bottom) / (euclid(left, right) + 1e-8)

#Logging
def log_event(event_type, ear, mar):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {event_type} | EAR={ear:.3f}, MAR={mar:.3f}"
    print(line)
    with open("log.txt", "a") as f: f.write(line + "\n")
    if not os.path.exists("data_log.csv"):
        with open("data_log.csv", "w", newline="") as f:
            csv.writer(f).writerow(["Time", "Event", "EAR", "MAR"])
    with open("data_log.csv", "a", newline="") as f:
        csv.writer(f).writerow([ts, event_type, f"{ear:.3f}", f"{mar:.3f}"])

# location
import os
import requests
import geocoder
from geopy.geocoders import Nominatim

def get_current_location():
    """Fetch the most accurate location available."""
    try:
      
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if api_key:
            url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={api_key}"
            response = requests.post(url)
            data = response.json()

            if "location" in data:
                lat = data["location"]["lat"]
                lon = data["location"]["lng"]
                accuracy = data.get("accuracy", 0)

                geolocator = Nominatim(user_agent="drowsy_tracker")
                location = geolocator.reverse(f"{lat}, {lon}", language="en")

                address = location.address if location else "Unknown"
                print(f"✅ Accurate GPS location: {lat}, {lon}")
                return {
                    "latitude": lat,
                    "longitude": lon,
                    "accuracy": accuracy,
                    "address": address
                }

        g = geocoder.ip('me')
        if g.ok:
            lat, lon = g.latlng
            geolocator = Nominatim(user_agent="drowsy_tracker_backup")
            location = geolocator.reverse(f"{lat}, {lon}", language='en')
            address = location.address if location else "Unknown"
            print(f"✅ Approximate IP location: {lat}, {lon}")
            return {
                "latitude": lat,
                "longitude": lon,
                "accuracy": "IP-based",
                "address": address
            }

        print("⚠️ Location detection failed (no method succeeded)")
        return None

    except Exception as e:
        print(f"⚠️ Location detection error: {e}")
        return None


#Cloudinary Upload 
def upload_image_to_cloudinary(path):
    try:
        res = cloudinary.uploader.upload(path)
        url = res.get("secure_url")
        print("✅ Uploaded to Cloudinary:", url)
        return url
    except Exception as e:
        print("❌ Cloudinary upload failed:", e)
        return None

#  WhatsApp Alert 
def send_whatsapp_alert(message, image_url=None):
    try:
        msg = client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_FROM,
            to=TWILIO_WHATSAPP_TO,
            media_url=[image_url] if image_url else None
        )
        print("✅ WhatsApp alert sent:", msg.sid)
        return True
    except Exception as e:
        print("❌ WhatsApp send failed:", e)
        return False

#Capture + Send 
def handle_alert_screenshot(frame_path):
    """Upload screenshot + send alert without freezing video"""
    def async_task():
        image_url = upload_image_to_cloudinary(frame_path)
        location = get_current_location()
        msg = (
            f"⚠️ Drowsiness Detected!\n\n"
            f"📍 Location: {location['city']}, {location['region']}, {location['country']}\n"
            f"🌐 Map: {location['map_url']}\n\n"
            f"🕒 Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        send_whatsapp_alert(msg, image_url)
    threading.Thread(target=async_task, daemon=True).start()
