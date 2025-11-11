# ultimate_sensor.py
import paho.mqtt.client as mqtt
import random
import time
import sys

SENSOR_ID = sys.argv[1] if len(sys.argv) > 1 else "Sensor01"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        # ステータスをRetainで送信（QoS 1）
        client.publish(
            f"sensors/{SENSOR_ID}/status",
            "ONLINE",
            qos=1,
            retain=True
        )
        print(f"✅ {SENSOR_ID} 起動完了")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, SENSOR_ID)

# Last Will設定（QoS 2 + Retain）
client.will_set(
    f"sensors/{SENSOR_ID}/status",
    "OFFLINE",
    qos=2,
    retain=True
)

client.on_connect = on_connect
client.connect("localhost", 1883, 60)
client.loop_start()

print(f"🌡️  {SENSOR_ID} 稼働中...")
print("💡 機能:")
print("  - Last Will (QoS 2 + Retain)")
print("  - 温度データ (QoS 0)")
print("  - 異常アラート (QoS 2)")
print()

try:
    while True:
        temp = round(random.uniform(15, 35), 1)

        # 温度データ（QoS 0: 高速）
        client.publish(
            f"sensors/{SENSOR_ID}/temperature",
            str(temp),
            qos=0
        )

        # 異常値チェック（QoS 2: 確実）
        if temp < 18 or temp > 32:
            alert = f"異常値: {temp}°C"
            client.publish(
                f"sensors/{SENSOR_ID}/alert",
                alert,
                qos=2
            )
            print(f"🚨 {alert}")
        else:
            print(f"📊 {temp}°C")

        time.sleep(2)
except KeyboardInterrupt:
    print(f"\n⚠️  異常終了（Last Willが発火します）")
    exit(0)
