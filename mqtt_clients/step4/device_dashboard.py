import paho.mqtt.client as mqtt
from datetime import datetime

devices = {}

def on_message(client, userdata, msg):
    parts = msg.topic.split('/')
    device = parts[1]
    message_type = parts[2]
    value = msg.payload.decode()

    if device not in devices:
        devices[device] = {"status": "?", "data": "?", "last_seen": "?"}

    devices[device][message_type] = value
    devices[device]["last_seen"] = datetime.now().strftime("%H:%M:%S")

    # ダッシュボード表示
    print("\n" + "=" * 70)
    print("📊 IoTデバイス監視ダッシュボード")
    print("=" * 70)
    for dev_id, info in sorted(devices.items()):
        status_emoji = "🟢" if info["status"] == "ONLINE" else "🔴"
        print(f"{status_emoji} {dev_id:15} | "
              f"状態: {info['status']:8} | "
              f"データ: {info['data']:6} | "
              f"最終更新: {info['last_seen']}")
    print("=" * 70)

def on_connect(client, userdata, flags, rc):
    print("📡 ダッシュボード起動")
    client.subscribe("devices/#")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Dashboard")
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)

print("⏳ デバイスを監視中...")
client.loop_forever()
