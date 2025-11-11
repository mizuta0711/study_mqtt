import paho.mqtt.client as mqtt
import random
import time
import json

client = mqtt.Client()
client.connect("localhost", 1883, 60)

print("📊 複数センサーシミュレータ")

try:
    while True:
        data = {
            "temperature": round(random.uniform(20, 30), 1),
            "humidity": round(random.uniform(40, 80), 1),
            "pressure": round(random.uniform(1000, 1020), 1)
        }

        # JSONに変換して送信
        json_data = json.dumps(data)
        client.publish("sensors/data", json_data)

        print(f"📤 送信: 温度={data['temperature']}°C, "
              f"湿度={data['humidity']}%, "
              f"気圧={data['pressure']}hPa")

        time.sleep(2)
except KeyboardInterrupt:
    client.disconnect()
