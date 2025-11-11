import paho.mqtt.client as mqtt
import random
import time

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Player1")
client.connect("localhost", 1883, 60)

print("🎲 プレイヤー1です")
input("Enterキーでサイコロを振ります...")

dice = random.randint(1, 6)
client.publish("game/dice/player1", str(dice))
print(f"🎲 あなたの出目: {dice}")

client.disconnect()
