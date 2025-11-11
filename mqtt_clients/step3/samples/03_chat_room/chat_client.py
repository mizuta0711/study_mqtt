import paho.mqtt.client as mqtt
import threading

ROOM = "chat/lobby"

def on_message(client, userdata, msg):
    sender = msg.topic.split('/')[-1]
    message = msg.payload.decode()
    if sender != client._client_id.decode():
        print(f"\n💬 {sender}: {message}")
        print("あなた> ", end="", flush=True)

def on_connect(client, userdata, flags, rc):
    client.subscribe(f"{ROOM}/#")

# ユーザー名を入力
username = input("ユーザー名を入力: ")
print(f"\n👋 ようこそ、{username}さん！")
print("💬 メッセージを入力してください（'quit'で終了）\n")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, username)
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_start()

try:
    while True:
        message = input("あなた> ")
        if message.lower() == "quit":
            break
        client.publish(f"{ROOM}/{username}", message)
except KeyboardInterrupt:
    pass

client.loop_stop()
client.disconnect()
print("\n👋 チャットを終了しました")
