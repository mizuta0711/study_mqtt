# Step5 サンプルコード

第5章：応用演習と確認のサンプルコード集です。

## 📁 ファイル一覧

### 基本システム

| ファイル | 説明 | 使い方 |
|:---|:---|:---|
| `sensor_publisher.py` | 基本的な温度センサーPublisher | `python sensor_publisher.py` |
| `dashboard_subscriber.py` | リアルタイムダッシュボード | `python dashboard_subscriber.py` |

### 統合システム

| ファイル | 説明 | 使い方 |
|:---|:---|:---|
| `multi_sensor_publisher.py` | 複数センサー統合Publisher（温度、湿度、照度） | `python multi_sensor_publisher.py` |
| `multi_graph_dashboard.py` | 複数グラフ統合ダッシュボード | `python multi_graph_dashboard.py` |

### ユーティリティ

| ファイル | 説明 | 使い方 |
|:---|:---|:---|
| `data_logger.py` | データロガー（SQLite） | `python data_logger.py` |
| `alert_monitor.py` | アラート監視システム | `python alert_monitor.py` |

---

## 🚀 クイックスタート

### シナリオ1：基本的な温度監視

**必要なターミナル数**: 2

```bash
# ターミナル1: ダッシュボード起動
python mqtt_clients/step5/dashboard_subscriber.py

# ターミナル2: センサー起動
python mqtt_clients/step5/sensor_publisher.py
```

**確認ポイント:**
- ✅ グラフがリアルタイムで更新される
- ✅ ステータスが「🟢 ONLINE」と表示される
- ✅ Ctrl+Cで停止すると「🔴 OFFLINE」に変わる

---

### シナリオ2：複数センサー統合監視

**必要なターミナル数**: 3

```bash
# ターミナル1: 統合ダッシュボード起動
python mqtt_clients/step5/multi_graph_dashboard.py

# ターミナル2: 複数センサー起動
python mqtt_clients/step5/multi_sensor_publisher.py

# ターミナル3（オプション）: アラート監視
python mqtt_clients/step5/alert_monitor.py
```

**確認ポイント:**
- ✅ 温度、湿度、照度のグラフが同時に表示される
- ✅ 統計情報（平均、最小、最大）が表示される
- ✅ 閾値を超えるとアラートが発生する

---

### シナリオ3：データロギング付き監視

**必要なターミナル数**: 3

```bash
# ターミナル1: データロガー起動（バックグラウンドで記録）
python mqtt_clients/step5/data_logger.py

# ターミナル2: センサー起動
python mqtt_clients/step5/multi_sensor_publisher.py

# ターミナル3: ダッシュボード起動
python mqtt_clients/step5/multi_graph_dashboard.py
```

**確認ポイント:**
- ✅ データが `sensor_data.db` に保存される
- ✅ ロガーを停止すると統計情報が表示される
- ✅ SQLiteツールでデータベースを確認できる

---

## 🔧 前提条件

### 1. MQTTブローカーの起動

```bash
docker run -it -p 1883:1883 -v ./mqtt/config:/mosquitto/config eclipse-mosquitto
```

### 2. 必要なライブラリ

```bash
pip install paho-mqtt matplotlib
```

---

## 📊 各プログラムの詳細

### sensor_publisher.py

**機能:**
- 1秒ごとに温度データを送信（20〜30°C）
- ステータスをRetain + QoS 1で管理
- Last Willで異常終了を検知

**送信トピック:**
- `sensor/temperature` (QoS 0)
- `sensor/status` (QoS 1, Retain)

---

### dashboard_subscriber.py

**機能:**
- 温度データをリアルタイムグラフ表示
- センサーステータス監視
- matplotlibアニメーション

**購読トピック:**
- `sensor/#` (QoS 1)

---

### multi_sensor_publisher.py

**機能:**
- 温度、湿度、照度を同時に送信
- 異常値検出とアラート送信
- リアルな値の変化をシミュレート

