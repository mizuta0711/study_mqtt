"""
統計分析ツール

機能:
- センサーデータの統計分析
- 平均、中央値、標準偏差などの計算
- トレンド検出
- 定期的な統計レポート表示
"""

import paho.mqtt.client as mqtt
from collections import deque
from datetime import datetime
import time
import threading

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("⚠️  numpy がインストールされていません。基本統計のみ利用可能です。")
    print("   高度な統計機能を使う場合は pip install numpy を実行してください。")

BROKER = "localhost"
PORT = 1883

# データを保存（最大3600個 = 1時間分）
temp_data = deque(maxlen=3600)
humid_data = deque(maxlen=3600)
light_data = deque(maxlen=3600)

# 分析開始時刻
start_time = None
running = True

def on_connect(client, userdata, flags, rc):
    """接続時のコールバック"""
    global start_time
    if rc == 0:
        print("✅ ブローカーに接続")
        print(f"📡 {BROKER}:{PORT}")
        # 全センサーデータを購読
        client.subscribe("sensors/#", qos=1)
        print("📥 トピック購読: sensors/#")
        print("-" * 50)
        print("📊 統計分析システム起動")
        print("60秒ごとに統計レポートを表示します")
        print("Ctrl+C で停止")
        print("-" * 50)
        start_time = datetime.now()
    else:
        print(f"❌ 接続失敗: {rc}")

def on_message(client, userdata, msg):
    """メッセージ受信時のコールバック"""
    topic = msg.topic
    payload = msg.payload.decode()

    try:
        if "temperature" in topic and "alerts" not in topic:
            temp = float(payload)
            temp_data.append(temp)

        elif "humidity" in topic and "alerts" not in topic:
            humid = float(payload)
            humid_data.append(humid)

        elif "light" in topic and "alerts" not in topic:
            light = float(payload)
            light_data.append(light)

    except ValueError:
        pass

def analyze_basic_stats(data, unit=""):
    """基本統計量を計算"""
    if len(data) == 0:
        return None

    data_list = list(data)

    stats = {
        "データ数": len(data_list),
        "平均": sum(data_list) / len(data_list),
        "最大値": max(data_list),
        "最小値": min(data_list),
        "範囲": max(data_list) - min(data_list)
    }

    # 中央値
    sorted_data = sorted(data_list)
    n = len(sorted_data)
    if n % 2 == 0:
        stats["中央値"] = (sorted_data[n//2-1] + sorted_data[n//2]) / 2
    else:
        stats["中央値"] = sorted_data[n//2]

    # 標準偏差（numpyがあれば）
    if HAS_NUMPY:
        stats["標準偏差"] = np.std(data_list)

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

def print_statistics():
    """統計情報を表示"""
    global start_time

    print("\n" + "=" * 60)
    print("📊 統計分析レポート")
    print("=" * 60)

    if start_time:
        print(f"データ取得開始: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"現在時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

    # 温度統計
    if len(temp_data) > 0:
        print("【温度データ】")
        stats = analyze_basic_stats(temp_data, "°C")
        for key, value in stats.items():
            if key == "データ数":
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value:.2f} °C")
        trend = detect_trend(temp_data)
        print(f"  トレンド: {trend}")
        print()

    # 湿度統計
    if len(humid_data) > 0:
        print("【湿度データ】")
        stats = analyze_basic_stats(humid_data, "%")
        for key, value in stats.items():
            if key == "データ数":
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value:.2f} %")
        trend = detect_trend(humid_data)
        print(f"  トレンド: {trend}")
        print()

    # 照度統計
    if len(light_data) > 0:
        print("【照度データ】")
        stats = analyze_basic_stats(light_data, "lux")
        for key, value in stats.items():
            if key == "データ数":
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value:.0f} lux")
        trend = detect_trend(light_data)
        print(f"  トレンド: {trend}")
        print()

    print("=" * 60)

def periodic_analysis():
    """定期的に統計分析を実行"""
    global running
    time.sleep(60)  # 最初の60秒は待機

    while running:
        if len(temp_data) > 0 or len(humid_data) > 0 or len(light_data) > 0:
            print_statistics()
        time.sleep(60)  # 60秒ごと

def main():
    global running

    # MQTTクライアント設定
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "StatsAnalyzer01")
    client.on_connect = on_connect
    client.on_message = on_message

    # 統計分析スレッドを起動
    analysis_thread = threading.Thread(target=periodic_analysis, daemon=True)
    analysis_thread.start()

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_forever()

    except KeyboardInterrupt:
        print("\n\n🛑 統計分析システムを停止します...")
        running = False
        print_statistics()  # 最終レポート

    finally:
        # クリーンアップ
        client.disconnect()
        print("\n✅ 停止完了")

if __name__ == "__main__":
    main()
