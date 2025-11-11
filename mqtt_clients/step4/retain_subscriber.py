import paho.mqtt.client as mqtt
import time

def on_message(client, userdata, msg):
    retained = "✅ [Retained]" if msg.retain else "📨 [New]"
    print(f"{retained} {msg.payload.decode()}")

def on_connect(client, userdata, flags, rc):
    print("📻 購読開始...")
    client.subscribe("device/status")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message

# わざと5秒待ってから接続
print("⏳ 5秒後に接続します...")
time.sleep(5)

client.connect("localhost", 1883, 60)
client.loop_forever()
