# 実験4：全機能統合センサー

## 📖 概要

このプログラムは、MQTTの主要機能（QoS、Retain、Last Will）をすべて統合した実践的な温度センサーシミュレータです。実際のIoTデバイスで使用される設計パターンを学べます。

## 🎯 学習目標

- QoS、Retain、Last Willを組み合わせた実装パターンを習得
- データの重要度に応じた適切なQoSレベルの選択
- プロダクションレディなセンサーコードの書き方
- 複数センサーインスタンスの管理方法

## 🔍 実装されている機能

### 1. Last Will（遺言）
- **トピック**: `sensors/{SENSOR_ID}/status`
- **メッセージ**: `OFFLINE`
- **QoS**: 2（確実な配信）
- **Retain**: 有効（最新状態を保持）

### 2. ステータス通知
- **トピック**: `sensors/{SENSOR_ID}/status`
- **メッセージ**: `ONLINE`
- **QoS**: 1（確認応答あり）
- **Retain**: 有効

### 3. 温度データ
- **トピック**: `sensors/{SENSOR_ID}/temperature`
- **QoS**: 0（高速送信）
- **頻度**: 2秒ごと

### 4. 異常アラート
- **トピック**: `sensors/{SENSOR_ID}/alert`
- **QoS**: 2（重複なし保証）
- **条件**: 温度が18°C未満または32°C超過

## 🚀 使い方

### 前提条件

1. MQTTブローカー（Mosquitto）がlocalhost:1883で起動していること
2. paho-mqttライブラリがインストールされていること

```bash
pip install paho-mqtt
```

### 実行方法

#### 単一センサーの起動

```bash
python ultimate_sensor.py
```

デフォルトのセンサーID（`Sensor01`）で起動します。

#### カスタムセンサーIDで起動

```bash
python ultimate_sensor.py Sensor02
python ultimate_sensor.py TempSensor_Room1
```

#### 複数センサーの同時実行

複数のターミナルで異なるIDを指定して実行：

```bash
# ターミナル1
python ultimate_sensor.py Sensor01

# ターミナル2
python ultimate_sensor.py Sensor02

# ターミナル3
python ultimate_sensor.py Sensor03
```

### 実行例

```
🌡️  Sensor01 稼働中...
💡 機能:
  - Last Will (QoS 2 + Retain)
  - 温度データ (QoS 0)
  - 異常アラート (QoS 2)

✅ Sensor01 起動完了
📊 23.4°C
📊 25.7°C
🚨 異常値: 33.2°C
📊 28.1°C
📊 19.5°C
🚨 異常値: 16.8°C
```

## 💡 設計の意図

### QoSレベルの使い分け

| データ種別 | QoS | 理由 |
|----------|-----|------|
| 温度データ | 0 | 頻繁に送信されるため、多少のロスは許容可能。高速性を優先 |
| ステータス（ONLINE） | 1 | 起動通知は重要だが、重複しても問題ない |
| Last Will（OFFLINE） | 2 | 切断検知は極めて重要。重複も欠損も許されない |
| 異常アラート | 2 | クリティカルな通知。確実に1回だけ届ける必要がある |

### Retainの活用

```python
client.publish(f"sensors/{SENSOR_ID}/status", "ONLINE", qos=1, retain=True)
```

- **メリット**: 監視システムが起動した時、センサーの現在状態を即座に取得できる
- **Last Willにも適用**: 切断時も状態が保持される

### トピック階層設計

```
sensors/
  └─ {SENSOR_ID}/
       ├─ status       ← ONLINE/OFFLINE
       ├─ temperature  ← 温度値
       └─ alert        ← 異常アラート
```

- 階層的に整理されており、購読しやすい
- ワイルドカード（`sensors/+/temperature`）で一括購読可能

## 🔬 実験方法

### 1. 基本動作の確認

Subscriberで状態を監視：

```bash
mosquitto_sub -t "sensors/#" -v
```

出力例：
```
sensors/Sensor01/status ONLINE
sensors/Sensor01/temperature 24.3
sensors/Sensor01/temperature 26.7
sensors/Sensor01/alert 異常値: 33.1°C
```

### 2. Last Willのテスト

