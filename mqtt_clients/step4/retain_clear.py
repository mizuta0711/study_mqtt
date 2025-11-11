import paho.mqtt.client as mqtt

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.connect("localhost", 1883, 60)

# 空のペイロードでRetain=Trueを送信すると削除される
client.publish("device/status", "", retain=True)
print("🗑️  Retainメッセージを削除しました")

client.disconnect()
