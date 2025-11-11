# 📈 サンプル6：センサーダッシュボード（JSON使用）

## 概要

複数のセンサー（温度、湿度、気圧）のデータをJSON形式で送信し、ダッシュボードで可視化するシステムです。IoTセンサーネットワークの典型的なアーキテクチャを体験でき、JSONデータの扱い方を学べます。

## 動作説明

### システムアーキテクチャ

```
┌─────────────────────────────┐         ┌─────────────────────────────┐
│  multi_sensor.py            │         │  sensor_dashboard.py        │
│  (センサーノード)           │────────>│  (監視ダッシュボード)       │
├─────────────────────────────┤         ├─────────────────────────────┤
│  🌡️  温度センサー            │         │  ・データ受信               │
│  💧 湿度センサー            │         │  ・JSON パース              │
│  🌤️  気圧センサー            │         │  ・フォーマット表示         │
│                             │         │  ・快適度判定               │
│  → JSON形式で一括送信       │         └─────────────────────────────┘
└─────────────────────────────┘
         │
         │ sensors/data
         │ {"temperature": 22.5, "humidity": 60, "pressure": 1013}
         └──────────────────────────────────────────>
                    MQTT Broker経由
```

### データフロー

```
センサー側の処理フロー:

1. センサー値の生成（ランダムシミュレーション）
   ├─ 温度: 20〜30°C
   ├─ 湿度: 40〜80%
   └─ 気圧: 1000〜1020 hPa

2. データ構造化（辞書作成）
   data = {
       "temperature": 22.5,
       "humidity": 60.0,
       "pressure": 1013.5
   }

3. JSONシリアライゼーション
   json_data = json.dumps(data)
   → '{"temperature": 22.5, "humidity": 60.0, "pressure": 1013.5}'

4. MQTT送信
   client.publish("sensors/data", json_data)

5. 2秒待機 → 1に戻る
```

```
ダッシュボード側の処理フロー:

1. MQTT受信
   msg.payload = b'{"temperature": 22.5, ...}'

2. デコード + JSONパース
   json_str = msg.payload.decode()
   data = json.loads(json_str)

3. データ取り出し
   temp = data['temperature']
   humid = data['humidity']
   press = data['pressure']

4. 表示フォーマット
   ┌──────────────────────────────────────────┐
   │ 📊 センサーダッシュボード                │
   ├──────────────────────────────────────────┤
   │ 🌡️  温度: 22.5°C                        │
   │ 💧 湿度: 60.0%                          │
   │ 🌤️  気圧: 1013.5hPa                     │
   │ 😊 快適な環境です！                      │
   └──────────────────────────────────────────┘

5. 快適度判定
   if 22 <= temp <= 26 and 40 <= humid <= 60:
       print("😊 快適な環境です！")
```

## 技術的なポイント

### 1. JSON形式のメリット

**従来の方式（個別送信）**:
```python
# 3つのトピックに分けて送信
client.publish("sensors/temperature", "22.5")
client.publish("sensors/humidity", "60.0")
client.publish("sensors/pressure", "1013.5")

# 問題点:
# - 3回の通信が必要
# - 時刻がずれる可能性
# - 関連性が分かりにくい
```

**JSON方式（一括送信）**:
```python
# 1つのトピックで全データを送信
data = {
    "temperature": 22.5,
    "humidity": 60.0,
    "pressure": 1013.5
}
client.publish("sensors/data", json.dumps(data))

# メリット:
# - 1回の通信で完結
# - データの整合性が保証される
# - 拡張が容易
```

### 2. JSONシリアライゼーション

**送信側（Pythonオブジェクト → JSON文字列）**:
```python
import json

# Pythonの辞書
data = {
    "temperature": 22.5,
    "humidity": 60.0,
    "pressure": 1013.5
}

# JSON文字列に変換
json_data = json.dumps(data)
# 結果: '{"temperature": 22.5, "humidity": 60.0, "pressure": 1013.5}'

# MQTTで送信（文字列として）
client.publish("sensors/data", json_data)
```

