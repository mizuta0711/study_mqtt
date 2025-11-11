# 第4章：QoS・Retain・Willを試す

## 🎯 この章でやること

MQTTの高度な機能を実際に動かして、違いを体感しましょう！
- 🔢 **QoS（品質保証レベル）**: メッセージの配信保証
- 🔖 **Retain**: 最新メッセージの保持
- 💀 **Last Will**: 異常切断の自動通知

実験しながら学ぶのが一番楽しいです！🚀

---

## 🔢 実験1：QoS（品質保証レベル）を試す（30分）

### QoSとは？

MQTTには3つの品質レベルがあります：

| QoS | 名前 | 保証 | 速度 | 用途 |
|:---:|:---|:---|:---:|:---|
| **0** | At most once | なし | ⚡⚡⚡ | リアルタイムデータ |
| **1** | At least once | 最低1回 | ⚡⚡ | 重要なデータ |
| **2** | Exactly once | 正確に1回 | ⚡ | 決済など |

### 実験1-1：QoS 0を試す

**qos0_publisher.py**:
```python
import paho.mqtt.client as mqtt
import time

client = mqtt.Client()
client.connect("localhost", 1883, 60)

print("📤 QoS 0 でメッセージ送信中...")
for i in range(5):
    result = client.publish("test/qos0", f"メッセージ {i}", qos=0)
    print(f"送信 {i}: rc={result.rc}")
    time.sleep(0.5)

client.disconnect()
print("✅ 完了（QoS 0）")
```

**qos0_subscriber.py**:
```python
import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    print(f"📥 受信 [QoS={msg.qos}]: {msg.payload.decode()}")

def on_connect(client, userdata, flags, rc):
    print("📻 QoS 0 で購読開始...")
    client.subscribe("test/qos0", qos=0)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)

print("⏳ QoS 0 メッセージを待機中...")
client.loop_forever()
```

**実験方法**:
1. ターミナル1で `python qos0_subscriber.py` を起動
2. ターミナル2で `python qos0_publisher.py` を実行

**観察ポイント**:
- ✅ 高速で処理される
- ⚠️ ネットワーク障害があると、メッセージが失われる可能性

### 実験1-2：QoS 1を試す

**qos1_publisher.py**:
```python
import paho.mqtt.client as mqtt
import time

def on_publish(client, userdata, mid):
    print(f"  → ✅ メッセージID {mid} の送信完了を確認")

client = mqtt.Client()
client.on_publish = on_publish
client.connect("localhost", 1883, 60)

print("📤 QoS 1 でメッセージ送信中...")
for i in range(5):
    info = client.publish("test/qos1", f"メッセージ {i}", qos=1)
    print(f"送信 {i}: メッセージID={info.mid}")
    time.sleep(0.5)

client.disconnect()
print("✅ 完了（QoS 1）")
```

**qos1_subscriber.py**:
```python
import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    print(f"📥 受信 [QoS={msg.qos}]: {msg.payload.decode()}")

def on_connect(client, userdata, flags, rc):
    print("📻 QoS 1 で購読開始...")
    client.subscribe("test/qos1", qos=1)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)

print("⏳ QoS 1 メッセージを待機中...")
client.loop_forever()
```

**実験方法**: 同様に2つのターミナルで実行

**観察ポイント**:
- ✅ 確実に届く（ACK確認あり）
- ⚠️ 重複する可能性がある
- 📊 QoS 0より少し遅い

### 実験1-3：QoS 2を試す

**qos2_publisher.py** と **qos2_subscriber.py** を同様に作成（`qos=2`に変更）

**観察ポイント**:
- ✅ 正確に1回だけ届く
- ✅ 重複なし
- 📊 最も遅い（4ウェイハンドシェイク）

### 実験1-4：3つのQoSを比較する実験

**qos_comparison.py**:
```python
import paho.mqtt.client as mqtt
import time

client = mqtt.Client()
client.connect("localhost", 1883, 60)

print("🔬 QoS 0/1/2 の比較実験")
print("=" * 60)

qos_levels = [0, 1, 2]
for qos in qos_levels:
    start = time.time()

    for i in range(10):
        client.publish(f"test/qos{qos}", f"メッセージ {i}", qos=qos)

    elapsed = time.time() - start
    print(f"QoS {qos}: {elapsed:.4f}秒 で10メッセージ送信")

client.disconnect()
print("=" * 60)
print("💡 結果: QoS 0が最速、QoS 2が最も確実")
```

