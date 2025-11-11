# message_counter.py
import paho.mqtt.client as mqtt

stats = {"qos0": 0, "qos1": 0, "qos2": 0, "retained": 0}

def on_message(client, userdata, msg):
    stats[f"qos{msg.qos}"] += 1
    if msg.retain:
        stats["retained"] += 1

    print(f"\rQoS0: {stats['qos0']} | "
          f"QoS1: {stats['qos1']} | "
          f"QoS2: {stats['qos2']} | "
          f"Retain: {stats['retained']}", end="")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.subscribe("#")

print("📊 メッセージカウンター起動")
client.loop_forever()
