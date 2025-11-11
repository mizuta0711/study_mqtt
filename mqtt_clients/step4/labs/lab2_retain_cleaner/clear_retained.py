# clear_retained.py
import paho.mqtt.client as mqtt
import time

retained_topics = []

def on_message(client, userdata, msg):
    if msg.retain:
        retained_topics.append(msg.topic)
        print(f"発見: {msg.topic}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_message = on_message
client.connect("localhost", 1883, 60)

# すべてのトピックを購読
client.subscribe("#")

print("Retainメッセージを検索中...")
client.loop_start()
time.sleep(3)  # 3秒待機
client.loop_stop()

print(f"\n{len(retained_topics)}個のRetainメッセージを発見")
print("削除しますか？ (y/n): ", end="")

if input().lower() == 'y':
    for topic in retained_topics:
        client.publish(topic, "", retain=True)
        print(f"削除: {topic}")
    print("✅ 完了")

client.disconnect()
