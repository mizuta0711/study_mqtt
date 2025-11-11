# 第3章：Pythonでクライアント作成

## 🎯 この章でやること

実際にPythonコードを書いて、MQTT通信を体験しましょう！
- 📤 **Publisher**: メッセージを送信するプログラム
- 📥 **Subscriber**: メッセージを受信するプログラム

2つのプログラムが通信できたら、あなたは立派なMQTT開発者です！🎉

---

## 🛠️ ステップ1：環境準備（5分）

### 1-1. Pythonのバージョン確認

```bash
python --version
# Python 3.7以上ならOK！
```

### 1-2. paho-mqttのインストール

```bash
pip install paho-mqtt
```

**実行例**:
```
Collecting paho-mqtt
  Downloading paho-mqtt-1.6.1.tar.gz (99 kB)
Installing collected packages: paho-mqtt
Successfully installed paho-mqtt-1.6.1
```

✅ インストール成功！

### 1-3. MQTTブローカーが起動しているか確認

```bash
docker ps | grep mqtt-broker
```

起動していない場合：
```bash
# PowerShellで実行
docker-compose up -d
```

---

## 📤 ステップ2：最初のPublisherを作る（20分）

### 2-1. プロジェクト構造

```
D:\Develop\python\StudyMQTT\
├── mqtt_clients/          # ← 新しく作成
│   └── publisher.py      # ← これから作る
├── mqtt/
├── docker-compose.yml
└── ...
```

### 2-2. publisher.pyを作成

以下のコードをコピーして、`mqtt_clients/publisher.py`として保存してください。

```python
# publisher.py
import paho.mqtt.client as mqtt
import time

# 接続設定
BROKER = "localhost"
PORT = 1883
TOPIC = "test/hello"

# MQTTクライアントを作成
client = mqtt.Client()

print("🔌 MQTTブローカーに接続中...")
client.connect(BROKER, PORT, 60)
print("✅ 接続成功！")

# メッセージを5回送信
for i in range(1, 6):
    message = f"こんにちは！これは{i}回目のメッセージです 🎉"
    result = client.publish(TOPIC, message)

    if result.rc == 0:
        print(f"📤 送信成功: {message}")
    else:
        print(f"❌ 送信失敗: エラーコード {result.rc}")

    time.sleep(1)  # 1秒待機

print("👋 すべてのメッセージを送信しました。切断します。")
client.disconnect()
```

### 2-3. 実行してみよう！

```bash
cd D:\Develop\python\StudyMQTT
python mqtt_clients/publisher.py
```

**期待される出力**:
```
🔌 MQTTブローカーに接続中...
✅ 接続成功！
📤 送信成功: こんにちは！これは1回目のメッセージです 🎉
📤 送信成功: こんにちは！これは2回目のメッセージです 🎉
📤 送信成功: こんにちは！これは3回目のメッセージです 🎉
📤 送信成功: こんにちは！これは4回目のメッセージです 🎉
📤 送信成功: こんにちは！これは5回目のメッセージです 🎉
👋 すべてのメッセージを送信しました。切断します。
```

🎊 **おめでとうございます！** 最初のPublisherが動きました！

でも、今はメッセージを送信しただけです。受信するプログラムがないので、誰も見ていません...😢

次は受信側を作りましょう！

---

## 📥 ステップ3：Subscriberを作る（20分）

### 3-1. subscriber.pyを作成

`mqtt_clients/subscriber.py`として保存してください。

