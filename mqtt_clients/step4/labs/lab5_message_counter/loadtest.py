# load_test.py
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("localhost", 1883, 60)

for i in range(10000):
    client.publish("test/load", f"msg{i}", qos=0)
    if i % 1000 == 0:
        print(f"{i} messages sent")