**受信側（JSON文字列 → Pythonオブジェクト）**:
```python
import json

def on_message(client, userdata, msg):
    # バイト列から文字列にデコード
    json_str = msg.payload.decode()

    # JSON文字列をPythonの辞書にパース
    data = json.loads(json_str)

    # 辞書のキーでアクセス
    temp = data['temperature']   # 22.5
    humid = data['humidity']     # 60.0
    press = data['pressure']     # 1013.5
```

### 3. ランダムデータ生成（センサーシミュレーション）

```python
import random

data = {
    "temperature": round(random.uniform(20, 30), 1),  # 20.0〜30.0
    "humidity": round(random.uniform(40, 80), 1),     # 40.0〜80.0
    "pressure": round(random.uniform(1000, 1020), 1)  # 1000.0〜1020.0
}
```

**random.uniform()の仕組み**:
```python
random.uniform(20, 30)  # 20.0以上30.0未満の浮動小数点数
# 例: 23.456789123

round(..., 1)  # 小数点以下1桁に丸める
# 例: 23.5
```

**実際のセンサーデータの取得**:
```python
# Raspberry Piでの例
import Adafruit_DHT

# DHT22センサーから読み取り
humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, pin=4)

data = {
    "temperature": round(temperature, 1),
    "humidity": round(humidity, 1),
    "pressure": read_pressure_sensor()  # BMP280など
}
```

### 4. 快適度判定ロジック

```python
def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())

    temp = data['temperature']
    humid = data['humidity']

    # 快適度の判定基準
    if 22 <= temp <= 26 and 40 <= humid <= 60:
        print("😊 快適な環境です！")
    else:
        print("⚠️ 環境を調整することをお勧めします")
```

**快適度の基準（一般的な室内環境）**:
```
温度: 22〜26°C  → 快適範囲
湿度: 40〜60%   → 快適範囲

組み合わせ判定:
┌────────────┬────────────┬────────────┐
│  温度/湿度  │  40-60%    │  その他    │
├────────────┼────────────┼────────────┤
│  22-26°C   │  😊 快適   │  ⚠️ 注意   │
│  その他     │  ⚠️ 注意   │  ⚠️ 注意   │
└────────────┴────────────┴────────────┘
```

### 5. データ構造の拡張性

**基本的な構造**:
```python
data = {
    "temperature": 22.5,
    "humidity": 60.0,
    "pressure": 1013.5
}
```

**拡張例1（メタデータ追加）**:
```python
import time

data = {
    "sensor_id": "DHT22_01",
    "location": "リビング",
    "timestamp": time.time(),
    "measurements": {
        "temperature": 22.5,
        "humidity": 60.0,
        "pressure": 1013.5
    }
}
```

**拡張例2（複数センサー）**:
```python
data = {
    "sensors": [
        {"id": "sensor01", "temperature": 22.5, "humidity": 60.0},
        {"id": "sensor02", "temperature": 23.1, "humidity": 58.5},
        {"id": "sensor03", "temperature": 21.8, "humidity": 62.3}
    ]
}
```

**拡張例3（統計情報）**:
```python
data = {
    "temperature": {
        "current": 22.5,
        "min": 20.1,
        "max": 25.3,
        "avg": 22.8
    }
}
```

### 6. エラーハンドリング

**JSONパースエラーの処理**:
```python
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())

        temp = data['temperature']
        humid = data['humidity']
        press = data['pressure']

        # 正常処理
        display_data(temp, humid, press)

    except json.JSONDecodeError as e:
        print(f"❌ JSONパースエラー: {e}")
    except KeyError as e:
        print(f"❌ 必要なキーがありません: {e}")
    except Exception as e:
        print(f"❌ エラー: {e}")
```

## 設計・実装のポイント

### データモデリング