```python
# subscriber.py
import paho.mqtt.client as mqtt

# 接続設定
BROKER = "localhost"
PORT = 1883
TOPIC = "test/hello"

# メッセージを受信したときの処理
def on_message(client, userdata, msg):
    """
    メッセージが届いたら、この関数が自動的に呼ばれます
    """
    message = msg.payload.decode('utf-8')
    topic = msg.topic
    print(f"📨 受信: [{topic}] {message}")

# 接続成功時の処理
def on_connect(client, userdata, flags, rc):
    """
    ブローカーに接続できたら、この関数が自動的に呼ばれます
    """
    if rc == 0:
        print("✅ ブローカーに接続しました")
        print(f"📻 トピック '{TOPIC}' を購読開始...")
        client.subscribe(TOPIC)
    else:
        print(f"❌ 接続失敗: エラーコード {rc}")

# MQTTクライアントを作成
client = mqtt.Client()

# コールバック関数を登録
client.on_connect = on_connect
client.on_message = on_message

print("🔌 MQTTブローカーに接続中...")
client.connect(BROKER, PORT, 60)

print("⏳ メッセージを待っています... (Ctrl+Cで終了)")
print("-" * 50)

# メッセージを待ち続ける
client.loop_forever()
```

### 3-2. コードの説明

**重要な概念: コールバック関数**

MQTTでは、イベントが発生したときに自動的に呼ばれる関数を「コールバック関数」と呼びます。

| コールバック関数 | 呼ばれるタイミング |
|:---|:---|
| `on_connect()` | ブローカーに接続成功したとき |
| `on_message()` | メッセージを受信したとき |
| `on_disconnect()` | 切断されたとき |

`loop_forever()`は、これらのイベントを待ち続ける無限ループです。

---

## 🎉 ステップ4：通信テストをしよう！（15分）

いよいよPublisherとSubscriberを同時に動かします！

### 4-1. 2つのターミナルを開く

**ターミナル1（Subscriber）**:
```bash
cd D:\Develop\python\StudyMQTT
python mqtt_clients/subscriber.py
```

**出力**:
```
🔌 MQTTブローカーに接続中...
✅ ブローカーに接続しました
📻 トピック 'test/hello' を購読開始...
⏳ メッセージを待っています... (Ctrl+Cで終了)
--------------------------------------------------
```

Subscriberが待機状態になります。このターミナルはそのままにしておきましょう。

### 4-2. 別のターミナルでPublisherを実行

**ターミナル2（Publisher）**:
```bash
cd D:\Develop\python\StudyMQTT
python mqtt_clients/publisher.py
```

### 4-3. 結果を見てみよう！

**ターミナル1（Subscriber側）に表示される**:
```
📨 受信: [test/hello] こんにちは！これは1回目のメッセージです 🎉
📨 受信: [test/hello] こんにちは！これは2回目のメッセージです 🎉
📨 受信: [test/hello] こんにちは！これは3回目のメッセージです 🎉
📨 受信: [test/hello] こんにちは！これは4回目のメッセージです 🎉
📨 受信: [test/hello] こんにちは！これは5回目のメッセージです 🎉
```

🎊🎊🎊 **大成功！** Publisher → Broker → Subscriber の通信が成功しました！

これであなたはMQTT通信の基本をマスターしました！

---

## 🎮 ステップ5：楽しい実験をしてみよう！（30分）

### 実験1：メッセージをカスタマイズ

publisher.pyの`message`を好きな内容に変更してみましょう：

```python
# 例1：カウントダウン
message = f"カウントダウン: {6-i}秒前！"

# 例2：ランダムな絵文字
import random
emojis = ["🎉", "🚀", "⭐", "🌈", "🎈"]
message = f"メッセージ{i}: {random.choice(emojis)}"

# 例3：時刻付き
from datetime import datetime
message = f"[{datetime.now().strftime('%H:%M:%S')}] メッセージ{i}"
```

### 実験2：複数のトピックを使う

**publisher.py**を修正：
```python
topics = ["sensor/temperature", "sensor/humidity", "sensor/pressure"]

for i, topic in enumerate(topics, 1):
    message = f"センサー{i}からのデータです"
    client.publish(topic, message)
    print(f"📤 送信: [{topic}] {message}")
    time.sleep(1)
```

**subscriber.py**を修正（ワイルドカードを使用）：
```python
TOPIC = "sensor/#"  # sensor/配下のすべてを購読
```

実行すると、すべてのセンサーデータを受信できます！

