# publisher.py
import paho.mqtt.client as mqtt
import time

# 接続設定
BROKER = "localhost"
PORT = 1883
TOPIC = "test/hello"

# MQTTクライアントを作成
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

print("🔌 MQTTブローカーに接続中...")
client.connect(BROKER, PORT, 60)
print("✅ 接続成功！")

# メッセージを5回送信
for i in range(1, 6):
    topics = [f"sensor/{i}/temperature", f"sensor/{i}/humidity", f"sensor/{i}/pressure"]

    for j, topic in enumerate(topics, 1):
        message = f"センサー{i}からのデータです"
        client.publish(topic, message)
        print(f"📤 送信: [{topic}] {message}")
        time.sleep(1)

print("👋 すべてのメッセージを送信しました。切断します。")
client.disconnect()
