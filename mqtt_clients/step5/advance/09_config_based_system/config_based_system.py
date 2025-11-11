"""
設定ベースシステム

機能:
- JSON設定ファイルからシステムを構成
- 複数センサーの一括管理
- 閾値ベースのアラート
- 柔軟なカスタマイズ
"""

import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

# グローバル変数
config = None
sensor_data = {}

def load_config(filename='config.json'):
    """設定ファイルを読み込み"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        print(f"✅ 設定ファイルを読み込みました: {filename}")
        return cfg
    except FileNotFoundError:
        print(f"❌ 設定ファイルが見つかりません: {filename}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ 設定ファイルの解析に失敗: {e}")
        return None

def validate_config(cfg):
    """設定の妥当性をチェック"""
    required_keys = ['broker', 'sensors', 'alerts']
    for key in required_keys:
        if key not in cfg:
            print(f"❌ 設定に '{key}' がありません")
            return False

    if 'host' not in cfg['broker']:
        print("❌ ブローカーのホストが指定されていません")
        return False

    if len(cfg['sensors']) == 0:
        print("⚠️  センサーが設定されていません")

    return True

def check_threshold(sensor_config, value):
    """閾値チェック"""
    if 'thresholds' not in sensor_config:
        return None

    thresholds = sensor_config['thresholds']
    min_val = thresholds.get('min')
    max_val = thresholds.get('max')

    if min_val is not None and value < min_val:
        return f"低{sensor_config['type']}警告"
    elif max_val is not None and value > max_val:
        return f"高{sensor_config['type']}警告"

    return None

def send_alert(sensor_config, value, alert_msg):
    """アラートを送信"""
    if not config['alerts']['enabled']:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # コンソール出力
    if config['alerts']['console']:
        print(f"\n🚨 アラート発生！")
        print(f"  時刻: {timestamp}")
        print(f"  センサー: {sensor_config['id']} ({sensor_config['location']})")
        print(f"  値: {value}")
        print(f"  メッセージ: {alert_msg}\n")

    # メール通知（実装例）
    if config['alerts'].get('email', False):
        print(f"📧 メール通知: {alert_msg}")

    # Slack通知（実装例）
    if config['alerts'].get('slack', False):
        print(f"💬 Slack通知: {alert_msg}")

def on_connect(client, userdata, flags, rc):
    """接続時のコールバック"""
    if rc == 0:
        broker_cfg = config['broker']
        print("✅ ブローカーに接続")
        print(f"📡 {broker_cfg['host']}:{broker_cfg['port']}")

        # 設定されたセンサーのトピックを購読
        for sensor in config['sensors']:
            client.subscribe(sensor['topic'], qos=sensor.get('qos', 0))
            print(f"📥 購読: {sensor['topic']} (QoS {sensor.get('qos', 0)})")

        print("-" * 50)
        print(f"📊 監視中のセンサー: {len(config['sensors'])}個")
        print("Ctrl+C で停止")
        print("-" * 50)
    else:
        print(f"❌ 接続失敗: {rc}")

def on_message(client, userdata, msg):
    """メッセージ受信時のコールバック"""
    topic = msg.topic
    payload = msg.payload.decode()

    # トピックに対応するセンサー設定を検索
    sensor_config = None
    for sensor in config['sensors']:
        if sensor['topic'] == topic:
            sensor_config = sensor
            break

    if sensor_config is None:
        return

    try:
        value = float(payload)

        # データを記録
        sensor_id = sensor_config['id']
        if sensor_id not in sensor_data:
            sensor_data[sensor_id] = []
        sensor_data[sensor_id].append(value)

        # コンソール出力
        timestamp = datetime.now().strftime("%H:%M:%S")
        location = sensor_config.get('location', sensor_id)
        sensor_type = sensor_config['type']
        print(f"[{timestamp}] {location} ({sensor_type}): {value}")

        # 閾値チェック
        alert_msg = check_threshold(sensor_config, value)
        if alert_msg:
            send_alert(sensor_config, value, alert_msg)

    except ValueError:
        print(f"⚠️  無効なデータ: {payload}")

def print_summary():
    """サマリーを表示"""
    print("\n" + "=" * 50)
    print("📊 監視サマリー")
    print("=" * 50)

    for sensor in config['sensors']:
        sensor_id = sensor['id']
        location = sensor.get('location', sensor_id)

        if sensor_id in sensor_data and len(sensor_data[sensor_id]) > 0:
            data = sensor_data[sensor_id]
            print(f"\n【{location}】")
            print(f"  データ数: {len(data)}")
            print(f"  平均: {sum(data) / len(data):.2f}")
            print(f"  最小: {min(data):.2f}")
            print(f"  最大: {max(data):.2f}")

    print("=" * 50)

def main():
    global config

    # 設定ファイルを読み込み
    config = load_config('config.json')
    if config is None:
        return

    # 設定を検証
    if not validate_config(config):
        return

    # 設定情報を表示
    print("\n" + "=" * 50)
    print("⚙️  システム設定")
    print("=" * 50)
    print(f"ブローカー: {config['broker']['host']}:{config['broker']['port']}")
    print(f"センサー数: {len(config['sensors'])}")
    print(f"アラート: {'有効' if config['alerts']['enabled'] else '無効'}")
    print("=" * 50 + "\n")

    # MQTTクライアント設定
    broker_cfg = config['broker']
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "ConfigBasedSystem01")
    client.on_connect = on_connect
    client.on_message = on_message

    # 認証設定
    if broker_cfg.get('username') and broker_cfg.get('password'):
        client.username_pw_set(broker_cfg['username'], broker_cfg['password'])

    try:
        client.connect(broker_cfg['host'], broker_cfg['port'], 60)
        client.loop_forever()

    except KeyboardInterrupt:
        print("\n\n🛑 システムを停止します...")
        print_summary()

    finally:
        # クリーンアップ
        client.disconnect()
        print("\n✅ 停止完了")

if __name__ == "__main__":
    main()