### 実験3：温度センサーシミュレータ

**temperature_sensor.py**として保存：

```python
# temperature_sensor.py
import paho.mqtt.client as mqtt
import random
import time

BROKER = "localhost"
PORT = 1883
TOPIC = "home/livingroom/temperature"

client = mqtt.Client("TempSensor01")  # クライアントIDを指定
client.connect(BROKER, PORT, 60)

print("🌡️  温度センサーシミュレータを起動しました")
print("📊 1秒ごとに温度データを送信します...")
print("-" * 50)

try:
    while True:
        # 20.0℃〜30.0℃のランダムな温度を生成
        temperature = round(random.uniform(20.0, 30.0), 1)

        client.publish(TOPIC, str(temperature))
        print(f"🌡️  送信: {temperature}°C")

        time.sleep(1)
except KeyboardInterrupt:
    print("\n👋 センサーを停止します")
    client.disconnect()
```

**temperature_monitor.py**として保存：

```python
# temperature_monitor.py
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "home/livingroom/temperature"

def on_message(client, userdata, msg):
    temp = float(msg.payload.decode())

    # 温度によって表示を変える
    if temp < 22.0:
        icon = "❄️"
        status = "寒い"
    elif temp > 28.0:
        icon = "🔥"
        status = "暑い"
    else:
        icon = "😊"
        status = "快適"

    print(f"{icon} 現在の温度: {temp}°C ({status})")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("📡 温度モニターを開始しました")
        client.subscribe(TOPIC)

client = mqtt.Client("TempMonitor01")
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
print("⏳ 温度データを待っています...")
print("-" * 50)

client.loop_forever()
```

**実行方法**:

ターミナル1:
```bash
python mqtt_clients/temperature_sensor.py
```

ターミナル2:
```bash
python mqtt_clients/temperature_monitor.py
```

**出力例**:

ターミナル1（センサー）:
```
🌡️  温度センサーシミュレータを起動しました
📊 1秒ごとに温度データを送信します...
--------------------------------------------------
🌡️  送信: 24.5°C
🌡️  送信: 27.3°C
🌡️  送信: 21.8°C
```

ターミナル2（モニター）:
```
📡 温度モニターを開始しました
⏳ 温度データを待っています...
--------------------------------------------------
😊 現在の温度: 24.5°C (快適)
😊 現在の温度: 27.3°C (快適)
❄️ 現在の温度: 21.8°C (寒い)
```

🎊 まるで本物のIoTシステムみたいですね！

---

## 🎯 ステップ6：コールバック関数を理解する（20分）

### コールバック関数一覧

| コールバック | 説明 | いつ使う？ |
|:---|:---|:---|
| `on_connect` | 接続成功時 | 接続後に購読を開始 |
| `on_disconnect` | 切断時 | 再接続処理 |
| `on_message` | メッセージ受信時 | メッセージ処理 |
| `on_publish` | 送信完了時 | 送信確認 |
| `on_subscribe` | 購読成功時 | 購読確認 |
| `on_log` | ログ出力時 | デバッグ |

### すべてのコールバックを使った例

```python
# advanced_subscriber.py
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print(f"🔌 接続: rc={rc}")
    if rc == 0:
        client.subscribe("test/#")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("⚠️ 予期しない切断が発生しました")

def on_message(client, userdata, msg):
    print(f"📨 メッセージ: [{msg.topic}] {msg.payload.decode()}")

def on_subscribe(client, userdata, mid, granted_qos):
    print(f"✅ 購読成功: QoS={granted_qos[0]}")

def on_log(client, userdata, level, buf):
    print(f"📝 ログ: {buf}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.on_log = on_log

client.connect("localhost", 1883, 60)
client.loop_forever()
```

---

## 🔄 ステップ7：ループ処理の種類（15分）

MQTTクライアントがイベントを処理する方法は3種類あります。

### 方法1: loop_forever() - 推奨

