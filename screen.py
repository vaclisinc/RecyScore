import time
import os
import json
import base64
from tkinter import Tk, Button
from picamera2 import Picamera2
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# 設定區
CERT_PATH = os.path.expanduser("~/aws-iot-certs/")
ENDPOINT = "a2drix3z851hyd-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "RaspberryPi_Camera"
TOPIC = "camera/images"
IMAGE_PATH = "/tmp/image.jpg"

ROOT_CA = CERT_PATH + "AmazonRootCA1.pem"
PRIVATE_KEY = CERT_PATH + "b555123197747ec6327a53bf46c85636106f00b514b01e9a7b3fbc96fa730b81-private.pem.key"          # 替換這行
CERT = CERT_PATH + "b555123197747ec6327a53bf46c85636106f00b514b01e9a7b3fbc96fa730b81-certificate.pem.crt"             # 替換這行

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
root = Tk()
root.attributes('-fullscreen', True)  # 全螢幕
btn = Button(root, text="📷 拍照上傳", font=("Arial", 40), command=capture_and_upload)
btn.pack(expand=True, fill='both')
root.mainloop()