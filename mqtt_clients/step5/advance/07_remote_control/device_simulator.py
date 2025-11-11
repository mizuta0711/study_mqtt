"""
デバイスシミュレーター

機能:
- コマンド受信と実行
- デバイス状態の管理
- ステータスの定期送信
"""

import paho.mqtt.client as mqtt
import time
import threading
from datetime import datetime

BROKER = "localhost"
PORT = 1883
DEVICE_ID = "living-room"

# デバイスの状態
device_state = {
    "power": "OFF",
    "mode": "cool",
    "target_temp": 25.0,
    "current_temp": 24.0
}

running = True

def on_connect(client, userdata, flags, rc):
    """接続時のコールバック"""
    if rc == 0:
        print("✅ ブローカーに接続")
        print(f"📡 {BROKER}:{PORT}")
        # コマンドトピックを購読
        client.subscribe(f"devices/{DEVICE_ID}/commands/#", qos=2)
        print(f"📥 トピック購読: devices/{DEVICE_ID}/commands/#")
        print("-" * 50)
        print(f"🏠 デバイス '{DEVICE_ID}' が起動しました")
        print("コマンド待機中...")
        print("Ctrl+C で停止")
        print("-" * 50)

        # 初期ステータスを送信
        send_all_status(client)
    else:
        print(f"❌ 接続失敗: {rc}")

def on_message(client, userdata, msg):
    """コマンド受信"""
    topic = msg.topic
    payload = msg.payload.decode()
    timestamp = datetime.now().strftime("%H:%M:%S")

    print(f"\n📥 [{timestamp}] コマンド受信: {topic.split('/')[-1]} = {payload}")

    # 電源制御
    if topic.endswith("/commands/power"):
        if payload == "ON":
            device_state["power"] = "ON"
            print("🔌 電源をONにしました")
        elif payload == "OFF":
            device_state["power"] = "OFF"
            print("🔌 電源をOFFにしました")

        send_status(client, "power", device_state["power"])

    # 温度設定
    elif topic.endswith("/commands/set-temp"):
        try:
            temp = float(payload)
            if 16 <= temp <= 30:
                device_state["target_temp"] = temp
                print(f"🎯 目標温度を {temp}°C に設定しました")
                send_status(client, "target_temp", str(temp))
            else:
                print("⚠️  温度は16〜30°Cの範囲で設定してください")
        except ValueError:
            print("⚠️  無効な温度値です")

    # モード変更
    elif topic.endswith("/commands/mode"):
        if payload in ["cool", "heat", "fan"]:
            device_state["mode"] = payload
            mode_name = {"cool": "冷房", "heat": "暖房", "fan": "送風"}[payload]
            print(f"🌡️  モードを {mode_name} に変更しました")
            send_status(client, "mode", payload)
        else:
            print("⚠️  無効なモードです")

    # ステータス要求
    elif topic.endswith("/commands/status"):
        print("📊 ステータスを送信します")
        send_all_status(client)

def send_status(client, status_type, value):
    """ステータスを送信"""
    topic = f"devices/{DEVICE_ID}/status/{status_type}"
    client.publish(topic, value, qos=1)

def send_all_status(client):
    """全ステータスを送信"""
    send_status(client, "power", device_state["power"])
    send_status(client, "mode", device_state["mode"])
    send_status(client, "target_temp", str(device_state["target_temp"]))
    send_status(client, "current_temp", str(device_state["current_temp"]))

def simulate_temperature(client):
    """温度をシミュレート"""
    global running

    while running:
        time.sleep(5)  # 5秒ごと

        if device_state["power"] == "ON":
            # 目標温度に近づける
            target = device_state["target_temp"]
            current = device_state["current_temp"]

            if current < target:
                device_state["current_temp"] += 0.5
            elif current > target:
                device_state["current_temp"] -= 0.5

            # ステータス送信
            send_status(client, "current_temp", f"{device_state['current_temp']:.1f}")

def main():
    global running

    # MQTTクライアント設定
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, f"Device_{DEVICE_ID}")
    client.on_connect = on_connect
    client.on_message = on_message

    # 温度シミュレーションスレッド
    temp_thread = threading.Thread(target=simulate_temperature, args=(client,), daemon=True)
    temp_thread.start()

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_forever()

    except KeyboardInterrupt:
        print("\n\n🛑 デバイスを停止します...")
        running = False

    finally:
        # クリーンアップ
        client.disconnect()
        print("✅ 停止完了")

if __name__ == "__main__":
    main()
