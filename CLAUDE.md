# CLAUDE.md

このファイルは、このリポジトリでコードを扱う際にClaude Code (claude.ai/code)にガイダンスを提供します。

## プロジェクト概要

このリポジトリは、DockerとPythonを使用したMQTT（Message Queuing Telemetry Transport）プロトコル実装の学習用リポジトリです。`MQTT_1day_study_plan.md`に記載されている1日の学習計画に従って構成されています。

**コア技術:**
- **MQTTブローカー**: Eclipse Mosquitto (Dockerコンテナ)
- **クライアントライブラリ**: paho-mqtt (Python)
- **環境**: Docker Desktopを使用したWindows環境

## 開発環境のセットアップ

### 前提条件
- Docker Desktopがインストールされ、起動していること
- Python 3.x とpip
- paho-mqttライブラリ: `pip install paho-mqtt`

### MQTTブローカーのセットアップ (Docker上のMosquitto)

1. **Mosquittoイメージの取得:**
   ```bash
   docker pull eclipse-mosquitto
   ```

2. **Mosquitto用ディレクトリ構造:**
   ```
   mqtt/
     ├─ config/
     │   └─ mosquitto.conf
     ├─ data/
     └─ log/
   ```

3. **Mosquittoコンテナの起動:**
   ```bash
   docker run -it -p 1883:1883 -v ./config:/mosquitto/config -v ./data:/mosquitto/data -v ./log:/mosquitto/log eclipse-mosquitto
   ```

4. **ブローカーの動作確認:**
   ```bash
   docker exec -it <container_id> sh
   mosquitto_sub -t test/topic &
   mosquitto_pub -t test/topic -m "Hello MQTT"
   ```

### Python MQTTクライアントのテスト

**Subscriberの起動 (ターミナル1):**
```bash
python subscriber.py
```

**Publisherの実行 (ターミナル2):**
```bash
python publisher.py
```

## アーキテクチャ

### MQTT通信パターン
```
Publisher (Python) → Broker (Mosquitto/Docker) → Subscriber (Python)
```

**主要コンポーネント:**
- **Broker**: Docker上で動作し、ポート1883でリッスン
- **Publisher**: トピックにメッセージを送信するPythonクライアント
- **Subscriber**: 購読したトピックからメッセージを受信するPythonクライアント

### 接続パラメータ
- **Brokerホスト**: `localhost` (ローカル実行時)
- **ポート**: `1883` (MQTTデフォルトポート、非暗号化)
- **匿名アクセス**: 学習用設定ではデフォルトで有効

## 実装されるMQTT概念

### QoSレベル (Quality of Service)
- **QoS 0**: 最大1回 (配信保証なし)
- **QoS 1**: 最低1回 (確認応答付き配信)
- **QoS 2**: 正確に1回 (重複なし保証配信)

### 主要機能
- **Retain**: 新規Subscriberのためにブローカーが最後のメッセージを保持
- **Last Will**: クライアントが予期せず切断した際に自動送信されるメッセージ
- **Topics**: 階層的なメッセージルーティング (例: `sensor/temperature`)

## よく使うパターン

### 基本的なPublisher
```python
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.publish("topic/name", "message", qos=1)
client.disconnect()
```

### 基本的なSubscriber
```python
import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    print(f"{msg.topic}: {msg.payload.decode()}")

client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.subscribe("topic/name")
client.on_message = on_message
client.loop_forever()
```

### Last Willの設定
```python
client.will_set("status/offline", "Client disconnected", qos=1)
```

## プロジェクトコンテキスト

このリポジトリは構造化された学習パスに従っています (`MQTT_1day_study_plan.md`参照):
1. **第1章**: MQTTの基礎理解 (1時間)
2. **第2章**: Dockerブローカーのセットアップ (1.5時間)
3. **第3章**: Pythonクライアントの実装 (2時間)
4. **第4章**: QoS、Retain、Last Willのテスト (1.5時間)
5. **第5章**: 実用的なIoTシミュレーション (センサー/ダッシュボード) (1時間)
6. **第6章**: まとめと次のステップ (30分)

実装例を作成する際は、学習計画の進行に従ってください。最終的なアプリケーションは、温度データを送信するセンサーと、matplotlibで可視化できるダッシュボードSubscriberをシミュレートします。

## 注意事項

- 設定では学習目的で`allow_anonymous true`を使用 - 本番環境では認証を追加してください
- docsディレクトリは現在空ですが、追加のドキュメントが格納される可能性があります
- デフォルトのmosquitto.confは永続化とログ記録を有効にして、ブローカーの動作を追跡できるようにしています
