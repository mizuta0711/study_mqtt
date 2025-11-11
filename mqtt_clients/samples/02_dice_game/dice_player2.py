import paho.mqtt.client as mqtt
import random

player1_dice = None
player2_dice = None

def on_message(client, userdata, msg):
    global player1_dice, player2_dice

    if msg.topic == "game/dice/player1":
        player1_dice = int(msg.payload.decode())
        print(f"🎲 プレイヤー1の出目: {player1_dice}")

    if player1_dice and player2_dice:
        print("\n" + "=" * 50)
        if player2_dice > player1_dice:
            print("🎉 あなたの勝ち！")
        elif player2_dice < player1_dice:
            print("😢 あなたの負け...")
        else:
            print("🤝 引き分け！")
        print("=" * 50)
        client.disconnect()

def on_connect(client, userdata, flags, rc):
    client.subscribe("game/dice/#")

client = mqtt.Client("Player2")
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)

print("🎲 プレイヤー2です")
input("Enterキーでサイコロを振ります...")

player2_dice = random.randint(1, 6)
client.publish("game/dice/player2", str(player2_dice))
print(f"🎲 あなたの出目: {player2_dice}")

client.loop_forever()
