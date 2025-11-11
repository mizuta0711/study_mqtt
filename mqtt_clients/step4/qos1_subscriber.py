import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    print(f"📥 受信 [QoS={msg.qos}]: {msg.payload.decode()}")

def on_connect(client, userdata, flags, rc):
    print("📻 QoS 1 で購読開始...")
    client.subscribe("test/qos1", qos=1)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)

print("⏳ QoS 1 メッセージを待機中...")
client.loop_forever()