**期待される結果**:
```
QoS 0: 0.0023秒 で10メッセージ送信
QoS 1: 0.0156秒 で10メッセージ送信
QoS 2: 0.0312秒 で10メッセージ送信
```

🎯 **結論**: 用途に応じてQoSを選ぼう！

---

## 🔖 実験2：Retainメッセージを試す（20分）

### Retainとは？

Retainメッセージは、ブローカーが最後のメッセージを記憶します。
新しいSubscriberが接続したとき、即座に最新の状態を知ることができます。

### 実験2-1：Retainの基本動作

**retain_publisher.py**:
```python
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("localhost", 1883, 60)

# Retainメッセージを送信
client.publish("device/status", "ONLINE", retain=True)
print("📤 Retainメッセージを送信: ONLINE")

client.disconnect()
```

**retain_subscriber.py**:
```python
import paho.mqtt.client as mqtt
import time

def on_message(client, userdata, msg):
    retained = "✅ [Retained]" if msg.retain else "📨 [New]"
    print(f"{retained} {msg.payload.decode()}")

def on_connect(client, userdata, flags, rc):
    print("📻 購読開始...")
    client.subscribe("device/status")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# わざと5秒待ってから接続
print("⏳ 5秒後に接続します...")
time.sleep(5)

client.connect("localhost", 1883, 60)
client.loop_forever()
```

**実験手順**:
1. `python retain_publisher.py` を実行
2. Publisherが終了したことを確認
3. `python retain_subscriber.py` を実行

**結果**:
```
📻 購読開始...
✅ [Retained] ONLINE
```

🎉 Publisherが終了した後でも、Subscriberは最新の状態を受信できました！

### 実験2-2：デバイスステータスボード

**device_simulator.py**:
```python
import paho.mqtt.client as mqtt
import random
import time

devices = ["sensor01", "sensor02", "sensor03"]

client = mqtt.Client()
client.connect("localhost", 1883, 60)

print("🖥️  デバイスシミュレータ起動")
print("=" * 60)

try:
    for device in devices:
        status = random.choice(["ONLINE", "OFFLINE", "MAINTENANCE"])
        temp = round(random.uniform(20, 30), 1)

        # ステータスをRetainで送信
        client.publish(f"devices/{device}/status", status, retain=True)
        # 温度は通常のメッセージ
        client.publish(f"devices/{device}/temperature", str(temp), retain=False)

        print(f"📤 {device}: {status}, {temp}°C")
        time.sleep(1)
except KeyboardInterrupt:
    pass

client.disconnect()
print("\n✅ シミュレータ停止")
```

**status_board.py**:
```python
import paho.mqtt.client as mqtt

device_status = {}

def on_message(client, userdata, msg):
    parts = msg.topic.split('/')
    device = parts[1]
    data_type = parts[2]
    value = msg.payload.decode()

    if device not in device_status:
        device_status[device] = {}

    device_status[device][data_type] = value

    # ステータスボードを表示
    print("\n" + "=" * 60)
    print("📊 デバイスステータスボード")
    print("=" * 60)
    for dev, data in sorted(device_status.items()):
        status = data.get('status', '?')
        temp = data.get('temperature', '?')

        emoji = "🟢" if status == "ONLINE" else "🔴" if status == "OFFLINE" else "🟡"
        print(f"{emoji} {dev}: {status:12} | 温度: {temp}°C")
    print("=" * 60)

def on_connect(client, userdata, flags, rc):
    print("📡 ステータスボード起動")
    client.subscribe("devices/#")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)

print("⏳ デバイス情報を収集中...")
client.loop_forever()
```

**実験手順**:
1. `python device_simulator.py` を実行して終了
2. 少し待ってから `python status_board.py` を実行

**結果**: Retainされたステータスが即座に表示されます！

### 実験2-3：Retainメッセージの削除

```python
# retain_clear.py
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("localhost", 1883, 60)

# 空のペイロードでRetain=Trueを送信すると削除される
client.publish("device/status", "", retain=True)
print("🗑️  Retainメッセージを削除しました")

client.disconnect()
```

---

## 💀 実験3：Last Will（遺言機能）を試す（30分）

### Last Willとは？

クライアントが予期せず切断されたとき、ブローカーが自動的に送信するメッセージです。
デバイスの異常を検知するのに便利！

### 実験3-1：Last Willの基本動作

