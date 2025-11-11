# 実験5：メッセージカウンター

## 📖 概要

このプログラムは、MQTTブローカーを流れるすべてのメッセージをリアルタイムで監視し、QoSレベルごとの統計情報を表示する分析ツールです。システムのトラフィック状況を把握するのに役立ちます。

## 🎯 学習目標

- リアルタイムメッセージ監視の実装方法を学ぶ
- MQTTメッセージのメタデータ（QoS、Retainフラグ）の活用
- ワイルドカード購読（`#`）を使ったトラフィック分析
- 動的な画面更新（`\r`によるインライン更新）の実装

## 🔍 主な機能

### 集計項目

- **QoS 0メッセージ数**: 配信保証なしのメッセージ
- **QoS 1メッセージ数**: 確認応答ありのメッセージ
- **QoS 2メッセージ数**: 重複なし保証のメッセージ
- **Retainメッセージ数**: 保持フラグが立っているメッセージ

### 表示形式

```
QoS0: 245 | QoS1: 89 | QoS2: 12 | Retain: 5
```

- リアルタイムでカウントが更新される
- 1行で簡潔に表示（画面スクロールなし）

## 🚀 使い方

### 前提条件

1. MQTTブローカー（Mosquitto）がlocalhost:1883で起動していること
2. paho-mqttライブラリがインストールされていること

```bash
pip install paho-mqtt
```

### 実行方法

```bash
python message_counter.py
```

### 実行例

#### 起動直後

```
📊 メッセージカウンター起動
QoS0: 0 | QoS1: 0 | QoS2: 0 | Retain: 0
```

#### センサー稼働中

```
📊 メッセージカウンター起動
QoS0: 156 | QoS1: 3 | QoS2: 2 | Retain: 3
```

#### 統合センサー実験時

実験4のultimate_sensor.pyと組み合わせると：

```bash
# ターミナル1
python ultimate_sensor.py Sensor01

# ターミナル2
python message_counter.py
```

結果例：
```
QoS0: 423 | QoS1: 1 | QoS2: 15 | Retain: 3
```

- **QoS 0**: 温度データ（2秒ごとに送信されるため多い）
- **QoS 1**: ONLINE通知（起動時の1回）
- **QoS 2**: 異常アラート + Last Will設定
- **Retain**: ステータスメッセージ

## 💡 コード解説

### 全メッセージの購読

```python
client.subscribe("#")
```

- `#`はマルチレベルワイルドカード
- ブローカーを通過するすべてのメッセージを受信
- 新規Retainメッセージも即座に受信

### QoSレベルの取得

```python
stats[f"qos{msg.qos}"] += 1
```

- `msg.qos`属性でメッセージのQoSレベルを取得（0, 1, 2）
- ディクショナリキーとして使用して該当カウンタをインクリメント

### Retainフラグの判定

```python
if msg.retain:
    stats["retained"] += 1
```

- `msg.retain`は真偽値
- Trueの場合、Retainメッセージとしてカウント
- 既存のRetainメッセージ + 新規Retainメッセージの両方をカウント

### インライン更新

```python
print(f"\r...", end="")
```

- `\r`でカーソルを行頭に戻す
- `end=""`で改行を抑制
- 同じ行を繰り返し上書きすることでちらつきを防止

## 🔬 実験のアイデア

### 1. QoSベンチマークとの連携

実験1のqos_benchmark.pyを実行しながら監視：

```bash
# ターミナル1
python message_counter.py

# ターミナル2
python qos_benchmark.py
```

→ 各QoSレベルのメッセージが100個ずつカウントされる様子を観察

### 2. トラフィックパターンの分析

複数の統合センサーを起動して、トラフィックを分析：

```bash
# 3つのセンサーを起動
python ultimate_sensor.py Sensor01 &
python ultimate_sensor.py Sensor02 &
python ultimate_sensor.py Sensor03 &

# カウンター起動
python message_counter.py
```

→ QoS 0（温度データ）が圧倒的に多いことを確認

### 3. Retain メッセージの蓄積監視

時間経過とともにRetainメッセージが蓄積される様子を観察：

```bash
# 複数回センサーを起動・停止
for i in {1..10}; do
    python ultimate_sensor.py Sensor0$i &
    sleep 5
    kill %1
done
```

