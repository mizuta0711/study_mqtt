# IoTシステム構築実践

## 🎯 この章の目標

実用的なIoTシステムを構築します。具体的には：
- 温度センサーをシミュレートするPublisher
- リアルタイムでグラフ表示するSubscriber（ダッシュボード）

---

## 📊 システム概要

```
[温度センサー] ─(Publish)→ [MQTT Broker] ─(Subscribe)→ [ダッシュボード]
   (Publisher)              (Mosquitto)               (Subscriber + Graph)
```

**トピック設計:**
- `sensor/temperature` - 温度データ（QoS 0、高速送信）
- `sensor/status` - センサー状態（QoS 1、Retain有効）

---

## 🌡️ ステップ1：温度センサーPublisher

### 基本的な実装

温度センサーをシミュレートして、1秒ごとにランダムな温度データを送信します。

```python
# sensor_publisher.py
import paho.mqtt.client as mqtt
import random
import time

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        # ステータスをRetainで送信（新規Subscriberがすぐ状態を知れる）
        client.publish("sensor/status", "ONLINE", qos=1, retain=True)
        print("✅ センサー起動完了")
    else:
        print(f"❌ 接続失敗: {rc}")

# クライアント作成（VERSION1を使用）
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "TemperatureSensor01")

# Last Will設定（異常終了時に自動送信）
client.will_set("sensor/status", "OFFLINE", qos=1, retain=True)

client.on_connect = on_connect
client.connect("localhost", 1883, 60)
client.loop_start()

print("🌡️  温度センサー稼働中...")
print("Ctrl+C で停止")

try:
    while True:
        # 温度データ生成（20.0〜30.0°C）
        temperature = round(random.uniform(20.0, 30.0), 2)

        # QoS 0で高速送信（リアルタイム性重視）
        client.publish("sensor/temperature", str(temperature), qos=0)
        print(f"📤 送信: {temperature}°C")

        time.sleep(1)

except KeyboardInterrupt:
    print("\n🛑 センサーを停止します...")
    # 正常停止時もステータスを更新
    client.publish("sensor/status", "OFFLINE", qos=1, retain=True)
    client.loop_stop()
    client.disconnect()
    print("✅ 停止完了")
```

**コードファイル**: [../../mqtt_clients/step5/sensor_publisher.py](../../mqtt_clients/step5/sensor_publisher.py)

### ポイント解説

1. **Retain + QoS 1 でステータス管理**
   - `sensor/status` はRetainを有効にすることで、新規Subscriberが接続時に最新の状態をすぐ取得できる
   - QoS 1で確実に配信

2. **Last Willで異常終了を検知**
   - `Ctrl+C` で強制終了すると、BrokerがLast Willを発火
   - ダッシュボード側でセンサーの異常を検知できる

3. **温度データはQoS 0で高速送信**
   - リアルタイム性重視
   - 多少のパケットロスは許容（次のデータがすぐ来るため）

---

## 📈 ステップ2：ダッシュボードSubscriber

### リアルタイムグラフ表示

matplotlibを使って、受信した温度データをリアルタイムでグラフ表示します。

```python
# dashboard_subscriber.py
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
from datetime import datetime

# データを保存（最大50個）
temperature_data = deque(maxlen=50)
time_data = deque(maxlen=50)
sensor_status = "UNKNOWN"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ ブローカーに接続")
        # ワイルドカードで全センサートピックを購読
        client.subscribe("sensor/#", qos=1)
    else:
        print(f"❌ 接続失敗: {rc}")

def on_message(client, userdata, msg):
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
        print(f"{emoji} ステータス: {payload}")

# MQTTクライアント設定
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Dashboard01")
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_start()

# グラフの初期化
fig, ax = plt.subplots(figsize=(10, 6))
line, = ax.plot([], [], 'b-', linewidth=2)
ax.set_xlabel('時刻')
ax.set_ylabel('温度 (°C)')
ax.set_title('リアルタイム温度モニター')
ax.grid(True)

def init():
    ax.set_xlim(0, 50)
    ax.set_ylim(15, 35)
    return line,

def update(frame):
    if len(temperature_data) > 0:
        # データをプロット
        line.set_data(range(len(temperature_data)), list(temperature_data))

        # タイトルにステータスを表示
        status_emoji = "🟢" if sensor_status == "ONLINE" else "🔴"
        ax.set_title(f'リアルタイム温度モニター {status_emoji} {sensor_status}')

        # 最新の温度を表示
        if len(temperature_data) > 0:
            latest_temp = temperature_data[-1]
            ax.set_ylabel(f'温度 (°C) - 最新: {latest_temp}°C')

    return line,

# アニメーション開始
ani = animation.FuncAnimation(
    fig, update, init_func=init,
    interval=1000, blit=True, cache_frame_data=False
)

print("📊 ダッシュボード起動")
print("ウィンドウを閉じて終了")
plt.show()

# クリーンアップ
client.loop_stop()
client.disconnect()
```

