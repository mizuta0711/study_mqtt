import paho.mqtt.client as mqtt
import random
import time

locations = [
    "倉庫",
    "高速道路",
    "SA（休憩中）",
    "市街地",
    "配達先エリア",
    "配達完了"
]

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "DeliveryVan01")
client.connect("localhost", 1883, 60)

print("🚚 配達車両シミュレータ")
print("-" * 50)

for i, location in enumerate(locations):
    progress = int((i / (len(locations) - 1)) * 100)
    message = f"{location}|{progress}"

    client.publish("delivery/van01/location", message)
    print(f"📍 現在地: {location} ({progress}%)")

    time.sleep(2)

client.disconnect()
print("✅ 配達完了！")
