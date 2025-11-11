import paho.mqtt.client as mqtt

device_status = {}

def on_message(client, userdata, msg):
    parts = msg.topic.split('/')
    device = parts[1]
    data_type = parts[2]
    value = msg.payload.decode()

    if device not in device_status:
        device_status[device] = {}

    device_status[device][data_type] = value

    # ステータスボードを表示
    print("\n" + "=" * 60)
    print("📊 デバイスステータスボード")
    print("=" * 60)
    for dev, data in sorted(device_status.items()):
        status = data.get('status', '?')
        temp = data.get('temperature', '?')

        emoji = "🟢" if status == "ONLINE" else "🔴" if status == "OFFLINE" else "🟡"
        print(f"{emoji} {dev}: {status:12} | 温度: {temp}°C")
    print("=" * 60)

def on_connect(client, userdata, flags, rc):
    print("📡 ステータスボード起動")
    client.subscribe("devices/#")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)

print("⏳ デバイス情報を収集中...")
client.loop_forever()