1. センサーを起動
2. Subscriberで`sensors/+/status`を監視
3. センサーをCtrl+Cで強制終了
4. `OFFLINE`メッセージが配信されることを確認

```bash
# 別ターミナル
mosquitto_sub -t "sensors/+/status" -v
```

### 3. Retainメッセージの確認

センサー起動後、新しいSubscriberを接続：

```bash
mosquitto_sub -t "sensors/Sensor01/status" -v
```

→ 即座に`ONLINE`が受信される（Retain機能）

### 4. 複数センサーのシミュレーション

3つのターミナルで異なるセンサーを起動し、統合監視：

```bash
# 監視用ターミナル
mosquitto_sub -t "sensors/+/alert" -v
```

→ すべてのセンサーからのアラートを一括監視

## 🎓 応用例

### 1. データ可視化

Subscriberでデータを受信して、matplotlibでリアルタイムグラフ化：

```python
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
from collections import deque

temps = deque(maxlen=50)

def on_message(client, userdata, msg):
    if "temperature" in msg.topic:
        temp = float(msg.payload.decode())
        temps.append(temp)
        # グラフ更新処理
```

### 2. データベース保存

```python
import sqlite3

def on_message(client, userdata, msg):
    if "temperature" in msg.topic:
        sensor_id = msg.topic.split('/')[1]
        temp = float(msg.payload.decode())

        conn = sqlite3.connect("sensor_data.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO temperatures (sensor_id, value, timestamp) VALUES (?, ?, datetime('now'))",
            (sensor_id, temp)
        )
        conn.commit()
```

### 3. Webダッシュボード

FlaskやDashを使ってリアルタイムダッシュボードを構築：

```python
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

def on_message(client, userdata, msg):
    data = {
        "topic": msg.topic,
        "payload": msg.payload.decode()
    }
    socketio.emit("mqtt_message", data)
```

### 4. アラート通知

```python
def on_message(client, userdata, msg):
    if "alert" in msg.topic:
        sensor_id = msg.topic.split('/')[1]
        alert_msg = msg.payload.decode()

        # メール通知
        send_email(f"Alert from {sensor_id}: {alert_msg}")

        # Slack通知
        send_slack_message(f"🚨 {sensor_id}: {alert_msg}")
```

## 📊 監視システムとの統合

### 統合監視スクリプト

```python
# monitor_all_sensors.py
import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    sensor_id = msg.topic.split('/')[1]
    data_type = msg.topic.split('/')[2]
    payload = msg.payload.decode()

    if data_type == "status":
        print(f"{'🟢' if payload == 'ONLINE' else '🔴'} {sensor_id}: {payload}")
    elif data_type == "alert":
        print(f"🚨 {sensor_id}: {payload}")
    elif data_type == "temperature":
        print(f"🌡️  {sensor_id}: {payload}°C")

client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.subscribe("sensors/#")
client.loop_forever()
```

## ⚠️ プロダクション環境への展開

### セキュリティ強化

```python
# 認証情報の設定
client.username_pw_set("sensor_user", "secure_password")

# TLS/SSL暗号化
client.tls_set(ca_certs="ca.crt")
client.connect("mqtt.example.com", 8883, 60)  # ポート8883
```

### エラーハンドリング

```python
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"予期しない切断。再接続を試みます...")
        try:
            client.reconnect()
        except Exception as e:
            print(f"再接続失敗: {e}")

client.on_disconnect = on_disconnect
```

### ログ記録

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{SENSOR_ID}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(SENSOR_ID)
logger.info(f"センサー起動: {SENSOR_ID}")
```

## 🎓 まとめ

この統合センサーを通じて、以下が学べます：

- MQTTの主要機能を組み合わせた実践的な実装
- データの重要度に応じたQoS選択の判断基準
- プロダクション環境を見据えた設計パターン
- スケーラブルなIoTシステムの構築方法

**重要なポイント**: 実際のIoTシステムでは、すべてのメッセージに高いQoSを使うのではなく、データの性質に応じて適切なレベルを選択することが重要です。

## 🔗 関連実験

- **実験3（Last Will監視システム）**: このセンサーを監視するシステムの実装
- **実験1（QoS性能比較）**: QoSレベルごとの性能差の測定
- **実験5（メッセージカウンター）**: トラフィック分析ツール
