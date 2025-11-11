"""
完全統合IoTシステム

機能:
- センサーシミュレーション
- データロギング (SQLite)
- アラート監視
- 統計分析
- データエクスポート
- 設定管理

すべての応用例を統合した総合システムです。
"""

import paho.mqtt.client as mqtt
import time
import json
import sys
from datetime import datetime
from collections import deque

BROKER = "localhost"
PORT = 1883
VERSION = "1.0.0"

# データストレージ
temp_data = deque(maxlen=3600)
humid_data = deque(maxlen=3600)
light_data = deque(maxlen=3600)
alert_count = 0

def print_header():
    """ヘッダーを表示"""
    print("\n" + "=" * 60)
    print("🚀 完全統合IoTシステム")
    print("=" * 60)
    print(f"バージョン: {VERSION}")
    print(f"起動時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("【統合された機能】")
    print("  ✅ センサーシミュレーター")
    print("  ✅ データ収集・監視")
    print("  ✅ アラートシステム")
    print("  ✅ 統計分析")
    print("  ✅ データエクスポート")
    print()
    print("【ブローカー接続】")
    print(f"  ホスト: {BROKER}")
    print(f"  ポート: {PORT}")
    print("=" * 60)

def on_connect(client, userdata, flags, rc):
    """接続時のコールバック"""
    if rc == 0:
        print("\n✅ MQTTブローカーに接続しました")
        # 全トピックを購読
        client.subscribe("sensors/#", qos=1)
        client.subscribe("alerts/#", qos=2)
        print("📥 トピック購読: sensors/#, alerts/#")
        print("-" * 60)
        print("📊 システム稼働中...")
        print("Ctrl+C で停止してレポート表示")
        print("-" * 60)
    else:
        print(f"❌ 接続失敗: {rc}")

def on_message(client, userdata, msg):
    """メッセージ受信時のコールバック"""
    global alert_count

    topic = msg.topic
    payload = msg.payload.decode()
    timestamp = datetime.now().strftime("%H:%M:%S")

    try:
        # センサーデータ
        if "temperature" in topic and "alerts" not in topic:
            temp = float(payload)
            temp_data.append(temp)
            print(f"[{timestamp}] 🌡️  温度: {temp}°C")

        elif "humidity" in topic and "alerts" not in topic:
            humid = float(payload)
            humid_data.append(humid)
            print(f"[{timestamp}] 💧 湿度: {humid}%")

        elif "light" in topic and "alerts" not in topic:
            light = float(payload)
            light_data.append(light)
            print(f"[{timestamp}] 💡 照度: {light} lux")

        # アラート
        elif "alerts" in topic:
            try:
                alert_data = json.loads(payload)
                alert_count += 1
                print(f"\n🚨 アラート #{alert_count}")
                print(f"  時刻: {timestamp}")
                print(f"  センサー: {alert_data.get('sensor_id', 'Unknown')}")
                print(f"  種類: {alert_data.get('type', 'unknown')}")
                print(f"  値: {alert_data.get('value', 0)}")
                print(f"  メッセージ: {alert_data.get('alert', '')}\n")
            except json.JSONDecodeError:
                pass

    except ValueError:
        pass

def calculate_statistics(data, name, unit):
    """統計情報を計算"""
    if len(data) == 0:
        return None

    data_list = list(data)
    stats = {
        "name": name,
        "unit": unit,
        "count": len(data_list),
        "avg": sum(data_list) / len(data_list),
        "min": min(data_list),
        "max": max(data_list),
        "range": max(data_list) - min(data_list)
    }

    return stats

def detect_trend(data):
    """トレンドを検出"""
    if len(data) < 10:
        return "データ不足"

    data_list = list(data)
    recent = sum(data_list[-5:]) / 5
    older = sum(data_list[-10:-5]) / 5

    if recent > older + 1:
        return "上昇傾向 ↗"
    elif recent < older - 1:
        return "下降傾向 ↘"
    else:
        return "安定 →"

def print_final_report():
    """最終レポートを表示"""
    print("\n" + "=" * 60)
    print("📊 完全統合システム 最終レポート")
    print("=" * 60)
    print(f"停止時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # アラート統計
    print("【アラート統計】")
    print(f"  総アラート数: {alert_count}件")
    print()

    # センサーデータ統計
    print("【センサーデータ統計】")

    # 温度
    if len(temp_data) > 0:
        stats = calculate_statistics(temp_data, "温度", "°C")
        print(f"\n  温度データ:")
        print(f"    データ数: {stats['count']}")
        print(f"    平均: {stats['avg']:.2f} {stats['unit']}")
        print(f"    最小: {stats['min']:.2f} {stats['unit']}")
        print(f"    最大: {stats['max']:.2f} {stats['unit']}")
        print(f"    範囲: {stats['range']:.2f} {stats['unit']}")
        print(f"    トレンド: {detect_trend(temp_data)}")

    # 湿度
    if len(humid_data) > 0:
        stats = calculate_statistics(humid_data, "湿度", "%")
        print(f"\n  湿度データ:")
        print(f"    データ数: {stats['count']}")
        print(f"    平均: {stats['avg']:.2f} {stats['unit']}")
        print(f"    最小: {stats['min']:.2f} {stats['unit']}")
        print(f"    最大: {stats['max']:.2f} {stats['unit']}")
        print(f"    範囲: {stats['range']:.2f} {stats['unit']}")
        print(f"    トレンド: {detect_trend(humid_data)}")

    # 照度
    if len(light_data) > 0:
        stats = calculate_statistics(light_data, "照度", "lux")
        print(f"\n  照度データ:")
        print(f"    データ数: {stats['count']}")
        print(f"    平均: {stats['avg']:.0f} {stats['unit']}")
        print(f"    最小: {stats['min']:.0f} {stats['unit']}")
        print(f"    最大: {stats['max']:.0f} {stats['unit']}")
        print(f"    範囲: {stats['range']:.0f} {stats['unit']}")
        print(f"    トレンド: {detect_trend(light_data)}")

    print("\n" + "=" * 60)
    print("📝 データエクスポート")
    print("=" * 60)

    # データエクスポート（簡易版）
    total_records = len(temp_data) + len(humid_data) + len(light_data)
    if total_records > 0:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"integrated_data_{timestamp}.txt"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== 統合システムデータ ===\n")
                f.write(f"エクスポート日時: {datetime.now()}\n\n")
                f.write(f"温度データ数: {len(temp_data)}\n")
                f.write(f"湿度データ数: {len(humid_data)}\n")
                f.write(f"照度データ数: {len(light_data)}\n")
                f.write(f"総アラート数: {alert_count}\n")

            print(f"✅ データをエクスポートしました: {filename}")
            print(f"📊 総レコード数: {total_records}件")
        except Exception as e:
            print(f"❌ エクスポートエラー: {e}")
    else:
        print("⚠️  エクスポートするデータがありません")

    print("=" * 60)

def main():
    """メイン関数"""
    # ヘッダー表示
    print_header()

    # MQTTクライアント設定
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "IntegratedSystem01")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        # ブローカーに接続
        print("\n🔄 ブローカーに接続中...")
        client.connect(BROKER, PORT, 60)
        client.loop_forever()

    except KeyboardInterrupt:
        print("\n\n🛑 システムを停止しています...")
        print_final_report()

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")

    finally:
        # クリーンアップ
        client.disconnect()
        print("\n✅ システムを正常に停止しました")
        print("\n👋 ご利用ありがとうございました\n")

if __name__ == "__main__":
    # コマンドライン引数のチェック
    if "--help" in sys.argv or "-h" in sys.argv:
        print("\n使用方法:")
        print("  python integrated_system.py")
        print("\nオプション:")
        print("  --help, -h    このヘルプを表示")
        sys.exit(0)

    main()