1. **構造化データの重要性**
   ```python
   # 悪い例（文字列結合）
   message = f"{temp},{humid},{press}"
   # パース時に順序に依存、拡張が困難

   # 良い例（JSON）
   data = {"temperature": temp, "humidity": humid, "pressure": press}
   # キー名で識別、順序に依存しない、拡張が容易
   ```

2. **データ型の保持**
   ```python
   # JSONは型情報を保持
   data = {
       "temperature": 22.5,      # float
       "sensor_active": True,    # bool
       "reading_count": 100      # int
   }
   ```

3. **ネストした構造**
   ```python
   data = {
       "device": {
           "id": "sensor01",
           "type": "DHT22"
       },
       "readings": {
           "temperature": 22.5,
           "humidity": 60.0
       }
   }
   ```

### IoTアーキテクチャのベストプラクティス

1. **センサーデータの標準化**
   ```python
   # 統一されたフォーマット
   {
       "sensor_id": "string",
       "timestamp": "ISO8601",
       "data": {
           "metric_name": value
       }
   }
   ```

2. **時刻同期**
   ```python
   import datetime

   data = {
       "timestamp": datetime.datetime.utcnow().isoformat(),
       "temperature": 22.5
   }
   # 結果: "timestamp": "2024-01-15T10:30:45.123456"
   ```

3. **データ検証**
   ```python
   # センサー値の妥当性チェック
   if not (-40 <= temperature <= 80):
       print("⚠️ 温度センサー異常")
   ```

### 拡張可能な設計

**1. データベース保存**:
```python
import sqlite3

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())

    conn = sqlite3.connect('sensor_data.db')
    conn.execute("""
        INSERT INTO readings (timestamp, temperature, humidity, pressure)
        VALUES (datetime('now'), ?, ?, ?)
    """, (data['temperature'], data['humidity'], data['pressure']))
    conn.commit()
```

**2. グラフ表示**:
```python
import matplotlib.pyplot as plt

temperatures = []

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    temperatures.append(data['temperature'])

    # リアルタイムグラフ更新
    plt.clf()
    plt.plot(temperatures)
    plt.draw()
    plt.pause(0.01)
```

**3. アラート機能**:
```python
def check_alerts(data):
    alerts = []

    if data['temperature'] > 30:
        alerts.append("🔥 高温注意")
    if data['humidity'] > 70:
        alerts.append("💧 高湿度注意")

    return alerts
```

## 使用方法

### 前提条件

- MQTTブローカー（Mosquitto）が起動していること
- paho-mqttライブラリがインストール済みであること

### 実行手順

1. **ターミナル1でDashboardを起動**:
   ```bash
   cd mqtt_clients/samples/06_sensor_dashboard
   python sensor_dashboard.py
   ```

   出力:
   ```
   📡 ダッシュボード起動
   ```

2. **ターミナル2でSensorを起動**:
   ```bash
   cd mqtt_clients/samples/06_sensor_dashboard
   python multi_sensor.py
   ```

   Sensor側の出力:
   ```
   📊 複数センサーシミュレータ
   📤 送信: 温度=22.5°C, 湿度=60.0%, 気圧=1013.5hPa
   📤 送信: 温度=23.1°C, 湿度=58.3%, 気圧=1014.2hPa
   📤 送信: 温度=24.2°C, 湿度=62.1%, 気圧=1012.8hPa
   ...
   ```

3. **Dashboard側で受信データを確認**:
   ```
   📡 ダッシュボード起動

   ==================================================
   📊 センサーダッシュボード
   ==================================================
   🌡️  温度: 22.5°C
   💧 湿度: 60.0%
   🌤️  気圧: 1013.5hPa
   😊 快適な環境です！

   ==================================================
   📊 センサーダッシュボード
   ==================================================
   🌡️  温度: 23.1°C
   💧 湿度: 58.3%
   🌤️  気圧: 1014.2hPa
   😊 快適な環境です！
   ```

