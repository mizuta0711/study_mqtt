"""
温度センサーシミュレーター (Publisher)

機能:
- 1秒ごとにランダムな温度データを送信
- ステータスをRetain + QoS 1で管理
- Last Willで異常終了を検知可能
"""

import paho.mqtt.client as mqtt
import random
import time

BROKER = "localhost"
PORT = 1883
SENSOR_ID = "TemperatureSensor01"

def on_connect(client, userdata, flags, rc):
    """接続時のコールバック"""
    if rc == 0:
        # ステータスをRetainで送信（新規Subscriberがすぐ状態を知れる）
        client.publish("sensor/status", "ONLINE", qos=1, retain=True)
        print("✅ センサー起動完了")
        print(f"📡 ブローカー: {BROKER}:{PORT}")
    else:
        print(f"❌ 接続失敗: {rc}")

def main():
    # クライアント作成（VERSION1を使用）
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, SENSOR_ID)

    # Last Will設定（異常終了時に自動送信）
    client.will_set("sensor/status", "OFFLINE", qos=1, retain=True)

    client.on_connect = on_connect

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()

        print("🌡️  温度センサー稼働中...")
        print("Ctrl+C で停止")
        print("-" * 40)

        while True:
            # 温度データ生成（20.0〜30.0°C）
            temperature = round(random.uniform(20.0, 30.0), 2)

            # QoS 0で高速送信（リアルタイム性重視）
            result = client.publish("sensor/temperature", str(temperature), qos=0)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"📤 送信: {temperature}°C")
            else:
                print(f"⚠️  送信失敗: {result.rc}")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 センサーを停止します...")
        # 正常停止時もステータスを更新
        client.publish("sensor/status", "OFFLINE", qos=1, retain=True)
        time.sleep(0.5)  # メッセージ送信を待つ
        client.loop_stop()
        client.disconnect()
        print("✅ 停止完了")

    except Exception as e:
        print(f"❌ エラー: {e}")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
