# paho-mqtt ライブラリ詳細リファレンス

## 📖 主要なクラスとメソッド

### Client クラス

```python
import paho.mqtt.client as mqtt
client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv311)
```

### 接続関連

| メソッド | 説明 | 例 |
|:---|:---|:---|
| `connect(host, port, keepalive)` | ブローカーに接続 | `client.connect("localhost", 1883, 60)` |
| `disconnect()` | 切断 | `client.disconnect()` |
| `reconnect()` | 再接続 | `client.reconnect()` |

### メッセージ送信

| メソッド | 説明 | 例 |
|:---|:---|:---|
| `publish(topic, payload, qos, retain)` | メッセージ送信 | `client.publish("test", "msg", qos=1, retain=True)` |

### メッセージ受信

| メソッド | 説明 | 例 |
|:---|:---|:---|
| `subscribe(topic, qos)` | トピック購読 | `client.subscribe("test/#", qos=1)` |
| `unsubscribe(topic)` | 購読解除 | `client.unsubscribe("test/#")` |

### ループ処理

| メソッド | 説明 | 用途 |
|:---|:---|:---|
| `loop_forever()` | 永続ループ | Subscriber |
| `loop_start()` | バックグラウンド実行 | 他の処理と並行 |
| `loop_stop()` | ループ停止 | loop_start()の終了 |
| `loop(timeout)` | 1回処理 | 細かい制御 |

### コールバック関数

```python
def on_connect(client, userdata, flags, rc):
    # 接続時
    pass

def on_disconnect(client, userdata, rc):
    # 切断時
    pass

def on_message(client, userdata, msg):
    # メッセージ受信時
    # msg.topic, msg.payload, msg.qos, msg.retain
    pass

def on_publish(client, userdata, mid):
    # 送信完了時
    pass

def on_subscribe(client, userdata, mid, granted_qos):
    # 購読成功時
    pass

def on_log(client, userdata, level, buf):
    # ログ出力時（デバッグ用）
    pass

# コールバック登録
client.on_connect = on_connect
client.on_message = on_message
```

**詳細**: [paho-mqtt公式ドキュメント](https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php)