4. **終了**: 両方のターミナルで`Ctrl+C`

### カスタマイズ例

**センサー値の範囲変更**:
```python
# multi_sensor.py を編集
data = {
    "temperature": round(random.uniform(15, 35), 1),  # 範囲拡大
    "humidity": round(random.uniform(30, 90), 1),
    "pressure": round(random.uniform(990, 1030), 1)
}
```

**更新頻度の変更**:
```python
time.sleep(2)  # 2秒 → 5秒に変更
time.sleep(5)
```

**快適度基準の変更**:
```python
# sensor_dashboard.py を編集
if 20 <= temp <= 28 and 30 <= humid <= 70:  # 基準を緩和
    print("😊 快適な環境です！")
```

## 学習ポイント

### 初級レベル

- ✅ **JSON形式**: 構造化データの送受信
- ✅ **複数データの一括送信**: 効率的な通信
- ✅ **データの可視化**: ダッシュボード表示

### 中級レベル

- ✅ **シリアライゼーション**: dumps/loadsの使い方
- ✅ **条件分岐**: 快適度判定ロジック
- ✅ **エラーハンドリング**: 例外処理

### 上級レベル

- ✅ **データモデリング**: 拡張性の高い構造設計
- ✅ **IoTアーキテクチャ**: センサーネットワークの基礎
- ✅ **リアルタイム処理**: ストリーミングデータの扱い

## 応用アイデア

1. **時系列グラフ表示**:
   ```python
   import matplotlib.pyplot as plt
   import matplotlib.animation as animation

   # matplotlibでリアルタイムグラフ
   ```

2. **複数センサーノードの統合**:
   ```python
   # 各部屋にセンサーを配置
   rooms = ["リビング", "寝室", "キッチン"]
   for room in rooms:
       topic = f"sensors/{room}/data"
       client.publish(topic, json.dumps(data))
   ```

3. **データの集計・分析**:
   ```python
   # 過去1時間の平均値を計算
   import statistics
   avg_temp = statistics.mean(recent_temperatures)
   ```

4. **Web ダッシュボード**:
   ```python
   # Flask + Chart.js でブラウザ表示
   from flask import Flask, render_template
   from flask_socketio import SocketIO

   # WebSocketでリアルタイム更新
   ```

5. **機械学習での異常検知**:
   ```python
   # scikit-learnで異常値検出
   from sklearn.ensemble import IsolationForest

   model.fit(sensor_data)
   anomalies = model.predict(new_data)
   ```

6. **アラート通知**:
   ```python
   # Slackやメールで通知
   if temperature > threshold:
       send_slack_notification("🔥 高温アラート")
   ```

7. **データ保存と分析**:
   ```python
   # InfluxDB（時系列DB）に保存
   # Grafanaで可視化
   ```

## トラブルシューティング

### よくある問題

1. **JSONDecodeError**:
   ```
   json.decoder.JSONDecodeError: Expecting value
   ```
   - ペイロードが正しいJSON形式か確認
   - 送信側でjson.dumps()を使用しているか確認

2. **KeyError**:
   ```
   KeyError: 'temperature'
   ```
   - JSON内のキー名が一致しているか確認
   - typo（綴り間違い）がないか確認

3. **データが表示されない**:
   - Dashboard側が起動しているか確認
   - トピック名が一致しているか確認（`sensors/data`）
   - ブローカーが起動しているか確認

4. **快適度が常に「注意」と表示される**:
   - センサー値の範囲を確認
   - 判定条件を環境に合わせて調整

## まとめ

このサンプルでは、MQTTとJSONを組み合わせた実践的なIoTシステムを学べます。JSON形式を使うことで、複数のセンサーデータを効率的に送信し、拡張性の高いシステムを構築できます。実際のIoTプロジェクトでも広く使われるパターンであり、スマートホーム、工場の監視システム、環境モニタリングなど、様々な応用が可能です。
