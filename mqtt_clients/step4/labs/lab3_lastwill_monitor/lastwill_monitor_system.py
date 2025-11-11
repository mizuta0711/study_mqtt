# lastwill_monitor_system.py
import paho.mqtt.client as mqtt
from datetime import datetime

devices_status = {}

def on_message(client, userdata, msg):
    device = msg.topic.split('/')[1]
    status = msg.payload.decode()
    timestamp = datetime.now().strftime("%H:%M:%S")

    devices_status[device] = {
        "status": status,
        "time": timestamp
    }

    emoji = "🟢" if status == "ONLINE" else "🔴"
    print(f"[{timestamp}] {emoji} {device}: {status}")

    # アラート
    if status == "OFFLINE":
        print(f"  ⚠️  アラート: {device}が応答しません！")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "MonitoringSystem")
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.subscribe("devices/+/status")

print("📡 デバイス監視システム起動")
print("=" * 60)
client.loop_forever()
