# 実験3：Last Will監視システム

## 📖 概要

このプログラムは、MQTT Last Will（遺言）機能を活用したデバイス監視システムです。複数のデバイスのオンライン/オフライン状態をリアルタイムで監視し、予期しない切断を即座に検出します。

## 🎯 学習目標

- Last Will（遺言）機能の仕組みを理解する
- ワイルドカード購読（`+`）の実践的な使い方を学ぶ
- デバイス監視システムの設計パターンを習得する
- トピック階層構造の効果的な使い方を理解する

## 🔍 Last Will機能とは

**Last Will（遺言）**は、クライアントが予期せず切断された場合に、ブローカーが自動的に送信するメッセージです。

### 動作の仕組み

1. クライアントが接続時にLast Willメッセージを設定
2. 正常に切断された場合は送信されない
3. 異常切断（ネットワーク断、クラッシュ等）の場合に自動送信
4. デバイスの死活監視に最適

### 設定例

```python
client.will_set("devices/sensor01/status", "OFFLINE", qos=1, retain=True)
```

## 🚀 使い方

### 前提条件

1. MQTTブローカー（Mosquitto）がlocalhost:1883で起動していること
2. paho-mqttライブラリがインストールされていること

```bash
pip install paho-mqtt
```

### 実行方法

#### 1. 監視システムの起動

```bash
python lastwill_monitor_system.py
```

#### 2. テスト用デバイスの起動

別のターミナルで以下のようなデバイスシミュレータを実行：

```python
# test_device.py
import paho.mqtt.client as mqtt
import time

client = mqtt.Client("Device01")

# Last Will設定
client.will_set("devices/Device01/status", "OFFLINE", qos=1, retain=True)

client.connect("localhost", 1883, 60)
client.publish("devices/Device01/status", "ONLINE", qos=1, retain=True)

print("デバイス起動 (Ctrl+Cで異常終了)")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("異常終了 - Last Willが発火")
    exit(0)
```

### 実行例

```
📡 デバイス監視システム起動
============================================================
[14:30:15] 🟢 Device01: ONLINE
[14:32:45] 🔴 Device01: OFFLINE
  ⚠️  アラート: Device01が応答しません！
[14:33:10] 🟢 Device02: ONLINE
```

## 💡 コード解説

### ワイルドカード購読

```python
client.subscribe("devices/+/status")
```

- `+`は単一レベルワイルドカード
- `devices/Device01/status`、`devices/Device02/status`など、すべてマッチ
- デバイス名が動的に増えても対応可能

### トピック階層の解析

```python
device = msg.topic.split('/')[1]
```

- トピック`devices/Device01/status`から`Device01`を抽出
- 階層構造を活用した情報の取り出し

### 状態管理

```python
devices_status[device] = {
    "status": status,
    "time": timestamp
}
```

- 各デバイスの最新状態をディクショナリで管理
- タイムスタンプを記録して履歴追跡が可能

## 🔬 実験のポイント

### Last Willのテスト方法

1. **正常終了**: `client.disconnect()`を呼ぶとLast Willは送信されない
2. **異常終了**: プログラムを強制終了（Ctrl+C）するとLast Willが発火
3. **ネットワーク断**: Wi-Fiを切断するなど

### トピック設計のベストプラクティス

```
devices/{device_id}/status  ← オンライン状態
devices/{device_id}/metrics ← メトリクス
devices/{device_id}/config  ← 設定
```

- 階層的に整理することで管理しやすくなる
- ワイルドカードで柔軟に購読可能

## 🎓 応用例

### 1. ダッシュボード化

```python
def print_status_board():
    print("\n📊 デバイス状態一覧")
    for device, info in devices_status.items():
        emoji = "🟢" if info["status"] == "ONLINE" else "🔴"
        print(f"  {emoji} {device}: {info['status']} (最終更新: {info['time']})")
```

### 2. アラート通知

```python
if status == "OFFLINE":
    send_email_alert(device)
    send_slack_notification(device)
```

### 3. 状態履歴の記録

```python
import json

with open("device_logs.json", "a") as f:
    log_entry = {
        "device": device,
        "status": status,
        "timestamp": timestamp
    }
    f.write(json.dumps(log_entry) + "\n")
```

### 4. 自動復旧アクション

```python
if status == "OFFLINE":
    # デバイスの再起動リクエストを送信
    client.publish(f"devices/{device}/command", "restart", qos=2)
```

## 📊 監視システムの拡張

### ヘルスチェック付き監視

デバイス側で定期的にハートビートを送信：

```python
# デバイス側
while True:
    client.publish(f"devices/{DEVICE_ID}/heartbeat", str(time.time()), qos=0)
    time.sleep(30)
```

監視側でタイムアウト検出：

```python
# 最終ハートビートから60秒経過でアラート
if time.time() - last_heartbeat > 60:
    print(f"⚠️  {device} からのハートビートが途絶えました")
```

## ⚠️ 注意事項

- **Keep-Alive設定**: `connect()`の第3引数で設定（デフォルト60秒）
- **Retain推奨**: ステータストピックにはRetainを使うと、監視システム起動時に現在状態を取得可能
- **QoSレベル**: 重要な状態通知にはQoS 1以上を推奨

## 🎓 まとめ

このシステムを通じて、以下が学べます：

- Last Will機能の実践的な活用方法
- IoTデバイスの死活監視パターン
- トピック階層設計のベストプラクティス
- リアルタイム監視システムの実装

**重要なポイント**: Last Willは「切断の検出」に特化した機能です。定期的なヘルスチェックと組み合わせることで、より堅牢な監視システムが構築できます。

## 🔗 関連実験

- **実験4（全機能統合センサー）**: Last Will設定を含むセンサーの完全な実装例
- **実験2（Retain削除ツール）**: Retainメッセージの管理方法
