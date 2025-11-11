"""
高度なダッシュボード

機能:
- 温度、湿度、照度を同時にグラフ表示
- 統計情報の表示（平均、最大、最小、範囲）
- データの自動保存（CSV形式）
- センサーステータス監視
"""

import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
from datetime import datetime
import csv
import os

BROKER = "localhost"
PORT = 1883

# データを保存（最大100個）
temp_data = deque(maxlen=100)
humid_data = deque(maxlen=100)
light_data = deque(maxlen=100)
timestamps = deque(maxlen=100)
sensor_status = "UNKNOWN"

# データ保存用のリスト
all_data = []

def on_connect(client, userdata, flags, rc):
    """接続時のコールバック"""
    if rc == 0:
        print("✅ ブローカーに接続")
        print(f"📡 {BROKER}:{PORT}")
        # 全センサーデータを購読
        client.subscribe("sensors/#", qos=1)
        client.subscribe("alerts/#", qos=2)
        print("📥 トピック購読: sensors/#, alerts/#")
        print("-" * 50)
    else:
        print(f"❌ 接続失敗: {rc}")

def on_message(client, userdata, msg):
    """メッセージ受信時のコールバック"""
    global sensor_status

    topic = msg.topic
    payload = msg.payload.decode()
    timestamp = datetime.now()

    try:
        if "temperature" in topic and "alerts" not in topic:
            temp = float(payload)
            temp_data.append(temp)
            timestamps.append(timestamp)

            # データを記録
            record = {
                'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'sensor_id': 'MultiSensor01',
                'temperature': temp,
                'humidity': None,
                'light': None
            }
            all_data.append(record)

            print(f"📥 温度: {temp}°C")

        elif "humidity" in topic and "alerts" not in topic:
            humid = float(payload)
            humid_data.append(humid)

            # 最後のレコードを更新
            if all_data and all_data[-1]['humidity'] is None:
                all_data[-1]['humidity'] = humid

            print(f"📥 湿度: {humid}%")

        elif "light" in topic and "alerts" not in topic:
            light = float(payload)
            light_data.append(light)

            # 最後のレコードを更新
            if all_data and all_data[-1]['light'] is None:
                all_data[-1]['light'] = light

            print(f"📥 照度: {light} lux")

        elif "status" in topic:
            sensor_status = payload
            emoji = "🟢" if payload == "ONLINE" else "🔴"
            retain_mark = "(Retain)" if msg.retain else ""
            print(f"{emoji} ステータス: {payload} {retain_mark}")

        elif "alerts" in topic:
            print(f"🚨 アラート: {payload}")

    except ValueError:
        print(f"⚠️  不正なデータ: {payload}")

def get_stats(data):
    """統計情報を計算"""
    if len(data) == 0:
        return "N/A", "N/A", "N/A", "N/A"

    latest = data[-1]
    avg = sum(data) / len(data)
    min_val = min(data)
    max_val = max(data)

    return latest, avg, min_val, max_val

def save_data_to_csv():
    """データをCSVファイルに保存"""
    if len(all_data) == 0:
        print("💾 保存するデータがありません")
        return

    # ファイル名を生成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sensor_data_{timestamp}.csv"

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['timestamp', 'sensor_id', 'temperature', 'humidity', 'light']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            for record in all_data:
                writer.writerow(record)

        print(f"💾 データを保存しました: {filename}")
        print(f"📊 保存件数: {len(all_data)}件")

    except Exception as e:
        print(f"❌ データ保存エラー: {e}")

def init_plot():
    """グラフの初期化"""
    ax1.set_xlim(0, 100)
    ax1.set_ylim(15, 35)
    ax2.set_xlim(0, 100)
    ax2.set_ylim(20, 80)
    ax3.set_xlim(0, 100)
    ax3.set_ylim(0, 1000)
    return line1, line2, line3

def update_plot(frame):
    """グラフの更新"""
    # 温度グラフ
    if len(temp_data) > 0:
        line1.set_data(range(len(temp_data)), list(temp_data))
        latest, avg, min_val, max_val = get_stats(temp_data)
        ax1.set_title(
            f'温度: {latest:.1f}°C (平均: {avg:.1f}°C, 最小: {min_val:.1f}°C, 最大: {max_val:.1f}°C)',
            fontsize=10
        )
        ax1.set_xlim(0, max(100, len(temp_data)))

    # 湿度グラフ
    if len(humid_data) > 0:
        line2.set_data(range(len(humid_data)), list(humid_data))
        latest, avg, min_val, max_val = get_stats(humid_data)
        ax2.set_title(
            f'湿度: {latest:.1f}% (平均: {avg:.1f}%, 最小: {min_val:.1f}%, 最大: {max_val:.1f}%)',
            fontsize=10
        )
        ax2.set_xlim(0, max(100, len(humid_data)))

    # 照度グラフ
    if len(light_data) > 0:
        line3.set_data(range(len(light_data)), list(light_data))
        latest, avg, min_val, max_val = get_stats(light_data)
        ax3.set_title(
            f'照度: {latest:.0f} lux (平均: {avg:.0f} lux, 最小: {min_val:.0f} lux, 最大: {max_val:.0f} lux)',
            fontsize=10
        )
        ax3.set_xlim(0, max(100, len(light_data)))

    # メインタイトルにステータスとデータ件数を表示
    status_emoji = "🟢" if sensor_status == "ONLINE" else "🔴"
    fig.suptitle(
        f'高度なダッシュボード {status_emoji} {sensor_status} | データ件数: {len(all_data)}',
        fontsize=14, fontweight='bold'
    )

    return line1, line2, line3

def main():
    global fig, ax1, ax2, ax3, line1, line2, line3

    # MQTTクライアント設定
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "AdvancedDashboard01")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()

        print("📊 高度なダッシュボード起動")
        print("💾 データは自動的に保存されます")
        print("グラフウィンドウを閉じて終了")
        print("-" * 50)

        # グラフの初期化
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10))

        # 温度グラフ
        line1, = ax1.plot([], [], 'r-', linewidth=2, marker='o', markersize=3)
        ax1.set_ylabel('温度 (°C)', fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=30, color='r', linestyle='--', alpha=0.5, linewidth=2, label='高温警告 (30°C)')
        ax1.axhline(y=18, color='b', linestyle='--', alpha=0.5, linewidth=2, label='低温警告 (18°C)')
        ax1.legend(loc='upper right', fontsize=8)

        # 湿度グラフ
        line2, = ax2.plot([], [], 'b-', linewidth=2, marker='o', markersize=3)
        ax2.set_ylabel('湿度 (%)', fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5, linewidth=2, label='高湿度警告 (70%)')
        ax2.axhline(y=30, color='b', linestyle='--', alpha=0.5, linewidth=2, label='低湿度警告 (30%)')
        ax2.legend(loc='upper right', fontsize=8)

        # 照度グラフ
        line3, = ax3.plot([], [], 'g-', linewidth=2, marker='o', markersize=3)
        ax3.set_xlabel('データポイント', fontsize=10)
        ax3.set_ylabel('照度 (lux)', fontsize=10)
        ax3.grid(True, alpha=0.3)

        plt.tight_layout()

        # アニメーション開始
        ani = animation.FuncAnimation(
            fig, update_plot, init_func=init_plot,
            interval=1000, blit=True, cache_frame_data=False
        )

        plt.show()

    except KeyboardInterrupt:
        print("\n🛑 ダッシュボードを停止します...")

    finally:
        # データを保存
        save_data_to_csv()

        # クリーンアップ
        client.loop_stop()
        client.disconnect()
        print("✅ 停止完了")

if __name__ == "__main__":
    main()
