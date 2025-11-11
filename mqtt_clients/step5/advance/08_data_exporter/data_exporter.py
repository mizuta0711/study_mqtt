"""
データエクスポートツール

機能:
- センサーデータの収集
- CSV形式でエクスポート
- JSON形式でエクスポート
"""

import paho.mqtt.client as mqtt
from datetime import datetime
import csv
import json

BROKER = "localhost"
PORT = 1883

# データを保存するリスト
all_data = []

def on_connect(client, userdata, flags, rc):
    """接続時のコールバック"""
    if rc == 0:
        print("✅ ブローカーに接続")
        print(f"📡 {BROKER}:{PORT}")
        # 全センサーデータを購読
        client.subscribe("sensors/#", qos=1)
        print("📥 トピック購読: sensors/#")
        print("-" * 50)
        print("📝 データ収集開始...")
        print("Ctrl+C で停止してエクスポート")
        print("-" * 50)
    else:
        print(f"❌ 接続失敗: {rc}")

def on_message(client, userdata, msg):
    """メッセージ受信時のコールバック"""
    topic = msg.topic
    payload = msg.payload.decode()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # トピックからセンサーIDを抽出
        parts = topic.split('/')
        if len(parts) < 3:
            return

        sensor_id = parts[1]

        # センサーデータ
        if "temperature" in topic and "alerts" not in topic:
            record = {
                "timestamp": timestamp,
                "sensor_id": sensor_id,
                "type": "temperature",
                "value": float(payload),
                "unit": "°C"
            }
            all_data.append(record)
            print(f"📝 収集: {sensor_id} - 温度 {payload}°C (合計: {len(all_data)}件)")

        elif "humidity" in topic and "alerts" not in topic:
            record = {
                "timestamp": timestamp,
                "sensor_id": sensor_id,
                "type": "humidity",
                "value": float(payload),
                "unit": "%"
            }
            all_data.append(record)
            print(f"📝 収集: {sensor_id} - 湿度 {payload}% (合計: {len(all_data)}件)")

        elif "light" in topic and "alerts" not in topic:
            record = {
                "timestamp": timestamp,
                "sensor_id": sensor_id,
                "type": "light",
                "value": float(payload),
                "unit": "lux"
            }
            all_data.append(record)
            print(f"📝 収集: {sensor_id} - 照度 {payload} lux (合計: {len(all_data)}件)")

    except ValueError as e:
        print(f"⚠️  データのパースに失敗: {e}")
    except Exception as e:
        print(f"❌ エラー: {e}")

def export_to_csv():
    """CSV形式でエクスポート"""
    if len(all_data) == 0:
        print("💾 エクスポートするデータがありません")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sensor_data_{timestamp}.csv"

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['timestamp', 'sensor_id', 'type', 'value', 'unit']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            for record in all_data:
                writer.writerow(record)

        print(f"\n💾 CSVエクスポート完了: {filename}")
        print(f"📊 保存件数: {len(all_data)}件")
        return filename

    except Exception as e:
        print(f"❌ CSVエクスポートエラー: {e}")
        return None

def export_to_json():
    """JSON形式でエクスポート"""
    if len(all_data) == 0:
        print("💾 エクスポートするデータがありません")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sensor_data_{timestamp}.json"

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)

        print(f"💾 JSONエクスポート完了: {filename}")
        print(f"📊 保存件数: {len(all_data)}件")
        return filename

    except Exception as e:
        print(f"❌ JSONエクスポートエラー: {e}")
        return None

def print_summary():
    """サマリーを表示"""
    print("\n" + "=" * 50)
    print("📊 データ収集サマリー")
    print("=" * 50)

    if len(all_data) == 0:
        print("データが収集されませんでした")
        return

    # データ数
    print(f"\n総データ数: {len(all_data)}件")

    # 種類別データ数
    data_types = {}
    for record in all_data:
        data_type = record["type"]
        data_types[data_type] = data_types.get(data_type, 0) + 1

    print("\n【種類別データ数】")
    for data_type, count in data_types.items():
        print(f"  {data_type}: {count}件")

    # センサー別データ数
    sensors = {}
    for record in all_data:
        sensor_id = record["sensor_id"]
        sensors[sensor_id] = sensors.get(sensor_id, 0) + 1

    print("\n【センサー別データ数】")
    for sensor_id, count in sensors.items():
        print(f"  {sensor_id}: {count}件")

    # 収集期間
    if len(all_data) > 0:
        first = all_data[0]["timestamp"]
        last = all_data[-1]["timestamp"]
        print(f"\n【収集期間】")
        print(f"  開始: {first}")
        print(f"  終了: {last}")

    print("=" * 50)

def main():
    # MQTTクライアント設定
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "DataExporter01")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_forever()

    except KeyboardInterrupt:
        print("\n\n🛑 データ収集を停止します...")
        print_summary()

        # エクスポート
        if len(all_data) > 0:
            print("\n💾 データをエクスポートしています...")
            csv_file = export_to_csv()
            json_file = export_to_json()

            print("\n✅ エクスポート完了")
            if csv_file:
                print(f"  CSV: {csv_file}")
            if json_file:
                print(f"  JSON: {json_file}")

    finally:
        # クリーンアップ
        client.disconnect()
        print("\n✅ 停止完了")

if __name__ == "__main__":
    main()
