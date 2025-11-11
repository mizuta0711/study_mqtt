# 応用例1：複数センサー統合システム

## 📊 概要

複数の種類のセンサー（温度、湿度、照度）を同時にシミュレートし、統合ダッシュボードで監視するシステムです。

## 🎯 学習目標

- 複数のセンサーデータを統合して扱う方法
- 各センサーに適したQoS設定の理解
- 異常値の検出とアラート送信
- マルチグラフによるリアルタイム可視化

## 📁 ファイル構成

```
01_multi_sensor_system/
├── README.md                    # このファイル
├── multi_sensor_publisher.py    # センサーPublisher
└── multi_graph_dashboard.py     # 統合ダッシュボード
```

## 🚀 実行方法

### 1. MQTTブローカーの起動

```bash
# Dockerコンテナが起動していることを確認
docker ps
```

### 2. センサーシステムの起動

```bash
# ターミナル1: センサーPublisher
python mqtt_clients/step5/advance/01_multi_sensor_system/multi_sensor_publisher.py
```

### 3. ダッシュボードの起動

```bash
# ターミナル2: 統合ダッシュボード
python mqtt_clients/step5/advance/01_multi_sensor_system/multi_graph_dashboard.py
```

## ✨ 主な機能

### センサーPublisher

- ✅ **3種類のセンサー**: 温度、湿度、照度を同時にシミュレート
- ✅ **リアルな変化**: 前回値から徐々に変化する自然な挙動
- ✅ **異常値検出**: 閾値を超えた場合に自動でアラート送信
- ✅ **ステータス管理**: センサーの稼働状態をRetainメッセージで管理
- ✅ **Last Will設定**: 予期しない切断時に自動でOFFLINEを送信

### 統合ダッシュボード

- ✅ **3つのグラフ**: 温度、湿度、照度を同時表示
- ✅ **統計情報**: 最新値、平均値、最小値、最大値を表示
- ✅ **閾値ライン**: 警告レベルを視覚的に表示
- ✅ **ステータス監視**: センサーの稼働状態を監視
- ✅ **アラート表示**: 異常値をコンソールに表示

## 📊 使用するトピック

| トピック | 説明 | QoS | Retain |
|:---|:---|:---:|:---:|
| `sensors/MultiSensor01/temperature` | 温度データ (°C) | 0 | ❌ |
| `sensors/MultiSensor01/humidity` | 湿度データ (%) | 0 | ❌ |
| `sensors/MultiSensor01/light` | 照度データ (lux) | 0 | ❌ |
| `sensors/MultiSensor01/status` | センサーステータス | 1 | ✅ |
| `alerts/temperature` | 温度アラート (JSON) | 2 | ❌ |
| `alerts/humidity` | 湿度アラート (JSON) | 2 | ❌ |

## 🔧 QoS設定の理由

### QoS 0 (センサーデータ)
- 高頻度で送信されるデータのため、最新値が重要
- 多少のデータロスは許容可能
- ネットワーク負荷を軽減

### QoS 1 (ステータス)
- センサーの稼働状態は確実に伝達
- Retainと組み合わせて、新規Subscriberもすぐに状態を把握

### QoS 2 (アラート)
- 重要なアラートは確実に1回だけ送信
- 重複送信を防ぐ

## 🚨 アラート条件

### 温度アラート
- **高温警報**: 30°C以上
- **低温警報**: 18°C以下

### 湿度アラート
- **高湿度警報**: 70%以上
- **低湿度警報**: 30%以下

## 💡 実装のポイント

### 1. リアルな値の生成
```python
def generate_temperature():
    global current_temp
    # 前回値から±0.5°Cの範囲で変化
    current_temp += random.uniform(-0.5, 0.5)
    current_temp = max(15.0, min(35.0, current_temp))
    return round(current_temp, 2)
```

### 2. 異常値の検出
```python
def check_alert(client, sensor_type, value):
    if sensor_type == "temperature":
        if value > 30.0:
            alert = "高温警報"
        elif value < 18.0:
            alert = "低温警報"
```

### 3. マルチグラフの表示
```python
# 3つのサブプロットを作成
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
```

## 📈 期待される動作

1. センサーPublisherが起動し、ONLINEステータスを送信
2. 温度、湿度、照度データが毎秒送信される
3. ダッシュボードがリアルタイムでグラフを更新
4. 異常値が検出されたらアラートが送信される
5. センサーが停止すると、Last WillでOFFLINEが送信される

## 🔄 カスタマイズのヒント

### センサーの追加
```python
# 気圧センサーを追加
pressure = round(random.uniform(980, 1030), 1)  # hPa
client.publish(f"sensors/{SENSOR_ID}/pressure", str(pressure), qos=0)
```

### アラート条件の変更
```python
# より厳しい閾値に変更
if value > 28.0:  # 30°C → 28°C
    alert = "高温警報"
```

### グラフの色変更
```python
# 温度グラフを青色に変更
line1, = ax1.plot([], [], 'b-', linewidth=2)
```

## 🎓 学習ポイント

1. **複数センサーの統合**: 異なる種類のセンサーを一つのシステムで管理
2. **適切なQoS選択**: データの重要度に応じてQoSレベルを選択
3. **異常値の検出**: 閾値ベースのシンプルなアラートシステム
4. **リアルタイム可視化**: matplotlibのアニメーション機能を活用
5. **ステータス管理**: Retainメッセージでセンサーの状態を永続化

## 🔗 関連ドキュメント

- [../../study/step5/01_IoTシステム構築実践.md](../../../../study/step5/01_IoTシステム構築実践.md)
- [../../study/step5/05_応用コード集.md](../../../../study/step5/05_応用コード集.md)
