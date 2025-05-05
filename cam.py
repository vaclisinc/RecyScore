import time
import os
import json
import base64
import ssl
from picamera2 import Picamera2
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# === 設定區 ===
CERT_PATH = os.path.expanduser("~/aws-iot-certs/")
ENDPOINT = "a2drix3z851hyd-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "RaspberryPi_Camera"
TOPIC = "camera/images"
IMAGE_PATH = "/tmp/image.jpg"

ROOT_CA = CERT_PATH + "AmazonRootCA1.pem"
PRIVATE_KEY = CERT_PATH + "b555123197747ec6327a53bf46c85636106f00b514b01e9a7b3fbc96fa730b81-private.pem.key"          # 替換這行
CERT = CERT_PATH + "b555123197747ec6327a53bf46c85636106f00b514b01e9a7b3fbc96fa730b81-certificate.pem.crt"             # 替換這行

# === 初始化 MQTT 客戶端 ===
mqtt_client = AWSIoTMQTTClient(CLIENT_ID)
mqtt_client.configureEndpoint(ENDPOINT, 8883)
mqtt_client.configureCredentials(ROOT_CA, PRIVATE_KEY, CERT)
mqtt_client.configureOfflinePublishQueueing(-1)  # 無限佇列
mqtt_client.configureDrainingFrequency(2)
mqtt_client.configureConnectDisconnectTimeout(10)
mqtt_client.configureMQTTOperationTimeout(5)

print("🔗 Connecting to AWS IoT Core...")
mqtt_client.connect()
print("✅ Connected!")

# === 初始化 PiCamera2 ===
picam2 = Picamera2()
picam2.start()
time.sleep(2)  # 相機預熱

def capture_and_upload():
    try:
        # 拍照
        print("📸 Capturing image...")
        picam2.capture_file(IMAGE_PATH)
        print(f"✅ Image saved to {IMAGE_PATH}")
        
        # 讀圖 + base64 編碼
        with open(IMAGE_PATH, "rb") as f:
            encoded_image = base64.b64encode(f.read()).decode('utf-8')
        
        # 準備 payload
        # payload = {
        #     "timestamp": int(time.time()),
        #     "device_id": CLIENT_ID,
        #     "image_data": encoded_image
        # }
        payload = {
            "timestamp": int(time.time()),
            "device_id": CLIENT_ID,
            "image_data": encoded_image,
            "filename": f"{int(time.time())}.jpg"   # optional，可加可不加
        }
        # 發布到 MQTT
        print("📤 Publishing image to MQTT...")
        mqtt_client.publish(TOPIC, json.dumps(payload), 1)
        print("✅ Image published successfully!")
    
    except Exception as e:
        print(f"❌ Error: {e}")

# === 主循環 ===
try:
    while True:
        capture_and_upload()
        time.sleep(10)
except KeyboardInterrupt:
    print("🛑 Stopped by user.")
    mqtt_client.disconnect()
    picam2.close()