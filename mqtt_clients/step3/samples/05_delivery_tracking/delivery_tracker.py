import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    data = msg.payload.decode().split('|')
    location = data[0]
    progress = int(data[1])

    # プログレスバーを表示
    bar_length = 20
    filled = int(bar_length * progress / 100)
    bar = "█" * filled + "░" * (bar_length - filled)

    print(f"\r🚚 {location:20} [{bar}] {progress}%", end="", flush=True)

    if progress == 100:
        print("\n✅ 荷物が配達されました！")
        client.disconnect()

def on_connect(client, userdata, flags, rc):
    print("📡 配達トラッカー開始")
    client.subscribe("delivery/#")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Tracker")
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_forever()
