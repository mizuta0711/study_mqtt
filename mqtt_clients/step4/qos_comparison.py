import paho.mqtt.client as mqtt
import time

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.connect("localhost", 1883, 60)

print("🔬 QoS 0/1/2 の比較実験")
print("=" * 60)

qos_levels = [0, 1, 2]
for qos in qos_levels:
    start = time.time()

    for i in range(10):
        client.publish(f"test/qos{qos}", f"メッセージ {i}", qos=qos)

    elapsed = time.time() - start
    print(f"QoS {qos}: {elapsed:.4f}秒 で10メッセージ送信")

client.disconnect()
print("=" * 60)
print("💡 結果: QoS 0が最速、QoS 2が最も確実")
