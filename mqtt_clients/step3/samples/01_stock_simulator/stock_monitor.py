import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    symbol = msg.topic.split('/')[1]
    price = float(msg.payload.decode())
    print(f"💰 {symbol}: ${price:,.2f}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("📡 株価モニター開始")
        client.subscribe("stock/#")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_forever()
