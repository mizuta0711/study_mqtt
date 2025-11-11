import paho.mqtt.client as mqtt
import time

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.connect("localhost", 1883, 60)

print("📤 QoS 0 でメッセージ送信中...")
for i in range(5):
    result = client.publish("test/qos0", f"メッセージ {i}", qos=0)
    print(f"送信 {i}: rc={result.rc}")
    time.sleep(0.5)

client.disconnect()
print("✅ 完了(QoS 0)")