**送信トピック:**
- `sensors/MultiSensor01/temperature` (QoS 0)
- `sensors/MultiSensor01/humidity` (QoS 0)
- `sensors/MultiSensor01/light` (QoS 0)
- `sensors/MultiSensor01/status` (QoS 1, Retain)
- `alerts/temperature` (QoS 2)
- `alerts/humidity` (QoS 2)

---

### multi_graph_dashboard.py

**機能:**
- 3つのグラフを同時表示
- 統計情報表示（平均、最小、最大）
- 閾値ライン表示
- センサーステータス監視

**購読トピック:**
- `sensors/#` (QoS 1)
- `alerts/#` (QoS 2)

---

### data_logger.py

**機能:**
- 全センサーデータをSQLiteに保存
- アラート履歴の記録
- ステータス変更の記録
- 統計情報の表示

**データベース:**
- `sensor_data.db`
  - `sensor_data` テーブル
  - `alerts` テーブル
  - `status_log` テーブル

**購読トピック:**
- `sensors/#` (QoS 1)
- `alerts/#` (QoS 2)

---

### alert_monitor.py

**機能:**
- アラートの受信と表示
- センサーダウンの検知
- アラート履歴の管理
- 対処方法の提案

**購読トピック:**
- `alerts/#` (QoS 2)
- `sensors/+/status` (QoS 1)

---

## 🧪 テストシナリオ

### テスト1：Last Willの確認

1. ダッシュボードを起動
2. センサーを起動
3. センサーのターミナルを強制終了（ウィンドウを閉じる）
4. ダッシュボードに「🔴 OFFLINE」が表示されることを確認

---

### テスト2：アラートの確認

1. アラート監視を起動
2. 複数センサーを起動
3. 温度や湿度が閾値を超えるとアラートが表示されることを確認

**閾値:**
- 温度: 18°C未満 or 30°C超過
- 湿度: 30%未満 or 70%超過

---

### テスト3：データロギングの確認

1. データロガーを起動
2. センサーを起動して数分間動作
3. 両方を停止
4. `sensor_data.db` ファイルが作成されていることを確認
5. SQLiteツールでデータを確認

```bash
# SQLiteでデータベースを開く
sqlite3 sensor_data.db

# データを確認
SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10;
```

---

## 💡 カスタマイズのヒント

### 1. センサーの追加

```python
# 気圧センサーを追加
pressure = round(random.uniform(980, 1030), 1)
client.publish("sensors/pressure", pressure, qos=0)
```

### 2. グラフの追加

```python
# 4つ目のグラフを追加
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 12))
```

### 3. 更新間隔の変更

```python
# 2秒ごとに更新
time.sleep(2)

# グラフの更新間隔も変更
ani = animation.FuncAnimation(fig, update, interval=2000)
```

---

## 🆘 トラブルシューティング

### エラー: "Connection refused"

**原因:** Mosquittoブローカーが起動していない

**対処:**
```bash
docker run -it -p 1883:1883 eclipse-mosquitto
```

---

### エラー: "ModuleNotFoundError: No module named 'paho'"

**原因:** paho-mqttがインストールされていない

**対処:**
```bash
pip install paho-mqtt
```

---

### グラフが表示されない

**原因:** matplotlibがインストールされていない、または設定が不適切

**対処:**
```bash
pip install matplotlib
```

---

## 📚 関連ドキュメント

- [study/step5/00_学習ガイド.md](../../study/step5/00_学習ガイド.md) - 学習の進め方
- [study/step5/01_IoTシステム構築実践.md](../../study/step5/01_IoTシステム構築実践.md) - 基本実装
- [study/step5/05_応用コード集.md](../../study/step5/05_応用コード集.md) - 応用例

---

## ✅ 動作確認チェックリスト

- [ ] Mosquittoブローカーが起動している
- [ ] paho-mqttがインストールされている
- [ ] matplotlibがインストールされている
- [ ] 基本的なセンサーとダッシュボードが動作する
- [ ] 複数センサーシステムが動作する
- [ ] データロガーが正常に記録する
- [ ] アラート監視が正常に動作する

---

**前のステップ**: [step4](../step4/)
**学習ガイド**: [study/step5](../../study/step5/)
