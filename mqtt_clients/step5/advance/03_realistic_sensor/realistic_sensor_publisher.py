"""
リアルな温度変化シミュレーター

機能:
- 時刻に応じた温度変化（正弦波モデル）
- 慣性効果による滑らかな変化
- 湿度と温度の相関
- 照度の日内変動
"""

import paho.mqtt.client as mqtt
import random
import time
import math
import json
from datetime import datetime

BROKER = "localhost"
PORT = 1883
SENSOR_ID = "RealisticSensor01"

class RealisticTemperatureSensor:
    """リアルな温度センサーシミュレーター"""

    def __init__(self, base_temp=25.0):
        self.current_temp = base_temp

    def get_base_temperature(self):
        """時刻に応じた基準温度"""
        hour = datetime.now().hour
        # 正弦波で日内変動（午後2時頃に最高温度）
        # 午前6時: 約20°C、午後2時: 約28°C
        base = 24.0 + 4.0 * math.sin(math.pi * (hour - 6) / 12)
        return base

    def generate_temperature(self):
        """リアルな温度生成"""
        base = self.get_base_temperature()

        # 基準温度に徐々に近づく（慣性効果）
        self.current_temp += (base - self.current_temp) * 0.1

        # ランダムなノイズを追加
        self.current_temp += random.uniform(-0.3, 0.3)

        # 範囲制限
        self.current_temp = max(15.0, min(35.0, self.current_temp))

        return round(self.current_temp, 2)

class RealisticHumiditySensor:
    """リアルな湿度センサーシミュレーター"""

    def __init__(self, base_humid=50.0):
        self.current_humid = base_humid

    def generate_humidity(self, current_temp):
        """リアルな湿度生成（温度と逆相関）"""
        # 温度と逆相関（高温時は低湿度）
        temp_factor = (30.0 - current_temp) * 2.0

        # 基準湿度（50%）+ 温度補正
        base_humid = 50.0 + temp_factor

        # 基準値に徐々に近づく
        self.current_humid += (base_humid - self.current_humid) * 0.05

        # ノイズ追加
        self.current_humid += random.uniform(-1.5, 1.5)

        # 範囲制限
        self.current_humid = max(20.0, min(80.0, self.current_humid))

        return round(self.current_humid, 1)

class RealisticLightSensor:
    """リアルな照度センサーシミュレーター"""

    def __init__(self, base_light=500):
        self.current_light = base_light

    def generate_light(self):
        """リアルな照度生成（時刻依存）"""
        hour = datetime.now().hour

        # 日中（6時〜18時）は高照度
        if 6 <= hour < 18:
            # 正弦波で日中の変化（正午に最大）
            base_light = 500 + 400 * math.sin(math.pi * (hour - 6) / 12)
        else:
            # 夜間は低照度
            base_light = 50

        # 基準値に近づく
        self.current_light += (base_light - self.current_light) * 0.1

        # ノイズ追加
        self.current_light += random.uniform(-30, 30)

        # 範囲制限
        self.current_light = max(0, min(1000, self.current_light))

        return int(self.current_light)

def on_connect(client, userdata, flags, rc):
    """接続時のコールバック"""
    if rc == 0:
        # ステータスをRetainで送信
        client.publish(f"sensors/{SENSOR_ID}/status", "ONLINE", qos=1, retain=True)
        print("✅ リアルセンサーシステム起動完了")
        print(f"📡 ブローカー: {BROKER}:{PORT}")
        print("🌡️  温度モデル: 時刻依存 + 慣性効果 + ノイズ")
        print("💧 湿度モデル: 温度逆相関 + ノイズ")
        print("💡 照度モデル: 日内変動 + ノイズ")
        print("-" * 50)
    else:
        print(f"❌ 接続失敗: {rc}")

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
    # センサーインスタンス作成
    temp_sensor = RealisticTemperatureSensor(base_temp=25.0)
    humid_sensor = RealisticHumiditySensor(base_humid=50.0)
    light_sensor = RealisticLightSensor(base_light=500)

    # クライアント作成
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, SENSOR_ID)

    # Last Will設定
    client.will_set(f"sensors/{SENSOR_ID}/status", "OFFLINE", qos=1, retain=True)

    client.on_connect = on_connect

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()

        print("🌡️  リアルセンサー稼働中...")
        print("センサー: 温度、湿度、照度（リアルモデル）")
        print("Ctrl+C で停止")
        print("-" * 50)

        while True:
            # 現在時刻を取得
            now = datetime.now()
            hour = now.hour
            minute = now.minute

            # 各センサーの値を生成
            temp = temp_sensor.generate_temperature()
            humid = humid_sensor.generate_humidity(temp)  # 温度を渡す
            light = light_sensor.generate_light()

            # データ送信（QoS 0: 高速）
            client.publish(f"sensors/{SENSOR_ID}/temperature", str(temp), qos=0)
            client.publish(f"sensors/{SENSOR_ID}/humidity", str(humid), qos=0)
            client.publish(f"sensors/{SENSOR_ID}/light", str(light), qos=0)

            # 異常値チェック
            check_alert(client, "temperature", temp)
            check_alert(client, "humidity", humid)

            # コンソール出力（時刻付き）
            timestamp = now.strftime("%H:%M:%S")
            print(f"[{timestamp}] 🌡️ {temp}°C | 💧 {humid}% | 💡 {light} lux | ⏰ {hour:02d}:{minute:02d}")

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
