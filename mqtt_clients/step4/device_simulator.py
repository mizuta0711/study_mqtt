import paho.mqtt.client as mqtt
import random
import time

devices = ["sensor01", "sensor02", "sensor03"]

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.connect("localhost", 1883, 60)

print("🖥️  デバイスシミュレータ起動")
print("=" * 60)

try:
    for device in devices:
        status = random.choice(["ONLINE", "OFFLINE", "MAINTENANCE"])
        temp = round(random.uniform(20, 30), 1)

        # ステータスをRetainで送信
        client.publish(f"devices/{device}/status", status, retain=True)
        # 温度は通常のメッセージ
        client.publish(f"devices/{device}/temperature", str(temp), retain=False)

        print(f"📤 {device}: {status}, {temp}°C")
        time.sleep(1)
except KeyboardInterrupt:
    pass

client.disconnect()
print("\n✅ シミュレータ停止")
