# Last Will（遺言）機能詳細解説

## 📖 Last Willの仕組み

Last Willは、クライアントが**予期せず切断**されたときに、ブローカーが自動的に送信するメッセージです。

```
1. クライアントが接続時にLast Willを設定

2. 正常に切断（disconnect()呼び出し）
   → Last Willは送信されない

3. 異常切断（ネットワーク障害、クラッシュ）
   → ブローカーが自動的にLast Willを送信
```

---

## 💡 実装例

### 基本的な設定

```python
import paho.mqtt.client as mqtt

client = mqtt.Client()

# ⚠️ connect()の前に設定すること！
client.will_set(
    topic="devices/sensor01/status",
    payload="OFFLINE",
    qos=1,
    retain=True
)

client.connect("localhost", 1883, 60)
```

**重要**: `will_set()`は必ず`connect()`の前に呼ぶ！

---

## 🎯 ユースケース

### 1. デバイスの死活監視

```python
# センサー側
client.will_set("sensor/status", "DEAD", qos=1, retain=True)
client.connect("localhost", 1883)
client.publish("sensor/status", "ALIVE", retain=True)

# 監視側
def on_message(client, userdata, msg):
    if msg.payload.decode() == "DEAD":
        send_alert("センサーが応答しません！")
```

### 2. アラート通知

```python
# デバイス側
client.will_set(
    topic="alerts/critical",
    payload="Device-01 unexpectedly disconnected!",
    qos=2
)
```

### 3. セッション管理

```python
# チャットクライアント
username = "Alice"
client.will_set(
    topic=f"chat/users/{username}/status",
    payload="left",
    qos=1
)
```

---

## 🔄 正常終了とLast Willの違い

### 正常終了（Last Will送信されない）

```python
client = mqtt.Client()
client.will_set("topic", "OFFLINE", qos=1)
client.connect("localhost", 1883)

# 処理...

client.disconnect()  # ← 正常切断
# → Last Willは送信されない
```

### 異常終了（Last Will送信される）

```python
client = mqtt.Client()
client.will_set("topic", "OFFLINE", qos=1)
client.connect("localhost", 1883)

# 処理...

exit(0)  # disconnect()を呼ばずに終了
# → Last Willが送信される！
```

または

```python
# Ctrl+Cで強制終了
# → Last Willが送信される
```

---

## ⚙️ パラメータ詳細

```python
client.will_set(
    topic="status",         # トピック（必須）
    payload="OFFLINE",      # メッセージ（必須）
    qos=1,                  # QoSレベル（0/1/2）
    retain=True             # Retain有効化
)
```

### 推奨設定

| パラメータ | 推奨値 | 理由 |
|:---|:---|:---|
| qos | 1 または 2 | 確実に通知したい |
| retain | True | 新しい監視クライアントにも通知 |

---

## 🔗 Retain + Last Willの組み合わせ

**最強の設定**:

```python
client = mqtt.Client("Device01")

# Last Will: QoS 1 + Retain
client.will_set(
    topic="devices/device01/status",
    payload="OFFLINE",
    qos=1,
    retain=True
)

def on_connect(client, userdata, flags, rc):
    # 接続成功時にONLINEを送信（Retain）
    client.publish(
        "devices/device01/status",
        "ONLINE",
        qos=1,
        retain=True
    )

client.on_connect = on_connect
client.connect("localhost", 1883)
```

**動作**:
1. 正常接続 → "ONLINE"がRetainで保存
2. 新しい監視クライアント接続 → "ONLINE"を即座に受信
3. 異常切断 → "OFFLINE"が送信され、Retainで保存
4. 監視クライアントがアラート発動！

完璧です！🎯

---

## ⚠️ 注意点

### 1. タイミング

Last Willが送信されるのは：
- ネットワークタイムアウト後
- keepaliveの1.5倍の時間経過後

即座には送信されません。

### 2. 正常終了の明示

```python
try:
    client.loop_forever()
except KeyboardInterrupt:
    # 正常終了を明示
    client.publish("status", "OFFLINE", retain=True)
    client.disconnect()
```

### 3. will_set()のタイミング

```python
# ❌ 間違い
client.connect("localhost", 1883)
client.will_set("topic", "msg")  # 遅い！

# ✅ 正しい
client.will_set("topic", "msg")
client.connect("localhost", 1883)
```

---

**前の章**: [メインドキュメント](./01_MQTT機能実践.md)