**コードファイル**: [../../mqtt_clients/step5/dashboard_subscriber.py](../../mqtt_clients/step5/dashboard_subscriber.py)

### ポイント解説

1. **dequeで固定サイズのデータ保持**
   - `maxlen=50` で最新50個のデータのみ保持
   - メモリ効率が良い

2. **ワイルドカード購読**
   - `sensor/#` で `sensor/` 配下の全トピックを購読
   - 温度データとステータスを一度に購読できる

3. **matplotlibアニメーション**
   - `FuncAnimation` で1秒ごとにグラフを更新
   - リアルタイムでデータが流れる様子を視覚化

---

## 🚀 ステップ3：動作確認

### 1. Mosquittoブローカーを起動

```bash
docker run -it -p 1883:1883 -v ./mqtt/config:/mosquitto/config eclipse-mosquitto
```

### 2. ダッシュボードを起動（ターミナル1）

```bash
python mqtt_clients/step5/dashboard_subscriber.py
```

グラフウィンドウが開きます。

### 3. センサーを起動（ターミナル2）

```bash
python mqtt_clients/step5/sensor_publisher.py
```

### 4. 確認ポイント

- ✅ グラフがリアルタイムで更新される
- ✅ タイトルに「🟢 ONLINE」と表示される
- ✅ `Ctrl+C` でセンサーを停止すると「🔴 OFFLINE」に変わる（Last Will発火）
- ✅ センサーを再起動すると、すぐに「🟢 ONLINE」に戻る（Retain機能）

---

## 🔧 実験：Last Willの確認

### センサーを異常終了させる

1. ダッシュボードを起動
2. センサーを起動
3. **センサーのターミナルを強制終了**（ウィンドウを閉じる、またはタスクキル）

**結果**: ダッシュボードに「🔴 OFFLINE」が表示される

これは、Brokerがセンサーの異常終了を検知し、Last Willを発火したためです。

---

## 🎨 カスタマイズのアイデア

### 1. 複数のグラフを表示

```python
# 温度、湿度、気圧を同時に表示
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))
```

### 2. アラート機能を追加

```python
if temp > 28.0:
    print("🚨 アラート: 高温警報！")
    # メール送信やSlack通知など
```

### 3. データをCSVに保存

```python
import csv

with open('temperature_log.csv', 'a') as f:
    writer = csv.writer(f)
    writer.writerow([datetime.now(), temperature])
```

---

## 📚 より詳しく学ぶ

- **センサーシミュレーション**: [02_センサーシミュレーション詳細.md](./02_センサーシミュレーション詳細.md)
- **データ可視化**: [03_データ可視化詳細.md](./03_データ可視化詳細.md)
- **応用コード**: [05_応用コード集.md](./05_応用コード集.md)

---

## ✅ チェックポイント

- [ ] センサーPublisherが動作する
- [ ] ダッシュボードでグラフが表示される
- [ ] リアルタイムでデータが更新される
- [ ] Last Willが正しく動作する
- [ ] Retainメッセージが機能している

---

**次のステップ**: より高度なセンサーシミュレーションや複数センサーの管理を学びましょう！