**lastwill_client.py**:
```python
import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ 接続成功")
        # 正常なステータスを送信
        client.publish("sensor/status", "ONLINE", retain=True)

client = mqtt.Client("SensorDevice01")

# Last Willを設定（接続前に設定する！）
client.will_set(
    topic="sensor/status",
    payload="OFFLINE",
    qos=1,
    retain=True
)

client.on_connect = on_connect
client.connect("localhost", 1883, 60)
client.loop_start()

print("🌡️  センサー稼働中...")
print("💡 Ctrl+Cで異常終了をシミュレート")

try:
    while True:
        # 温度データを送信
        client.publish("sensor/temperature", "25.5")
        time.sleep(2)
except KeyboardInterrupt:
    print("\n⚠️  異常終了します（Last Willが送信されます）")
    # loop_stop()とdisconnect()を呼ばずに終了
    exit(0)
```

**lastwill_monitor.py**:
```python
import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    status = msg.payload.decode()

    if status == "ONLINE":
        print("🟢 センサーがオンラインになりました")
    elif status == "OFFLINE":
        print("🔴 センサーがオフラインになりました！")
        print("   ⚠️  異常な切断を検知しました")

def on_connect(client, userdata, flags, rc):
    print("📡 モニター起動")
    client.subscribe("sensor/status")

client = mqtt.Client("Monitor01")
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)

print("⏳ センサーの状態を監視中...")
client.loop_forever()
```

**実験手順**:
1. ターミナル1で `python lastwill_monitor.py` を起動
2. ターミナル2で `python lastwill_client.py` を起動
3. しばらく待つ（"ONLINE"が表示される）
4. **Ctrl+C**でセンサーを強制終了
5. モニターに"OFFLINE"が表示される！

**結果**:
```
ターミナル1（モニター）:
🟢 センサーがオンラインになりました
🔴 センサーがオフラインになりました！
   ⚠️  異常な切断を検知しました
```

🎯 **Last Willが自動的に送信されました！**

### 実験3-2：複数デバイスの監視システム

**multi_device_simulator.py**:
```python
import paho.mqtt.client as mqtt
import random
import time
import sys

if len(sys.argv) < 2:
    print("使い方: python multi_device_simulator.py <device_id>")
    sys.exit(1)

device_id = sys.argv[1]

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ {device_id} 接続成功")
        client.publish(f"devices/{device_id}/status", "ONLINE", retain=True)

client = mqtt.Client(device_id)

# Last Will設定
client.will_set(
    topic=f"devices/{device_id}/status",
    payload="OFFLINE",
    qos=1,
    retain=True
)

client.on_connect = on_connect
client.connect("localhost", 1883, 60)
client.loop_start()

print(f"🖥️  {device_id} 稼働中... (Ctrl+Cで終了)")

try:
    while True:
        data = round(random.uniform(20, 30), 1)
        client.publish(f"devices/{device_id}/data", str(data))
        time.sleep(2)
except KeyboardInterrupt:
    print(f"\n⚠️  {device_id} を異常終了します")
    exit(0)
```

**device_dashboard.py**:
```python
import paho.mqtt.client as mqtt
from datetime import datetime

devices = {}

def on_message(client, userdata, msg):
    parts = msg.topic.split('/')
    device = parts[1]
    message_type = parts[2]
    value = msg.payload.decode()

    if device not in devices:
        devices[device] = {"status": "?", "data": "?", "last_seen": "?"}

    devices[device][message_type] = value
    devices[device]["last_seen"] = datetime.now().strftime("%H:%M:%S")

    # ダッシュボード表示
    print("\n" + "=" * 70)
    print("📊 IoTデバイス監視ダッシュボード")
    print("=" * 70)
    for dev_id, info in sorted(devices.items()):
        status_emoji = "🟢" if info["status"] == "ONLINE" else "🔴"
        print(f"{status_emoji} {dev_id:15} | "
              f"状態: {info['status']:8} | "
              f"データ: {info['data']:6} | "
              f"最終更新: {info['last_seen']}")
    print("=" * 70)

def on_connect(client, userdata, flags, rc):
    print("📡 ダッシュボード起動")
    client.subscribe("devices/#")

client = mqtt.Client("Dashboard")
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)

print("⏳ デバイスを監視中...")
client.loop_forever()
```

