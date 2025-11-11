"""
複数グラフ統合ダッシュボード

機能:
- 温度、湿度、照度を同時にグラフ表示
- センサーステータス監視
- 統計情報表示
"""

import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
from datetime import datetime

BROKER = "localhost"
PORT = 1883

# データを保存（最大50個）
temp_data = deque(maxlen=50)
humid_data = deque(maxlen=50)
light_data = deque(maxlen=50)
sensor_status = "UNKNOWN"

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

    try:
        if "temperature" in topic and "alerts" not in topic:
            temp = float(payload)
            temp_data.append(temp)
            print(f"📥 温度: {temp}°C")

        elif "humidity" in topic and "alerts" not in topic:
            humid = float(payload)
            humid_data.append(humid)
            print(f"📥 湿度: {humid}%")

        elif "light" in topic and "alerts" not in topic:
            light = float(payload)
            light_data.append(light)
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
        return "N/A", "N/A", "N/A"

    latest = data[-1]
    avg = sum(data) / len(data)
    min_val = min(data)
    max_val = max(data)

    return latest, avg, min_val, max_val

def init_plot():
    """グラフの初期化"""
    ax1.set_xlim(0, 50)
    ax1.set_ylim(15, 35)
    ax2.set_xlim(0, 50)
    ax2.set_ylim(20, 80)
    ax3.set_xlim(0, 50)
    ax3.set_ylim(0, 1000)
    return line1, line2, line3

def update_plot(frame):
    """グラフの更新"""
    # 温度グラフ
    if len(temp_data) > 0:
        line1.set_data(range(len(temp_data)), list(temp_data))
        latest, avg, min_val, max_val = get_stats(temp_data)
        ax1.set_title(
            f'温度: {latest:.1f}°C (平均: {avg:.1f}°C, 範囲: {min_val:.1f}〜{max_val:.1f}°C)',
            fontsize=10
        )
        ax1.set_xlim(0, max(50, len(temp_data)))

    # 湿度グラフ
    if len(humid_data) > 0:
        line2.set_data(range(len(humid_data)), list(humid_data))
        latest, avg, min_val, max_val = get_stats(humid_data)
        ax2.set_title(
            f'湿度: {latest:.1f}% (平均: {avg:.1f}%, 範囲: {min_val:.1f}〜{max_val:.1f}%)',
            fontsize=10
        )
        ax2.set_xlim(0, max(50, len(humid_data)))

    # 照度グラフ
    if len(light_data) > 0:
        line3.set_data(range(len(light_data)), list(light_data))
        latest, avg, min_val, max_val = get_stats(light_data)
        ax3.set_title(
            f'照度: {latest:.0f} lux (平均: {avg:.0f} lux, 範囲: {min_val:.0f}〜{max_val:.0f} lux)',
            fontsize=10
        )
        ax3.set_xlim(0, max(50, len(light_data)))

    # メインタイトルにステータス表示
    status_emoji = "🟢" if sensor_status == "ONLINE" else "🔴"
    fig.suptitle(f'マルチセンサーダッシュボード {status_emoji} {sensor_status}',
                 fontsize=14, fontweight='bold')

    return line1, line2, line3

def main():
    global fig, ax1, ax2, ax3, line1, line2, line3

    # MQTTクライアント設定
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "MultiDashboard01")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()

        print("📊 マルチグラフダッシュボード起動")
        print("グラフウィンドウを閉じて終了")
        print("-" * 50)

        # グラフの初期化
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))

        # 温度グラフ
        line1, = ax1.plot([], [], 'r-', linewidth=2, marker='o', markersize=3)
        ax1.set_ylabel('温度 (°C)', fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=30, color='r', linestyle='--', alpha=0.5, label='高温警告')
        ax1.axhline(y=18, color='b', linestyle='--', alpha=0.5, label='低温警告')
        ax1.legend(loc='upper right', fontsize=8)

        # 湿度グラフ
        line2, = ax2.plot([], [], 'b-', linewidth=2, marker='o', markersize=3)
        ax2.set_ylabel('湿度 (%)', fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5, label='高湿度警告')
        ax2.axhline(y=30, color='b', linestyle='--', alpha=0.5, label='低湿度警告')
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
        # クリーンアップ
        client.loop_stop()
        client.disconnect()
        print("✅ 停止完了")

if __name__ == "__main__":
    main()
