# qos_benchmark.py
import paho.mqtt.client as mqtt
import time

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.connect("localhost", 1883, 60)

num_messages = 100

for qos in [0, 1, 2]:
    start = time.time()

    for i in range(num_messages):
        client.publish(f"benchmark/qos{qos}", f"msg{i}", qos=qos)

    elapsed = time.time() - start
    avg = elapsed / num_messages * 1000  # ミリ秒

    print(f"QoS {qos}: {elapsed:.4f}秒 | 平均 {avg:.2f}ms/msg")

client.disconnect()
