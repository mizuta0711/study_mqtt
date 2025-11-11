"""
MQTTデータロガー

機能:
- 全センサーデータをSQLiteデータベースに保存
- タイムスタンプ付きで記録
- データのクエリとエクスポート機能
"""

import paho.mqtt.client as mqtt
import sqlite3
from datetime import datetime
import json
import os

BROKER = "localhost"
PORT = 1883
DB_PATH = "sensor_data.db"

class DataLogger:
    def __init__(self, db_path):
        """データベース初期化"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
        print(f"✅ データベース準備完了: {db_path}")

    def _create_tables(self):
        """テーブル作成"""
        cursor = self.conn.cursor()

        # センサーデータテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                data_type TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT
            )
        ''')

        # アラートテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                value REAL NOT NULL,
                message TEXT
            )
        ''')

        # ステータステーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS status_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL
            )
        ''')

        self.conn.commit()

    def log_sensor_data(self, sensor_id, data_type, value, unit=""):
        """センサーデータを記録"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO sensor_data (sensor_id, timestamp, data_type, value, unit)
            VALUES (?, ?, ?, ?, ?)
        ''', (sensor_id, datetime.now().isoformat(), data_type, value, unit))
        self.conn.commit()

    def log_alert(self, sensor_id, alert_type, value, message):
        """アラートを記録"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO alerts (sensor_id, timestamp, alert_type, value, message)
            VALUES (?, ?, ?, ?, ?)
        ''', (sensor_id, datetime.now().isoformat(), alert_type, value, message))
        self.conn.commit()

    def log_status(self, sensor_id, status):
        """ステータスを記録"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO status_log (sensor_id, timestamp, status)
            VALUES (?, ?, ?)
        ''', (sensor_id, datetime.now().isoformat(), status))
        self.conn.commit()

    def get_recent_data(self, sensor_id, data_type, limit=100):
        """最新データを取得"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT timestamp, value
            FROM sensor_data
            WHERE sensor_id = ? AND data_type = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (sensor_id, data_type, limit))
        return cursor.fetchall()

    def get_statistics(self, sensor_id, data_type):
        """統計情報を取得"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT
                COUNT(*) as count,
                AVG(value) as avg,
                MIN(value) as min,
                MAX(value) as max
            FROM sensor_data
            WHERE sensor_id = ? AND data_type = ?
        ''', (sensor_id, data_type))
        return cursor.fetchone()

    def close(self):
        """データベースを閉じる"""
        self.conn.close()

# グローバル変数
logger = None

def on_connect(client, userdata, flags, rc):
    """接続時のコールバック"""
    if rc == 0:
        print("✅ ブローカーに接続")
        print(f"📡 {BROKER}:{PORT}")
        # 全トピックを購読
        client.subscribe("sensors/#", qos=1)
        client.subscribe("alerts/#", qos=2)
        print("📥 トピック購読: sensors/#, alerts/#")
        print("-" * 50)
        print("📝 データロギング開始...")
        print("Ctrl+C で停止")
        print("-" * 50)
    else:
        print(f"❌ 接続失敗: {rc}")

def on_message(client, userdata, msg):
    """メッセージ受信時のコールバック"""
    global logger

    topic = msg.topic
    payload = msg.payload.decode()

    try:
        # トピックからセンサーIDを抽出
        parts = topic.split('/')
        if len(parts) < 3:
            return

        sensor_id = parts[1]

        # 温度データ
        if "temperature" in topic and "alerts" not in topic:
            temp = float(payload)
            logger.log_sensor_data(sensor_id, "temperature", temp, "°C")
            print(f"📝 記録: {sensor_id} - 温度 {temp}°C")

        # 湿度データ
        elif "humidity" in topic and "alerts" not in topic:
            humid = float(payload)
            logger.log_sensor_data(sensor_id, "humidity", humid, "%")
            print(f"📝 記録: {sensor_id} - 湿度 {humid}%")

        # 照度データ
        elif "light" in topic and "alerts" not in topic:
            light = float(payload)
            logger.log_sensor_data(sensor_id, "light", light, "lux")
            print(f"📝 記録: {sensor_id} - 照度 {light} lux")

        # ステータス
        elif "status" in topic:
            logger.log_status(sensor_id, payload)
            emoji = "🟢" if payload == "ONLINE" else "🔴"
            print(f"📝 記録: {sensor_id} - ステータス {emoji} {payload}")

        # アラート
        elif "alerts" in topic:
            try:
                alert_data = json.loads(payload)
                logger.log_alert(
                    alert_data.get("sensor_id", sensor_id),
                    alert_data.get("type", "unknown"),
                    alert_data.get("value", 0),
                    alert_data.get("alert", "")
                )
                print(f"🚨 記録: アラート - {alert_data.get('alert', '')}")
            except json.JSONDecodeError:
                print(f"⚠️  アラートのパースに失敗: {payload}")

    except ValueError as e:
        print(f"⚠️  データのパースに失敗: {e}")
    except Exception as e:
        print(f"❌ エラー: {e}")

def print_statistics():
    """統計情報を表示"""
    global logger
    print("\n" + "=" * 50)
    print("📊 統計情報")
    print("=" * 50)

    sensor_ids = ["MultiSensor01", "RealisticSensor01"]
    data_types = [("temperature", "°C"), ("humidity", "%"), ("light", "lux")]

    for sensor_id in sensor_ids:
        print(f"\n【{sensor_id}】")
        for data_type, unit in data_types:
            stats = logger.get_statistics(sensor_id, data_type)
            if stats and stats[0] > 0:
                count, avg, min_val, max_val = stats
                print(f"  {data_type}:")
                print(f"    データ数: {count}")
                print(f"    平均: {avg:.2f} {unit}")
                print(f"    最小: {min_val:.2f} {unit}")
                print(f"    最大: {max_val:.2f} {unit}")

    print("=" * 50)

def main():
    global logger

    # データロガー初期化
    logger = DataLogger(DB_PATH)

    # MQTTクライアント設定
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "DataLogger01")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_forever()

    except KeyboardInterrupt:
        print("\n\n🛑 データロガーを停止します...")
        print_statistics()

    finally:
        # クリーンアップ
        client.disconnect()
        logger.close()
        print("✅ 停止完了")

if __name__ == "__main__":
    main()
