import paho.mqtt.client as mqtt
import json

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())

    temp = data['temperature']
    humid = data['humidity']
    press = data['pressure']

    print("\n" + "=" * 50)
    print("📊 センサーダッシュボード")
    print("=" * 50)
    print(f"🌡️  温度: {temp}°C")
    print(f"💧 湿度: {humid}%")
    print(f"🌤️  気圧: {press}hPa")

    # 快適度を判定
    if 22 <= temp <= 26 and 40 <= humid <= 60:
        print("😊 快適な環境です！")
    else:
        print("⚠️ 環境を調整することをお勧めします")

def on_connect(client, userdata, flags, rc):
    print("📡 ダッシュボード起動")
    client.subscribe("sensors/data")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_forever()
