import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    device = msg.topic.split('/')[-1]
    status = msg.payload.decode()
    print(f"✅ {device}の状態: {status}")

def on_connect(client, userdata, flags, rc):
    client.subscribe("home/status/#")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Controller")
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_start()

print("🎮 スマートホームコントローラー")
print("-" * 50)
print("コマンド:")
print("  light on/off")
print("  ac on/off")
print("  door locked/unlocked")
print("  quit - 終了")
print("-" * 50)

try:
    while True:
        command = input("\nコマンド> ").strip().split()
        if not command:
            continue

        if command[0] == "quit":
            break

        if len(command) == 2:
            device, action = command
            client.publish(f"home/control/{device}", action)
        else:
            print("❌ 使い方: <device> <action>")

except KeyboardInterrupt:
    pass

client.loop_stop()
client.disconnect()
print("\n👋 終了しました")
