import paho.mqtt.client as mqtt
import random
import time

SENSOR_ID = "SmartSensor01"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ {SENSOR_ID} 接続成功")
        # ステータスをRetainで送信
        client.publish(
            f"sensors/{SENSOR_ID}/status",
            "ONLINE",
            qos=1,
            retain=True
        )

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, SENSOR_ID)

# Last Will設定(QoS 1, Retain有効)
client.will_set(
    topic=f"sensors/{SENSOR_ID}/status",
    payload="OFFLINE",
    qos=1,
    retain=True
)

client.on_connect = on_connect
client.connect("localhost", 1883, 60)
client.loop_start()

print(f"🌡️  {SENSOR_ID} 稼働中...")
print("💡 各メッセージの設定:")
print("  - ステータス: QoS 1 + Retain")
print("  - 温度データ: QoS 0(リアルタイム優先)")
print("  - アラート: QoS 2(確実に配信)")
print()

try:
    counter = 0
    while True:
        counter += 1
        temp = round(random.uniform(18, 32), 1)

        # 温度データ(QoS 0)
        client.publish(
            f"sensors/{SENSOR_ID}/temperature",
            str(temp),
            qos=0
        )

        # 異常値の場合はアラート(QoS 2)
        if temp > 30 or temp < 20:
            alert = f"⚠️  異常値検知: {temp}°C"
            client.publish(
                f"sensors/{SENSOR_ID}/alert",
                alert,
                qos=2
            )
            print(f"🚨 {alert}")
        else:
            print(f"📊 温度: {temp}°C")

        time.sleep(2)
except KeyboardInterrupt:
    print(f"\n⚠️  異常終了")
    exit(0)
