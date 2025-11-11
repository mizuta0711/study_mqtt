# MQTT 1日学習計画（Docker + Python）

## 🗓️ 概要
本資料は **1日（約7時間）でMQTTの基礎から実践まで** 学ぶための学習計画です。  
Windows環境を前提に、**Docker上でMosquittoブローカーを構築し、Pythonでクライアントを実装・動作確認**します。

---

## 🕐 第1章：MQTTの基礎理解（1時間）

### 目的
MQTTの仕組み・用語・特徴を理解する。

### 内容
- MQTTとは何か（軽量Pub/Sub型プロトコル）
- IoTで使われる理由
- 基本構成  
  - Publisher（送信側）  
  - Subscriber（受信側）  
  - Broker（仲介サーバー）
- トピック（Topic）とメッセージ構造
- QoS（品質保証レベル：0/1/2）
- Retain / Last Will 機能
- 通信ポート（通常: 1883）

### 学習資料例
- [MQTT.org – Introduction](https://mqtt.org/)
- Mosquitto 公式ドキュメント

---

## 🕑 第2章：DockerでMQTT Brokerを構築（1.5時間）

### 目的
Windows上でDockerを用いてMQTTブローカー（Mosquitto）を起動。

### 手順
1. Docker Desktopをインストール・起動  
2. Mosquittoイメージを取得  
   ```bash
   docker pull eclipse-mosquitto
   ```

3. ローカル構成ファイルを作成  
   ```
   mqtt/
     ├─ config/
     │   └─ mosquitto.conf
     ├─ data/
     └─ log/
   ```

4. `mosquitto.conf` の例  
   ```conf
   persistence true
   persistence_location /mosquitto/data/
   log_dest file /mosquitto/log/mosquitto.log
   allow_anonymous true
   listener 1883
   ```

5. コンテナ起動  
   ```bash
   docker run -it -p 1883:1883 -v ./config:/mosquitto/config -v ./data:/mosquitto/data -v ./log:/mosquitto/log eclipse-mosquitto
   ```

6. 動作確認  
   ```bash
   docker exec -it <container_id> sh
   mosquitto_sub -t test/topic &
   mosquitto_pub -t test/topic -m "Hello MQTT"
   ```

---

## 🕒 第3章：Pythonでクライアント作成（2時間）

### 目的
PythonでPublisher・Subscriberを作成して、Brokerと通信確認。

### 使用ライブラリ
- paho-mqtt

### 環境構築
```bash
pip install paho-mqtt
```

### Publisher例
```python
import paho.mqtt.client as mqtt

broker = "localhost"
port = 1883
topic = "test/topic"

client = mqtt.Client()
client.connect(broker, port, 60)

for i in range(5):
    msg = f"Hello MQTT {i}"
    client.publish(topic, msg)
    print("Sent:", msg)

client.disconnect()
```

### Subscriber例
```python
import paho.mqtt.client as mqtt

broker = "localhost"
port = 1883
topic = "test/topic"

def on_message(client, userdata, msg):
    print(f"Received '{msg.payload.decode()}' on topic '{msg.topic}'")

client = mqtt.Client()
client.connect(broker, port, 60)
client.subscribe(topic)
client.on_message = on_message

print("Waiting for messages...")
client.loop_forever()
```

### 確認方法
- ターミナル1で `subscriber.py` を起動  
- ターミナル2で `publisher.py` を実行  
→ メッセージがリアルタイムに表示されればOK！

---

## 🕓 第4章：QoS・Retain・Willを試す（1.5時間）

### 目的
MQTTの主要機能を実際に試す。

### 実験内容
#### QoSの違い
```python
client.publish(topic, "Message", qos=1)
```
- QoS 0：最も軽量、失われる可能性あり  
- QoS 1：必ず1回は届く  
- QoS 2：重複なし、確実に1回  

#### Retainメッセージ
```python
client.publish(topic, "Retained Message", retain=True)
```

#### Last Will機能
```python
client.will_set("status/offline", "Client disconnected unexpectedly", qos=1)
```

---

## 🕔 第5章：応用演習と確認（1時間）

### 目的
実用的なIoT通信を模擬してみる。

### 例題
センサー送信機（Publisher）とダッシュボード受信機（Subscriber）を構築する。

#### Publisher例
```python
import paho.mqtt.client as mqtt
import random, time

client = mqtt.Client()
client.connect("localhost", 1883, 60)

while True:
    temp = round(random.uniform(20.0, 30.0), 2)
    client.publish("sensor/temperature", temp)
    print("Sent:", temp)
    time.sleep(1)
```

#### Subscriber例
```python
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
from collections import deque

data = deque(maxlen=50)
broker = "localhost"

def on_message(client, userdata, msg):
    value = float(msg.payload.decode())
    data.append(value)
    plt.clf()
    plt.plot(data)
    plt.pause(0.1)

client = mqtt.Client()
client.connect(broker, 1883, 60)
client.subscribe("sensor/temperature")
client.on_message = on_message

plt.ion()
plt.show()
client.loop_forever()
```

---

## 🕕 第6章：まとめと発展（30分）

### 振り返りポイント
- MQTTの仕組みと用語を理解できたか  
- Docker環境でBrokerを動かせたか  
- PythonからPublish/Subscribeができたか  
- QoSやRetainを試せたか  

### 発展テーマ（次のステップ）
- 認証付き通信（ユーザー・パスワード、SSL/TLS）
- クラウドMQTTブローカー（HiveMQ Cloud, AWS IoT Coreなど）
- ESP32など実機との通信

---

## 💡補足
- DockerとPythonを併用することで再現性が高く、環境差異を吸収しやすい。  
- MQTT ExplorerなどのGUIツールを使えば、トピックの流れも視覚的に確認できる。
