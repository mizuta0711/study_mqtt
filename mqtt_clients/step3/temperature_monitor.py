# temperature_monitor.py
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "home/livingroom/temperature"

def on_message(client, userdata, msg):
    temp = float(msg.payload.decode())

    # 温度によって表示を変える
    if temp < 22.0:
        icon = "❄️"
        status = "寒い"
    elif temp > 28.0:
        icon = "🔥"
        status = "暑い"
    else:
        icon = "😊"
        status = "快適"

    print(f"{icon} 現在の温度: {temp}°C ({status})")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("📡 温度モニターを開始しました")
        client.subscribe(TOPIC)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
print("⏳ 温度データを待っています...")
print("-" * 50)

client.loop_forever()
