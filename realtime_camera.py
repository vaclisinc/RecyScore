import time
import os
import json
import base64
from dotenv import load_dotenv
from picamera2 import Picamera2
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from tkinter import Tk, Canvas
from PIL import Image, ImageTk
from threading import Thread

# === 載入憑證設定 ===
CERT_PATH = os.path.expanduser("~/aws-iot-certs/")
CLIENT_ID = "RaspberryPi_Camera"
TOPIC = "camera/images"
IMAGE_PATH = "/tmp/image.jpg"

load_dotenv()
ENDPOINT = os.getenv("ENDPOINT")
ROOT_CA = CERT_PATH + os.getenv("ROOT_CA")
PRIVATE_KEY = CERT_PATH + os.getenv("PRIVATE_KEY")
CERT = CERT_PATH + os.getenv("CERT")

# === MQTT 初始化 ===
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

# === 相機初始化 ===
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

# === GUI ===
root = Tk()
root.attributes("-fullscreen", False)
canvas = Canvas(root, width=640, height=480, bg="black", highlightthickness=0)
canvas.place(relx=0.5, rely=0.5, anchor="center")

# 畫出按鈕（可更新圖示）
def draw_button(icon):
    r = 40
    x = 320
    y = 400
    canvas.delete("button")
    canvas.create_oval(x - r, y - r, x + r, y + r, fill="white", outline="", tags="button")
    canvas.create_text(x, y, text=icon, font=("Noto Color Emoji", 28), tags="button")

# 拍照與上傳
def capture_and_upload():
    def task():
        draw_button("📤")
        picam2.capture_file(IMAGE_PATH)
        with open(IMAGE_PATH, "rb") as f:
            encoded_image = base64.b64encode(f.read()).decode('utf-8')
        payload = {
            "timestamp": int(time.time()),
            "device_id": CLIENT_ID,
            "image_data": encoded_image
        }
        mqtt_client.publish(TOPIC, json.dumps(payload), 1)
        draw_button("✅")
        time.sleep(0.5)
        draw_button("📷")
    Thread(target=task).start()

# 點擊偵測按鈕範圍
def on_click(event):
    if 280 <= event.x <= 360 and 360 <= event.y <= 440:
        capture_and_upload()

canvas.bind("<Button-1>", on_click)

# 更新即時預覽畫面
def update_preview():
    frame = picam2.capture_array()
    image = Image.fromarray(frame)
    photo = ImageTk.PhotoImage(image)
    canvas.image = photo
    img_id = canvas.create_image(0, 0, image=photo, anchor="nw", tags="preview")
    canvas.tag_lower(img_id)  # 確保預覽畫面在最底層
    root.after(30, update_preview)

# 啟動
draw_button("📷")
update_preview()
root.mainloop()