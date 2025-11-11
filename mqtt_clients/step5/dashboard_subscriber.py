"""
リアルタイム温度ダッシュボード (Subscriber)

機能:
- 温度データをリアルタイムでグラフ表示
- センサーのステータスを監視
- matplotlib でアニメーション表示
"""

import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
from datetime import datetime

BROKER = "localhost"
PORT = 1883

# データを保存（最大50個）
temperature_data = deque(maxlen=50)
time_data = deque(maxlen=50)
sensor_status = "UNKNOWN"

def on_connect(client, userdata, flags, rc):
    """接続時のコールバック"""
    if rc == 0:
        print("✅ ブローカーに接続")
        print(f"📡 {BROKER}:{PORT}")
        # ワイルドカードで全センサートピックを購読
        client.subscribe("sensor/#", qos=1)
        print("📥 トピック購読: sensor/#")
    else:
        print(f"❌ 接続失敗: {rc}")

def on_message(client, userdata, msg):
    """メッセージ受信時のコールバック"""
    global sensor_status

    topic = msg.topic
    payload = msg.payload.decode()

    if topic == "sensor/temperature":
        # 温度データを保存
        try:
            temp = float(payload)
            temperature_data.append(temp)
            time_data.append(datetime.now())
            print(f"📥 受信: {temp}°C")
        except ValueError:
            print(f"⚠️  不正なデータ: {payload}")

    elif topic == "sensor/status":
        # ステータス更新
        sensor_status = payload
        emoji = "🟢" if payload == "ONLINE" else "🔴"
        retain_mark = "(Retain)" if msg.retain else ""
        print(f"{emoji} ステータス: {payload} {retain_mark}")

def init_plot():
    """グラフの初期化"""
    ax.set_xlim(0, 50)
    ax.set_ylim(15, 35)
    return line,

def update_plot(frame):
    """グラフの更新（アニメーション）"""
    if len(temperature_data) > 0:
        # データをプロット
        line.set_data(range(len(temperature_data)), list(temperature_data))

        # タイトルにステータスを表示
        status_emoji = "🟢" if sensor_status == "ONLINE" else "🔴"
        ax.set_title(f'リアルタイム温度モニター {status_emoji} {sensor_status}', fontsize=14, fontweight='bold')

        # 最新の温度を表示
        latest_temp = temperature_data[-1]
        ax.set_ylabel(f'温度 (°C) - 最新: {latest_temp}°C', fontsize=12)

        # X軸のラベルを調整
        ax.set_xlim(0, max(50, len(temperature_data)))

    return line,

def main():
    global fig, ax, line

    # MQTTクライアント設定
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Dashboard01")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()

        print("-" * 40)
        print("📊 ダッシュボード起動")
        print("グラフウィンドウを閉じて終了")
        print("-" * 40)

        # グラフの初期化
        fig, ax = plt.subplots(figsize=(12, 6))
        line, = ax.plot([], [], 'b-', linewidth=2, marker='o', markersize=4)
        ax.set_xlabel('データポイント', fontsize=12)
        ax.set_ylabel('温度 (°C)', fontsize=12)
        ax.set_title('リアルタイム温度モニター', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

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
