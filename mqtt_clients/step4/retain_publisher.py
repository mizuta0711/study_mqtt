import paho.mqtt.client as mqtt

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.connect("localhost", 1883, 60)

# Retainメッセージを送信
client.publish("device/status", "ONLINE", retain=True)
print("📤 Retainメッセージを送信: ONLINE")

client.disconnect()
