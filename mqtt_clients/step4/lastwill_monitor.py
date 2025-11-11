import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    status = msg.payload.decode()

    if status == "ONLINE":
        print("🟢 センサーがオンラインになりました")
    elif status == "OFFLINE":
        print("🔴 センサーがオフラインになりました!")
        print("   ⚠️  異常な切断を検知しました")

def on_connect(client, userdata, flags, rc):
    print("📡 モニター起動")
    client.subscribe("sensor/status")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Monitor01")
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)

print("⏳ センサーの状態を監視中...")
client.loop_forever()
