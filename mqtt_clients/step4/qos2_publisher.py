import paho.mqtt.client as mqtt
import time

def on_publish(client, userdata, mid):
    print(f"  → ✅ メッセージID {mid} の送信完了を確認")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_publish = on_publish
client.connect("localhost", 1883, 60)

print("📤 QoS 2 でメッセージ送信中...")
for i in range(5):
    info = client.publish("test/qos2", f"メッセージ {i}", qos=2)
    print(f"送信 {i}: メッセージID={info.mid}")
    time.sleep(0.5)

client.disconnect()
print("✅ 完了(QoS 2)")
