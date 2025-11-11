# temperature_sensor.py
import paho.mqtt.client as mqtt
import random
import time

BROKER = "localhost"
PORT = 1883
TOPIC = "home/livingroom/temperature"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.connect(BROKER, PORT, 60)

print("🌡️  温度センサーシミュレータを起動しました")
print("📊 1秒ごとに温度データを送信します...")
print("-" * 50)

try:
    while True:
        # 20.0℃〜30.0℃のランダムな温度を生成
        temperature = round(random.uniform(20.0, 30.0), 1)

        client.publish(TOPIC, str(temperature))
        print(f"🌡️  送信: {temperature}°C")

        time.sleep(1)
except KeyboardInterrupt:
    print("\n👋 センサーを停止します")
    client.disconnect()