**実験手順**:
1. ターミナル1: `python device_dashboard.py`
2. ターミナル2: `python multi_device_simulator.py device01`
3. ターミナル3: `python multi_device_simulator.py device02`
4. ターミナル4: `python multi_device_simulator.py device03`
5. どれか1つのデバイスをCtrl+Cで終了
6. ダッシュボードで"OFFLINE"を確認！

🎊 まるで本物のIoT監視システムみたいですね！

---

## 🎯 実験4：機能を組み合わせる（20分）

### 最強のセンサーシステム

QoS、Retain、Last Willをすべて組み合わせます！

**smart_sensor.py**:
```python
import paho.mqtt.client as mqtt
import random
import time

SENSOR_ID = "SmartSensor01"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ {SENSOR_ID} 接続成功")
        # ステータスをRetainで送信
        client.publish(
            f"sensors/{SENSOR_ID}/status",
            "ONLINE",
            qos=1,
            retain=True
        )

client = mqtt.Client(SENSOR_ID)

# Last Will設定（QoS 1, Retain有効）
client.will_set(
    topic=f"sensors/{SENSOR_ID}/status",
    payload="OFFLINE",
    qos=1,
    retain=True
)

client.on_connect = on_connect
client.connect("localhost", 1883, 60)
client.loop_start()

print(f"🌡️  {SENSOR_ID} 稼働中...")
print("💡 各メッセージの設定:")
print("  - ステータス: QoS 1 + Retain")
print("  - 温度データ: QoS 0（リアルタイム優先）")
print("  - アラート: QoS 2（確実に配信）")
print()

try:
    counter = 0
    while True:
        counter += 1
        temp = round(random.uniform(18, 32), 1)

        # 温度データ（QoS 0）
        client.publish(
            f"sensors/{SENSOR_ID}/temperature",
            str(temp),
            qos=0
        )

        # 異常値の場合はアラート（QoS 2）
        if temp > 30 or temp < 20:
            alert = f"⚠️  異常値検知: {temp}°C"
            client.publish(
                f"sensors/{SENSOR_ID}/alert",
                alert,
                qos=2
            )
            print(f"🚨 {alert}")
        else:
            print(f"📊 温度: {temp}°C")

        time.sleep(2)
except KeyboardInterrupt:
    print(f"\n⚠️  異常終了")
    exit(0)
```

このセンサーは：
- ✅ ステータスをRetainで保存（新規接続でも状態がわかる）
- ✅ Last Willで異常切断を通知
- ✅ 温度データはQoS 0（高速）
- ✅ アラートはQoS 2（確実に配信）

完璧です！🎉

---

## 📊 まとめ：使い分けガイド

### QoSの使い分け

| データの種類 | 推奨QoS | 理由 |
|:---|:---:|:---|
| 温度・湿度（連続データ） | 0 | 次のデータが来るので欠けてもOK |
| ドアの開閉イベント | 1 | 見逃せないが重複は許容 |
| 決済トランザクション | 2 | 重複も欠損も絶対NG |

### Retainの使い分け

| データの種類 | Retain | 理由 |
|:---|:---:|:---|
| デバイスのステータス | ✅ | 新規接続時に最新状態を知りたい |
| 設定値（温度設定など） | ✅ | 最後の設定を保持 |
| リアルタイムデータ | ❌ | 古いデータは不要 |

### Last Willの使い分け

| ユースケース | Last Will | 理由 |
|:---|:---:|:---|
| デバイスの死活監視 | ✅ | 異常切断を自動検知 |
| 一時的なクライアント | ❌ | 正常終了が多い |

---

## ✅ 動作確認チェックリスト

以下がすべてできればこの章は完了です！

- [ ] QoS 0/1/2の違いを実験で確認した
- [ ] Retainメッセージが動作することを確認した
- [ ] Last Willが発火することを確認した
- [ ] 3つの機能を組み合わせて使えた
- [ ] 実用的な設定を選択できる

---

## 🎓 この章で学んだこと

✅ **QoS 0/1/2の違いと使い分け**
✅ **Retainメッセージの活用方法**
✅ **Last Will機能の実装**
✅ **機能を組み合わせた実践的な設計**

---

## 🚀 次のステップ

おめでとうございます！MQTTの高度な機能をマスターしました！

次の第5章では、これまで学んだことを総動員して、実用的なIoTシステムを構築します。

**次の章**: 第5章：応用演習と確認

- センサー＆ダッシュボードシステム
- データの可視化（グラフ表示）
- 実践的なアプリケーション

---

**理解度テスト**: [第4章 理解度テスト](./06_理解度テスト.md)
