import paho.mqtt.client as mqtt

# デバイスの状態
devices = {
    "light": "off",
    "ac": "off",
    "door": "locked"
}

def on_message(client, userdata, msg):
    device = msg.topic.split('/')[-1]
    command = msg.payload.decode()

    if device in devices:
        devices[device] = command

        if device == "light":
            emoji = "💡" if command == "on" else "🌙"
            print(f"{emoji} 照明を{command}にしました")
        elif device == "ac":
            emoji = "❄️" if command == "on" else "🔥"
            print(f"{emoji} エアコンを{command}にしました")
        elif device == "door":
            emoji = "🔓" if command == "unlocked" else "🔒"
            print(f"{emoji} ドアを{command}にしました")

        # 状態を返信
        client.publish(f"home/status/{device}", command)

def on_connect(client, userdata, flags, rc):
    print("🏠 スマートホームシステム起動")
    client.subscribe("home/control/#")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "HomeDevices")
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)

print("⏳ コマンドを待っています...")
client.loop_forever()
