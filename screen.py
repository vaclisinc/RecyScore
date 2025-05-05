import time
import os
import json
import base64
from tkinter import Tk, Button
from picamera2 import Picamera2
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from dotenv import load_dotenv
from threading import Thread

# === 設定區 ===
CERT_PATH = os.path.expanduser("~/aws-iot-certs/")
CLIENT_ID = "RaspberryPi_Camera"
TOPIC = "camera/images"
IMAGE_PATH = "/tmp/image.jpg"

load_dotenv()
ENDPOINT = os.getenv("ENDPOINT")
ROOT_CA = CERT_PATH + os.getenv("ROOT_CA")
PRIVATE_KEY = CERT_PATH + os.getenv("PRIVATE_KEY")
CERT = CERT_PATH + os.getenv("CERT")

# MQTT 初始化
mqtt_client = AWSIoTMQTTClient(CLIENT_ID)
mqtt_client.configureEndpoint(ENDPOINT, 8883)
mqtt_client.configureCredentials(ROOT_CA, PRIVATE_KEY, CERT)
mqtt_client.configureOfflinePublishQueueing(-1)
mqtt_client.configureDrainingFrequency(2)
mqtt_client.configureConnectDisconnectTimeout(10)
mqtt_client.configureMQTTOperationTimeout(5)

print("🔗 Connecting to AWS IoT Core...")
mqtt_client.connect()
print("✅ Connected!")

# 相機初始化
picam2 = Picamera2()
picam2.start()
time.sleep(2)

# 拍照＋上傳邏輯
def capture_and_upload():
    try:
        print("📸 Capturing...")
        picam2.capture_file(IMAGE_PATH)
        with open(IMAGE_PATH, "rb") as f:
            encoded_image = base64.b64encode(f.read()).decode('utf-8')
        payload = {
            "timestamp": int(time.time()),
            "device_id": CLIENT_ID,
            "image_data": encoded_image
        }
        mqtt_client.publish(TOPIC, json.dumps(payload), 1)
        print("✅ Sent!")
    except Exception as e:
        print(f"❌ Error: {e}")

# GUI 觸控介面
def gui_capture():
    def task():
        btn.config(text="上傳中請稍後...", bg="#d5bdaf", state="disabled")
        capture_and_upload()
        btn.config(text="點我拍攝回收物品", bg="#d6ccc2", state="normal")

    Thread(target=task).start()

root = Tk()
root.title("RecyScore 拍照上傳")
root.configure(bg='black')
root.attributes('-fullscreen', True)

btn = Button(
    root,
    text="點我拍攝回收物品",
    font=("Arial", 48),
    bg="#d6ccc2",
    fg="white",
    activebackground="#d5bdaf",
    activeforeground="white",
    command=gui_capture
)
btn.pack(expand=True, fill='both', padx=50, pady=50)

root.mainloop()