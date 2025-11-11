# Retain（保持）機能詳細解説

## 📖 Retainの仕組み

Retainメッセージは、ブローカーが最後のメッセージを保存し、新規Subscriberに即座に配信します。

```
1. Publisher が Retain=true で送信
   → Broker がメッセージを保存

2. 時間経過（Publisherは切断済み）

3. 新しいSubscriberが接続
   → Broker が保存したメッセージを即座に送信
```

---

## 💡 実装例

### 送信側

```python
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("localhost", 1883, 60)

# Retainメッセージを送信
client.publish("device/status", "ONLINE", retain=True)

client.disconnect()
```

### 受信側

```python
import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    if msg.retain:
        print(f"[Retained] {msg.payload.decode()}")
    else:
        print(f"[New] {msg.payload.decode()}")

client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.subscribe("device/status")
client.loop_forever()
```

---

## 🎯 ユースケース

### 1. デバイスの最新ステータス

```python
# デバイス起動時
client.publish("devices/sensor01/status", "ONLINE", retain=True)

# 新しいダッシュボードが接続
# → 即座に"ONLINE"を受信
```

### 2. 設定値の保存

```python
# エアコンの温度設定
client.publish("home/ac/target_temp", "24", retain=True)

# 新しいコントローラーが接続
# → 現在の設定値を即座に取得
```

### 3. 最後の測定値

```python
# センサーの最新値を保存
client.publish("sensors/outdoor/temperature", "22.5", retain=True)

# ダッシュボード起動時
# → 最新の温度を即座に表示
```

---

## 🗑️ Retainメッセージの削除

空のペイロードで送信すると削除されます：

```python
# Retainメッセージを削除
client.publish("device/status", "", retain=True)
```

または

```python
client.publish("device/status", None, retain=True)
```

---

## ⚠️ 注意点

### 1. トピックごとに1つだけ

同じトピックに複数のRetainメッセージは保存できません。
最後のメッセージが上書きされます。

```python
client.publish("topic", "A", retain=True)  # 保存
client.publish("topic", "B", retain=True)  # Aが上書きされる
# → Subscriberは"B"のみ受信
```

### 2. センシティブな情報は避ける

Retainメッセージは長期間保存されるため、パスワードなどの機密情報は避けましょう。

### 3. ワイルドカード購読との相性

```python
client.subscribe("devices/#")
# → すべてのRetainメッセージが一気に届く
```

大量のRetainメッセージがある場合、注意が必要です。

---

## 🔄 Retain + QoS の組み合わせ

```python
# QoS 1 + Retain
client.publish("topic", "data", qos=1, retain=True)
```

Retainメッセージにもqosを指定できます：
- QoS 0: 高速だが保証なし
- QoS 1: 確実に保存される
- QoS 2: 重複なく確実（遅い）

**推奨**: 重要なステータスにはQoS 1以上を使用

---

**前の章**: [メインドキュメント](./01_MQTT機能実践.md)
