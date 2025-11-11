"""
アラート監視システム

機能:
- センサーデータの異常値を監視
- アラートの受信と表示
- センサーのダウン検知
"""

import paho.mqtt.client as mqtt
from datetime import datetime
import json

BROKER = "localhost"
PORT = 1883

# アラート履歴
alert_history = []

# センサーステータス
sensor_status = {}

def on_connect(client, userdata, flags, rc):
    """接続時のコールバック"""
    if rc == 0:
        print("✅ ブローカーに接続")
        print(f"📡 {BROKER}:{PORT}")
        # アラートとステータスを購読
        client.subscribe("alerts/#", qos=2)
        client.subscribe("sensors/+/status", qos=1)
        print("📥 トピック購読: alerts/#, sensors/+/status")
        print("-" * 50)
        print("🚨 アラート監視システム起動")
        print("Ctrl+C で停止")
        print("-" * 50)
    else:
        print(f"❌ 接続失敗: {rc}")

def on_message(client, userdata, msg):
    """メッセージ受信時のコールバック"""
    topic = msg.topic
    payload = msg.payload.decode()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # アラート受信
    if "alerts" in topic:
        try:
            alert_data = json.loads(payload)
            sensor_id = alert_data.get("sensor_id", "Unknown")
            alert_type = alert_data.get("type", "unknown")
            value = alert_data.get("value", 0)
            alert_msg = alert_data.get("alert", "")

            # アラート履歴に追加
            alert_history.append({
                "timestamp": timestamp,
                "sensor_id": sensor_id,
                "type": alert_type,
                "value": value,
                "message": alert_msg
            })

            # アラート表示
            print("\n" + "🚨" * 20)
            print(f"⚠️  アラート発生！")
            print(f"時刻: {timestamp}")
            print(f"センサー: {sensor_id}")
            print(f"種類: {alert_type}")
            print(f"値: {value}")
            print(f"メッセージ: {alert_msg}")
            print("🚨" * 20 + "\n")

            # アラートの種類に応じた処理
            if "温度" in alert_msg or "temperature" in alert_type:
                if "高温" in alert_msg:
                    print("💡 対処: 冷房を強化してください")
                elif "低温" in alert_msg:
                    print("💡 対処: 暖房を入れてください")

            elif "湿度" in alert_msg or "humidity" in alert_type:
                if "高湿度" in alert_msg:
                    print("💡 対処: 除湿器を使用してください")
                elif "低湿度" in alert_msg:
                    print("💡 対処: 加湿器を使用してください")

        except json.JSONDecodeError:
            print(f"⚠️  アラートのパースに失敗: {payload}")

    # ステータス変更
    elif "status" in topic:
        # トピックからセンサーIDを抽出
        parts = topic.split('/')
        sensor_id = parts[1] if len(parts) >= 2 else "Unknown"

        # 前回のステータスを取得
        previous_status = sensor_status.get(sensor_id, None)

        # ステータスを更新
        sensor_status[sensor_id] = payload

        # ステータス変更を表示
        if previous_status != payload:
            if payload == "ONLINE":
                print(f"\n🟢 [{timestamp}] {sensor_id} がオンラインになりました")
            elif payload == "OFFLINE":
                print(f"\n🔴 [{timestamp}] {sensor_id} がオフラインになりました")
                print(f"⚠️  {sensor_id} のダウンを検知しました！")
                print(f"💡 対処: センサーの状態を確認してください\n")

def print_summary():
    """サマリーを表示"""
    print("\n" + "=" * 50)
    print("📊 アラート監視サマリー")
    print("=" * 50)

    # アラート数
    print(f"\n総アラート数: {len(alert_history)}")

    if len(alert_history) > 0:
        # 種類別アラート数
        alert_types = {}
        for alert in alert_history:
            alert_type = alert["type"]
            alert_types[alert_type] = alert_types.get(alert_type, 0) + 1

        print("\n【種類別アラート数】")
        for alert_type, count in alert_types.items():
            print(f"  {alert_type}: {count}件")

        # 最新のアラート
        print("\n【最新のアラート（最大5件）】")
        for alert in alert_history[-5:]:
            print(f"  [{alert['timestamp']}] {alert['sensor_id']}: {alert['message']}")

    # センサーステータス
    print("\n【センサーステータス】")
    for sensor_id, status in sensor_status.items():
        emoji = "🟢" if status == "ONLINE" else "🔴"
        print(f"  {emoji} {sensor_id}: {status}")

    print("=" * 50)

def main():
    # MQTTクライアント設定
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "AlertMonitor01")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_forever()

    except KeyboardInterrupt:
        print("\n\n🛑 アラート監視システムを停止します...")
        print_summary()

    finally:
        # クリーンアップ
        client.disconnect()
        print("\n✅ 停止完了")

if __name__ == "__main__":
    main()
