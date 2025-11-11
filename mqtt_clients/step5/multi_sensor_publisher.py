"""
複数センサー統合Publisher

機能:
- 温度、湿度、照度の3種類のセンサーをシミュレート
- 各センサーに適したQoS設定
- 異常値の検出とアラート送信
"""

import paho.mqtt.client as mqtt
import random
import time
import json
from datetime import datetime

BROKER = "localhost"
PORT = 1883
SENSOR_ID = "MultiSensor01"

# センサーの現在値
current_temp = 25.0
current_humid = 50.0
current_light = 500

def on_connect(client, userdata, flags, rc):
    """接続時のコールバック"""
    if rc == 0:
        # ステータスをRetainで送信
        client.publish(f"sensors/{SENSOR_ID}/status", "ONLINE", qos=1, retain=True)
        print("✅ マルチセンサーシステム起動完了")
        print(f"📡 ブローカー: {BROKER}:{PORT}")
        print("-" * 50)
    else:
        print(f"❌ 接続失敗: {rc}")

def generate_temperature():
    """リアルな温度生成"""
    global current_temp
    # 前回値から±0.5°Cの範囲で変化
    current_temp += random.uniform(-0.5, 0.5)
    current_temp = max(15.0, min(35.0, current_temp))
    return round(current_temp, 2)

def generate_humidity():
    """湿度生成"""
    global current_humid
    # 前回値から±2%の範囲で変化
    current_humid += random.uniform(-2.0, 2.0)
    current_humid = max(20.0, min(80.0, current_humid))
    return round(current_humid, 1)

def generate_light():
    """照度生成"""
    global current_light
    # 前回値から±50 luxの範囲で変化
    current_light += random.uniform(-50, 50)
    current_light = max(0, min(1000, current_light))
    return int(current_light)

def check_alert(client, sensor_type, value):
    """異常値チェックとアラート送信"""
    alert = None

    if sensor_type == "temperature":
        if value > 30.0:
            alert = "高温警報"
        elif value < 18.0:
            alert = "低温警報"

    elif sensor_type == "humidity":
        if value > 70.0:
            alert = "高湿度警報"
        elif value < 30.0:
            alert = "低湿度警報"

    if alert:
        alert_data = {
            "sensor_id": SENSOR_ID,
            "type": sensor_type,
            "value": value,
            "alert": alert,
            "timestamp": datetime.now().isoformat()
        }

        # アラートはQoS 2で確実に送信
        client.publish(
            f"alerts/{sensor_type}",
            json.dumps(alert_data, ensure_ascii=False),
            qos=2
        )
        print(f"🚨 {alert}: {value}")

def main():
    # クライアント作成
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, SENSOR_ID)

    # Last Will設定
    client.will_set(f"sensors/{SENSOR_ID}/status", "OFFLINE", qos=1, retain=True)

    client.on_connect = on_connect

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()

        print("🌡️  マルチセンサー稼働中...")
        print("センサー: 温度、湿度、照度")
        print("Ctrl+C で停止")
        print("-" * 50)

        while True:
            # 各センサーの値を生成
            temp = generate_temperature()
            humid = generate_humidity()
            light = generate_light()

            # 温度データ送信（QoS 0: 高速）
            client.publish(f"sensors/{SENSOR_ID}/temperature", str(temp), qos=0)

            # 湿度データ送信（QoS 0: 高速）
            client.publish(f"sensors/{SENSOR_ID}/humidity", str(humid), qos=0)

            # 照度データ送信（QoS 0: 高速）
            client.publish(f"sensors/{SENSOR_ID}/light", str(light), qos=0)

            # 異常値チェック
            check_alert(client, "temperature", temp)
            check_alert(client, "humidity", humid)

            # コンソール出力
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 🌡️ {temp}°C | 💧 {humid}% | 💡 {light} lux")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 センサーシステムを停止します...")
        # 正常停止時もステータスを更新
        client.publish(f"sensors/{SENSOR_ID}/status", "OFFLINE", qos=1, retain=True)
        time.sleep(0.5)
        client.loop_stop()
        client.disconnect()
        print("✅ 停止完了")

    except Exception as e:
        print(f"❌ エラー: {e}")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
