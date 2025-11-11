import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ 接続成功")
        # 正常なステータスを送信
        client.publish("sensor/status", "ONLINE", retain=True)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "SensorDevice01")

# Last Willを設定(接続前に設定する!)
client.will_set(
    topic="sensor/status",
    payload="OFFLINE",
    qos=1,
    retain=True
)

client.on_connect = on_connect
client.connect("localhost", 1883, 60)
client.loop_start()

print("🌡️  センサー稼働中...")
print("💡 Ctrl+Cで異常終了をシミュレート")

try:
    while True:
        # 温度データを送信
        client.publish("sensor/temperature", "25.5")
        time.sleep(2)
except KeyboardInterrupt:
    print("\n⚠️  異常終了します(Last Willが送信されます)")
    # loop_stop()とdisconnect()を呼ばずに終了
    exit(0)
