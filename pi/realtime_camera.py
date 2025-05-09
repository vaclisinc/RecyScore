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
CLIENT_ID = "RaspberryPi_Cam"
TOPIC = "camera/images"
IMAGE_PATH = "/tmp/image.jpg"
SHADOW_TOPIC_UPDATE = f"$aws/things/{CLIENT_ID}/shadow/update"
SHADOW_TOPIC_DELTA = f"$aws/things/{CLIENT_ID}/shadow/delta"

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

# === Shadow State Management ===
def update_shadow_state(state):
    try:
        shadow_payload = {
            "state": {
                "reported": state
            }
        }
        mqtt_client.publish(SHADOW_TOPIC_UPDATE, json.dumps(shadow_payload), 1)
        print("Updated shadow state:", state)
    except Exception as e:
        print(f"Error updating shadow state: {e}")

def shadow_delta_callback(client, userdata, message):
    try:
        payload = json.loads(message.payload)
        print("Received shadow delta:", payload)
        
        # 處理 delta 更新
        if 'state' in payload:
            state = payload['state']
            if 'capture' in state and state['capture']:
                print("Received capture command from shadow")
                capture_and_upload()
    except Exception as e:
        print(f"Error processing shadow delta: {e}")

print("🔗 Connecting to AWS IoT Core...")
mqtt_client.connect()
print("✅ Connected!")

# 訂閱 shadow delta 主題
mqtt_client.subscribe(SHADOW_TOPIC_DELTA, 1, shadow_delta_callback)
print(f"Subscribed to shadow delta topic: {SHADOW_TOPIC_DELTA}")

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
        try:
            # 更新狀態為拍照中
            update_shadow_state({"status": "capturing"})
            draw_button("📤")
            
            # 拍照
            picam2.capture_file(IMAGE_PATH)
            
            # 更新狀態為上傳中
            update_shadow_state({"status": "uploading"})
            
            # 讀取並編碼圖片
            with open(IMAGE_PATH, "rb") as f:
                encoded_image = base64.b64encode(f.read()).decode('utf-8')
            
            # 準備並發送數據
            payload = {
                "timestamp": int(time.time()),
                "device_id": CLIENT_ID,
                "image_data": encoded_image
            }
            mqtt_client.publish(TOPIC, json.dumps(payload), 1)
            
            # 更新狀態為完成
            update_shadow_state({"status": "idle"})
            draw_button("✅")
            time.sleep(0.5)
            draw_button("📷")
            
        except Exception as e:
            print(f"Error in capture_and_upload: {e}")
            # 更新狀態為錯誤
            update_shadow_state({"status": "error", "error": str(e)})
            draw_button("❌")
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

# 設置初始狀態
update_shadow_state({"status": "idle"})

root.mainloop()