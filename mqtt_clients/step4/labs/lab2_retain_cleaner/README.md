# 実験2：Retain削除ツール

## 📖 概要

このプログラムは、MQTTブローカーに保存されているRetain（保持）メッセージを検索し、一括削除するためのメンテナンスツールです。ワイルドカード購読（`#`）を使用してすべてのトピックをスキャンし、Retainフラグが立っているメッセージを特定します。

## 🎯 学習目標

- Retainメッセージの仕組みを理解する
- ワイルドカード購読（`#`）の使い方を学ぶ
- Retainメッセージの削除方法を習得する
- メッセージフラグ（`msg.retain`）の活用方法を学ぶ

## 🔍 Retainメッセージとは

**Retain（保持）メッセージ**は、ブローカーがトピックごとに最後に受信したメッセージを保存する機能です。

### 特徴

- 新しいSubscriberが接続した時、即座に最新状態を取得できる
- トピックごとに1つだけ保存される
- 空のペイロード（`""`）で送信すると削除される

### 用途例

- デバイスの現在状態（オンライン/オフライン）
- センサーの最新値
- システム設定値

## 🚀 使い方

### 前提条件

1. MQTTブローカー（Mosquitto）がlocalhost:1883で起動していること
2. paho-mqttライブラリがインストールされていること

```bash
pip install paho-mqtt
```

### 実行方法

```bash
python clear_retained.py
```

### 実行例

```
Retainメッセージを検索中...
発見: sensors/temp01/status
発見: sensors/temp02/status
発見: devices/monitor/state

3個のRetainメッセージを発見
削除しますか？ (y/n): y
削除: sensors/temp01/status
削除: sensors/temp02/status
削除: devices/monitor/state
✅ 完了
```

## 💡 動作の仕組み

### 1. 全トピック購読

```python
client.subscribe("#")
```

- `#`はマルチレベルワイルドカード（すべてのトピック）
- ブローカーに保存されているすべてのRetainメッセージが即座に配信される

### 2. Retainメッセージの検出

```python
def on_message(client, userdata, msg):
    if msg.retain:
        retained_topics.append(msg.topic)
```

- `msg.retain`フラグでRetainメッセージかどうか判定
- トピック名をリストに保存

### 3. Retainメッセージの削除

```python
client.publish(topic, "", retain=True)
```

- **空のペイロード** + `retain=True` でRetainメッセージを削除
- この仕様がMQTTの標準的な削除方法

## 🔬 実験のポイント

### なぜ3秒待つのか？

```python
time.sleep(3)
```

- Retainメッセージは接続直後に配信されるが、ネットワーク遅延を考慮
- 大量のトピックがある場合、すべて受信するまで時間がかかる
- 環境に応じて調整可能

### ワイルドカード購読の種類

| パターン | マッチング例 | 説明 |
|---------|------------|------|
| `#` | すべて | マルチレベルワイルドカード |
| `sensors/#` | `sensors/temp`, `sensors/humid/room1` | sensorsで始まるすべて |
| `sensors/+/status` | `sensors/temp01/status`, `sensors/humid01/status` | 1レベルワイルドカード |

## 🎓 応用例

### 特定トピックのみ削除

```python
client.subscribe("sensors/#")  # sensorsトピックのみスキャン
```

### 削除前に内容を表示

```python
def on_message(client, userdata, msg):
    if msg.retain:
        print(f"発見: {msg.topic} = {msg.payload.decode()}")
        retained_topics.append(msg.topic)
```

### 自動削除（確認なし）

```python
# input()の部分をコメントアウトして自動化
for topic in retained_topics:
    client.publish(topic, "", retain=True)
```

## ⚠️ 注意事項

- **本番環境での使用に注意**: すべてのRetainメッセージを削除すると、システムの状態情報が失われます
- **権限確認**: ブローカーの設定によっては削除権限が必要な場合があります
- **バックアップ**: 重要なRetainメッセージは削除前に記録しておくことを推奨

## 🎓 まとめ

このツールを通じて、以下が学べます：

- Retainメッセージのライフサイクル
- ワイルドカード購読の実践的な使い方
- MQTTブローカーのメンテナンス手法
- メッセージフラグの活用方法

**重要なポイント**: Retainメッセージは便利ですが、適切に管理しないとブローカーのメモリを圧迫する可能性があります。
