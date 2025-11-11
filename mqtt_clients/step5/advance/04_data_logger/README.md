# 応用例4：データロガー

## 📊 概要

MQTTメッセージをSQLiteデータベースに保存し、後から分析できるようにするデータロガーシステムです。

## 🎯 学習目標

- SQLiteデータベースの基本操作
- MQTTメッセージの永続化
- データの構造化と保存
- SQL クエリによるデータ分析
- 統計情報の計算と表示

## 📁 ファイル構成

```
04_data_logger/
├── README.md        # このファイル
└── data_logger.py   # データロガー本体
```

## 🚀 実行方法

### 1. データロガーの起動

```bash
python mqtt_clients/step5/advance/04_data_logger/data_logger.py
```

### 2. センサーデータの送信（別ターミナル）

```bash
# マルチセンサーを起動
python mqtt_clients/step5/advance/01_multi_sensor_system/multi_sensor_publisher.py
```

または

```bash
# リアルセンサーを起動
python mqtt_clients/step5/advance/03_realistic_sensor/realistic_sensor_publisher.py
```

## ✨ 主な機能

### データ収集
- ✅ **全センサーデータを記録**: 温度、湿度、照度
- ✅ **アラートを記録**: 異常値アラートを保存
- ✅ **ステータスを記録**: センサーのONLINE/OFFLINE状態
- ✅ **タイムスタンプ付き**: すべてのデータに受信時刻を記録

### データ分析
- ✅ **統計情報の計算**: 平均、最大、最小、データ数
- ✅ **最新データの取得**: 直近N件のデータを取得
- ✅ **SQLクエリ**: 柔軟なデータ検索

## 📊 データベーススキーマ

### 1. sensor_data テーブル
センサーから受信したデータを保存

```sql
CREATE TABLE sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id TEXT NOT NULL,       -- センサーID
    timestamp TEXT NOT NULL,        -- タイムスタンプ（ISO形式）
    data_type TEXT NOT NULL,        -- データ種別（temperature/humidity/light）
    value REAL NOT NULL,            -- 測定値
    unit TEXT                       -- 単位（°C/%/lux）
);
```

**データ例:**
| id | sensor_id | timestamp | data_type | value | unit |
|:---|:---|:---|:---|---:|:---|
| 1 | MultiSensor01 | 2025-11-11T15:30:45 | temperature | 25.3 | °C |
| 2 | MultiSensor01 | 2025-11-11T15:30:45 | humidity | 52.1 | % |
| 3 | MultiSensor01 | 2025-11-11T15:30:45 | light | 480 | lux |

### 2. alerts テーブル
アラート情報を保存

```sql
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id TEXT NOT NULL,       -- センサーID
    timestamp TEXT NOT NULL,        -- タイムスタンプ
    alert_type TEXT NOT NULL,       -- アラート種別
    value REAL NOT NULL,            -- アラート時の値
    message TEXT                    -- アラートメッセージ
);
```

**データ例:**
| id | sensor_id | timestamp | alert_type | value | message |
|:---|:---|:---|:---|---:|:---|
| 1 | MultiSensor01 | 2025-11-11T15:35:12 | temperature | 31.2 | 高温警報 |

### 3. status_log テーブル
センサーステータスの履歴を保存

```sql
CREATE TABLE status_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id TEXT NOT NULL,       -- センサーID
    timestamp TEXT NOT NULL,        -- タイムスタンプ
    status TEXT NOT NULL            -- ステータス（ONLINE/OFFLINE）
);
```

**データ例:**
| id | sensor_id | timestamp | status |
|:---|:---|:---|:---|
| 1 | MultiSensor01 | 2025-11-11T15:30:00 | ONLINE |
| 2 | MultiSensor01 | 2025-11-11T16:00:00 | OFFLINE |

## 💾 DataLoggerクラス

### 主要メソッド

#### `log_sensor_data(sensor_id, data_type, value, unit)`
センサーデータを記録

```python
logger.log_sensor_data("MultiSensor01", "temperature", 25.5, "°C")
```

#### `log_alert(sensor_id, alert_type, value, message)`
アラートを記録

```python
logger.log_alert("MultiSensor01", "temperature", 31.2, "高温警報")
```

#### `log_status(sensor_id, status)`
ステータスを記録

```python
logger.log_status("MultiSensor01", "ONLINE")
```

#### `get_recent_data(sensor_id, data_type, limit=100)`
最新データを取得

```python
data = logger.get_recent_data("MultiSensor01", "temperature", limit=10)
# 返り値: [(timestamp, value), ...]
```

#### `get_statistics(sensor_id, data_type)`
統計情報を取得