### 4. ネットワーク負荷の可視化

大量のメッセージを送信してボトルネックを特定：

```python
# load_test.py
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("localhost", 1883, 60)

for i in range(10000):
    client.publish("test/load", f"msg{i}", qos=0)
    if i % 1000 == 0:
        print(f"{i} messages sent")
```

## 🎓 応用例

### 詳細統計の表示

```python
import time

start_time = time.time()

def on_message(client, userdata, msg):
    stats[f"qos{msg.qos}"] += 1
    if msg.retain:
        stats["retained"] += 1

    elapsed = time.time() - start_time
    total = sum([stats['qos0'], stats['qos1'], stats['qos2']])
    rate = total / elapsed if elapsed > 0 else 0

    print(f"\rQoS0: {stats['qos0']} | "
          f"QoS1: {stats['qos1']} | "
          f"QoS2: {stats['qos2']} | "
          f"Retain: {stats['retained']} | "
          f"合計: {total} | "
          f"レート: {rate:.1f} msg/s", end="")
```

### トピックごとのカウント

```python
topic_stats = {}

def on_message(client, userdata, msg):
    topic = msg.topic
    if topic not in topic_stats:
        topic_stats[topic] = 0
    topic_stats[topic] += 1

    # 上位5トピックを表示
    sorted_topics = sorted(topic_stats.items(), key=lambda x: x[1], reverse=True)
    print("\n📊 トップ5トピック:")
    for topic, count in sorted_topics[:5]:
        print(f"  {topic}: {count}")
```

### CSV出力

```python
import csv
import time

with open("mqtt_stats.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "qos0", "qos1", "qos2", "retained"])

    def on_message(client, userdata, msg):
        stats[f"qos{msg.qos}"] += 1
        if msg.retain:
            stats["retained"] += 1

        # 10秒ごとに記録
        if time.time() % 10 < 0.1:
            writer.writerow([
                time.time(),
                stats['qos0'],
                stats['qos1'],
                stats['qos2'],
                stats['retained']
            ])
```

### グラフ化

```python
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

fig, ax = plt.subplots()
qos_labels = ['QoS 0', 'QoS 1', 'QoS 2']
bars = ax.bar(qos_labels, [0, 0, 0])

def update_graph(frame):
    values = [stats['qos0'], stats['qos1'], stats['qos2']]
    for bar, value in zip(bars, values):
        bar.set_height(value)
    ax.set_ylim(0, max(values) * 1.1 if max(values) > 0 else 10)
    return bars

ani = FuncAnimation(fig, update_graph, interval=1000)
plt.show()
```

## 📊 分析のポイント

### 正常なトラフィックパターン

| 用途 | QoS 0 | QoS 1 | QoS 2 | 特徴 |
|-----|-------|-------|-------|-----|
| センサーデータ収集 | 高 | 低 | 低 | 頻繁な更新 |
| コマンド送信 | 低 | 中 | 低 | 適度な信頼性 |
| クリティカル通知 | 低 | 低 | 高 | 完全保証 |

### 異常パターンの検出

- **QoS 2が異常に多い**: 過剰な信頼性要求でパフォーマンス低下の可能性
- **Retainが増え続ける**: メモリリーク、削除されていないメッセージ
- **QoS 0が極端に少ない**: 設計が非効率（すべて高QoS）

## ⚠️ 注意事項

- **高負荷時の影響**: カウンター自体もブローカーの負荷になる
- **長時間実行**: カウンタがオーバーフローする可能性（Pythonは実質無制限だが表示が崩れる）
- **Retainの二重カウント**: 既存Retainと新規Retainを区別しない

## 🎓 まとめ

このカウンターを通じて、以下が学べます：

- MQTTトラフィックのリアルタイム監視手法
- QoSレベルの分布とシステム特性の関係
- メッセージメタデータの活用方法
- デバッグとパフォーマンス分析のツール開発

**重要なポイント**: システムのトラフィックパターンを理解することで、適切なQoS選択や最適化のポイントが見えてきます。

## 🔗 関連実験

- **実験1（QoS性能比較）**: 各QoSレベルの性能測定
- **実験4（全機能統合センサー）**: このツールで監視する対象
- **実験2（Retain削除ツール）**: Retainメッセージの管理
