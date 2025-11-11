import paho.mqtt.client as mqtt
import random
import time
import sys

if len(sys.argv) < 2:
    print("使い方: python multi_device_simulator.py <device_id>")
    sys.exit(1)

device_id = sys.argv[1]

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ {device_id} 接続成功")
        client.publish(f"devices/{device_id}/status", "ONLINE", retain=True)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, device_id)

# Last Will設定
client.will_set(
    topic=f"devices/{device_id}/status",
    payload="OFFLINE",
    qos=1,
    retain=True
)

client.on_connect = on_connect
client.connect("localhost", 1883, 60)
client.loop_start()

print(f"🖥️  {device_id} 稼働中... (Ctrl+Cで終了)")

try:
    while True:
        data = round(random.uniform(20, 30), 1)
        client.publish(f"devices/{device_id}/data", str(data))
        time.sleep(2)
except KeyboardInterrupt:
    print(f"\n⚠️  {device_id} を異常終了します")
    exit(0)