```python
client.connect("localhost", 1883, 60)
client.loop_forever()  # 永遠に待ち続ける（Ctrl+Cで終了）
```

**用途**: Subscriberなど、常時起動しておくプログラム

### 方法2: loop_start() - バックグラウンド実行

```python
client.connect("localhost", 1883, 60)
client.loop_start()  # 別スレッドでループ開始

# メインスレッドで他の処理ができる
print("他の処理を実行中...")
time.sleep(10)

client.loop_stop()  # ループ停止
client.disconnect()
```

**用途**: メインスレッドで別の処理をしたい場合

### 方法3: loop() - 手動ループ

```python
client.connect("localhost", 1883, 60)

for i in range(100):
    client.loop()  # 1回だけイベント処理
    time.sleep(0.1)

client.disconnect()
```

**用途**: 細かい制御が必要な場合

### 実践例：loop_start()を使う

```python
# interactive_publisher.py
import paho.mqtt.client as mqtt
import time

client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.loop_start()  # バックグラウンドで実行

print("💬 メッセージを入力してください（'quit'で終了）")
print("-" * 50)

while True:
    message = input("あなた> ")

    if message.lower() == "quit":
        break

    client.publish("chat/room1", message)
    print("📤 送信しました")

client.loop_stop()
client.disconnect()
print("👋 さようなら！")
```

これでチャットアプリのようなインタラクティブなプログラムが作れます！

---

## 🐛 ステップ8：エラーハンドリング（10分）

### 接続エラーの処理

```python
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ 接続成功")
    else:
        error_messages = {
            1: "不正なプロトコルバージョン",
            2: "クライアントIDが拒否されました",
            3: "サーバーが利用できません",
            4: "ユーザー名またはパスワードが間違っています",
            5: "認証されていません"
        }
        print(f"❌ 接続失敗: {error_messages.get(rc, '不明なエラー')}")

client = mqtt.Client()
client.on_connect = on_connect

try:
    client.connect("localhost", 1883, 60)
    client.loop_forever()
except Exception as e:
    print(f"⚠️ エラーが発生しました: {e}")
```

### 再接続処理

```python
import paho.mqtt.client as mqtt
import time

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("⚠️ 切断されました。再接続します...")
        time.sleep(5)
        try:
            client.reconnect()
        except:
            print("❌ 再接続に失敗しました")

client = mqtt.Client()
client.on_disconnect = on_disconnect
client.connect("localhost", 1883, 60)
client.loop_forever()
```

---

## 📊 動作確認チェックリスト

以下がすべてできればこの章は完了です！

- [ ] paho-mqttがインストールされている
- [ ] publisher.pyが動作する
- [ ] subscriber.pyが動作する
- [ ] Publisher/Subscriber間で通信できる
- [ ] 温度センサーシミュレータが動作する
- [ ] コールバック関数を理解している
- [ ] loop_forever()とloop_start()の違いが分かる

---

## 🎓 まとめ

### この章で学んだこと

✅ **paho-mqttライブラリの使い方**
✅ **Publisher/Subscriberの実装方法**
✅ **コールバック関数の仕組み**
✅ **ループ処理の種類**
✅ **エラーハンドリング**

### 重要なポイント

💡 **コールバック関数**がMQTT通信の核心
💡 **loop_forever()**でイベントを待ち続ける
💡 **複数のトピック**で柔軟な通信ができる
💡 **実験しながら学ぶ**のが一番早い！

---

## 🚀 次のステップ

次の第4章では、MQTTの高度な機能を試します：

**次の章**: [第4章：QoS・Retain・Willを試す](../step4/00_学習ガイド.md)

- QoSレベル（0/1/2）の違い
- Retainメッセージの実験
- Last Will機能のテスト

楽しみにしていてください！🎉

---

## 📚 参考資料

- [paho-mqtt公式ドキュメント](https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php)
- [Python公式ドキュメント](https://docs.python.org/ja/3/)

---

**理解度テスト**: [第3章 理解度テスト](./05_理解度テスト.md)