```python
stats = logger.get_statistics("MultiSensor01", "temperature")
# 返り値: (count, avg, min, max)
```

## 📊 統計情報の表示

プログラム終了時（Ctrl+C）に統計情報が表示されます。

```
==================================================
📊 統計情報
==================================================

【MultiSensor01】
  temperature:
    データ数: 3600
    平均: 25.34 °C
    最小: 18.20 °C
    最大: 31.50 °C
  humidity:
    データ数: 3600
    平均: 52.18 %
    最小: 35.40 %
    最大: 68.90 %
  light:
    データ数: 3600
    平均: 485.23 lux
    最小: 120.00 lux
    最大: 890.00 lux
==================================================
```

## 🔍 データの活用例

### SQLiteコマンドラインでのクエリ

```bash
# データベースに接続
sqlite3 sensor_data.db
```

#### 温度の時系列データを取得
```sql
SELECT timestamp, value
FROM sensor_data
WHERE sensor_id = 'MultiSensor01'
  AND data_type = 'temperature'
ORDER BY timestamp DESC
LIMIT 100;
```

#### 1時間ごとの平均温度を計算
```sql
SELECT
  strftime('%Y-%m-%d %H:00', timestamp) as hour,
  AVG(value) as avg_temp
FROM sensor_data
WHERE sensor_id = 'MultiSensor01'
  AND data_type = 'temperature'
GROUP BY hour
ORDER BY hour;
```

#### アラート発生回数をカウント
```sql
SELECT
  alert_type,
  COUNT(*) as count
FROM alerts
GROUP BY alert_type;
```

#### 最高温度と最低温度を取得
```sql
SELECT
  MAX(value) as max_temp,
  MIN(value) as min_temp
FROM sensor_data
WHERE data_type = 'temperature';
```

## 💡 実装のポイント

### 1. データベース接続の管理
```python
class DataLogger:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def close(self):
        self.conn.close()
```

### 2. トランザクションの確実な実行
```python
cursor.execute("INSERT INTO ...", (values,))
self.conn.commit()  # 確実にコミット
```

### 3. ISO形式のタイムスタンプ
```python
timestamp = datetime.now().isoformat()
# 例: "2025-11-11T15:30:45.123456"
```

## 📈 期待される動作

1. データロガーが起動し、データベースファイルを作成
2. センサーからデータが届くと自動的に記録
3. コンソールに記録状況が表示される
4. Ctrl+Cで停止すると統計情報が表示される
5. データベースファイルは永続化される

## 🔧 データベースファイルの場所

- **ファイル名**: `sensor_data.db`
- **保存先**: 実行ディレクトリ

## 🔄 カスタマイズ例

### 新しいセンサータイプの追加
```python
# 気圧データの記録
elif "pressure" in topic:
    pressure = float(payload)
    logger.log_sensor_data(sensor_id, "pressure", pressure, "hPa")
```

### データ保持期間の制限
```python
def cleanup_old_data(self, days=7):
    """古いデータを削除"""
    cursor = self.conn.cursor()
    cursor.execute('''
        DELETE FROM sensor_data
        WHERE timestamp < datetime('now', '-' || ? || ' days')
    ''', (days,))
    self.conn.commit()
```

### CSV エクスポート機能
```python
def export_to_csv(self, filename):
    """データをCSVにエクスポート"""
    import csv
    cursor = self.conn.cursor()
    cursor.execute("SELECT * FROM sensor_data")

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'sensor_id', 'timestamp', 'data_type', 'value', 'unit'])
        writer.writerows(cursor.fetchall())
```

## 🎓 学習ポイント

1. **SQLiteの基礎**: データベースの作成、テーブル設計、CRUD操作
2. **データの正規化**: 適切なテーブル構造の設計
3. **永続化**: アプリケーション終了後もデータを保持
4. **統計分析**: SQLの集約関数を使ったデータ分析
5. **エラーハンドリング**: データベース操作の安全な実行

## ⚠️ 注意事項

### データベースサイズの管理
長時間実行すると、データベースファイルが大きくなります。

```bash
# データベースサイズを確認
ls -lh sensor_data.db
```

定期的に古いデータを削除するか、別のストレージに移動してください。

### 同時アクセス
SQLiteは軽量ですが、同時書き込みには制限があります。高負荷環境では PostgreSQL や MySQL の使用を検討してください。

## 🔗 関連ドキュメント

- [../../study/step5/01_IoTシステム構築実践.md](../../../../study/step5/01_IoTシステム構築実践.md)
- [../../study/step5/05_応用コード集.md](../../../../study/step5/05_応用コード集.md)
- [SQLite公式ドキュメント](https://www.sqlite.org/docs.html)
