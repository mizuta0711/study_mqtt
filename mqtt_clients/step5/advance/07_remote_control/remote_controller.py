"""
MQTTリモートコントローラー

機能:
- デバイスへのコマンド送信
- 電源制御、温度設定、モード変更
- ステータス確認
"""

import paho.mqtt.client as mqtt
import time
from datetime import datetime

BROKER = "localhost"
PORT = 1883
DEVICE_ID = "living-room"

client = None

def on_connect(client, userdata, flags, rc):
    """接続時のコールバック"""
    if rc == 0:
        print("✅ ブローカーに接続")
        print(f"📡 {BROKER}:{PORT}")
        # デバイスのステータスを購読
        client.subscribe(f"devices/{DEVICE_ID}/status/#", qos=1)
        print(f"📥 トピック購読: devices/{DEVICE_ID}/status/#")
        print("-" * 50)
    else:
        print(f"❌ 接続失敗: {rc}")

def on_message(client, userdata, msg):
    """ステータス受信"""
    topic = msg.topic
    payload = msg.payload.decode()
    timestamp = datetime.now().strftime("%H:%M:%S")

    if "/status/" in topic:
        status_type = topic.split('/')[-1]
        print(f"📥 [{timestamp}] ステータス更新: {status_type} = {payload}")

def send_command(command_type, value):
    """コマンドを送信"""
    global client
    topic = f"devices/{DEVICE_ID}/commands/{command_type}"

    # QoS 2で確実に送信
    result = client.publish(topic, value, qos=2)

    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"📤 コマンド送信: {command_type} = {value}")
    else:
        print(f"❌ 送信失敗: {command_type}")

    time.sleep(0.1)  # 少し待機

def show_menu():
    """メニューを表示"""
    print("\n" + "=" * 50)
    print("🎮 MQTTリモートコントローラー")
    print("=" * 50)
    print(f"デバイスID: {DEVICE_ID}")
    print()
    print("コマンドを選択してください:")
    print("  1. 電源ON")
    print("  2. 電源OFF")
    print("  3. 温度設定")
    print("  4. モード変更 (cool/heat/fan)")
    print("  5. ステータス確認")
    print("  6. 終了")
    print("=" * 50)

def main():
    global client

    # MQTTクライアント設定
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "RemoteController01")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()

        time.sleep(1)  # 接続を待つ

        while True:
            show_menu()
            choice = input("\n選択 (1-6): ").strip()

            if choice == "1":
                # 電源ON
                send_command("power", "ON")

            elif choice == "2":
                # 電源OFF
                send_command("power", "OFF")

            elif choice == "3":
                # 温度設定
                temp = input("目標温度 (°C) を入力: ").strip()
                try:
                    temp_value = float(temp)
                    if 16 <= temp_value <= 30:
                        send_command("set-temp", str(temp_value))
                    else:
                        print("⚠️  温度は16〜30°Cの範囲で指定してください")
                except ValueError:
                    print("⚠️  数値を入力してください")

            elif choice == "4":
                # モード変更
                print("\nモードを選択:")
                print("  1. 冷房 (cool)")
                print("  2. 暖房 (heat)")
                print("  3. 送風 (fan)")
                mode_choice = input("選択 (1-3): ").strip()

                if mode_choice == "1":
                    send_command("mode", "cool")
                elif mode_choice == "2":
                    send_command("mode", "heat")
                elif mode_choice == "3":
                    send_command("mode", "fan")
                else:
                    print("⚠️  無効な選択です")

            elif choice == "5":
                # ステータス確認
                send_command("status", "request")
                print("⏳ ステータス取得中...")
                time.sleep(1)

            elif choice == "6":
                # 終了
                print("\n👋 コントローラーを終了します")
                break

            else:
                print("⚠️  1〜6の数字を入力してください")

    except KeyboardInterrupt:
        print("\n\n🛑 コントローラーを停止します...")

    finally:
        # クリーンアップ
        client.loop_stop()
        client.disconnect()
        print("✅ 停止完了")

if __name__ == "__main__":
    main()
