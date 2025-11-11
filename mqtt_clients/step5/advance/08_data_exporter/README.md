# 応用例8：データエクスポート機能

## 📊 概要

収集したセンサーデータをCSVやJSON形式でエクスポートし、外部ツールで分析できるようにします。

## 🎯 学習目標

- データのエクスポート方法
- CSV/JSON形式の理解
- ファイル操作の基礎
- データの永続化

## 📁 ファイル構成

```
08_data_exporter/
├── README.md         # このファイル
└── data_exporter.py  # データエクスポートツール
```

## 🚀 実行方法

### 1. データエクスポーターの起動

```bash
python mqtt_clients/step5/advance/08_data_exporter/data_exporter.py
```

### 2. データ収集

センサーを起動してデータを収集します（別ターミナル）。

```bash
python mqtt_clients/step5/advance/03_realistic_sensor/realistic_sensor_publisher.py
```

### 3. エクスポート

プログラムを停止（Ctrl+C）すると、自動的にエクスポートされます。

## ✨ 主な機能

### データ収集
- ✅ **リアルタイム収集**: センサーデータを受信
- ✅ **バッファリング**: メモリ上にデータを保持
- ✅ **タイムスタンプ**: 受信時刻を記録

### エクスポート機能
- ✅ **CSV形式**: Excel等で開ける
- ✅ **JSON形式**: プログラムで処理しやすい
- ✅ **自動ファイル名**: 日時を含むファイル名
- ✅ **UTF-8エンコード**: 日本語対応

## 📊 エクスポート形式

### CSV形式

```csv
timestamp,sensor_id,type,value,unit
2025-11-11 15:30:45,MultiSensor01,temperature,25.3,°C
2025-11-11 15:30:45,MultiSensor01,humidity,52.1,%
2025-11-11 15:30:45,MultiSensor01,light,480,lux
```

**特徴:**
- Excelで開ける
- 軽量で扱いやすい
- グラフ作成が簡単

### JSON形式

```json
[
  {
    "timestamp": "2025-11-11 15:30:45",
    "sensor_id": "MultiSensor01",
    "type": "temperature",
    "value": 25.3,
    "unit": "°C"
  },
  {
    "timestamp": "2025-11-11 15:30:45",
    "sensor_id": "MultiSensor01",
    "type": "humidity",
    "value": 52.1,
    "unit": "%"
  }
]
```

**特徴:**
- プログラムで読みやすい
- 階層構造を表現可能
- API連携に便利

## 💡 実装のポイント

### 1. CSV エクスポート

```python
import csv

def export_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'sensor_id', 'type', 'value', 'unit'])

        for record in data:
            writer.writerow([
                record['timestamp'],
                record['sensor_id'],
                record['type'],
                record['value'],
                record['unit']
            ])
```

### 2. JSON エクスポート

```python
import json

def export_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```

### 3. ファイル名の生成

```python
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"sensor_data_{timestamp}.csv"
```

## 📊 ファイル出力例

### 生成されるファイル

```
sensor_data_20251111_153045.csv
sensor_data_20251111_153045.json
```

### ファイルサイズの目安

- 1時間分（3600件）: 約200KB (CSV), 約400KB (JSON)
- 1日分（86400件）: 約5MB (CSV), 約10MB (JSON)

## 🔧 カスタマイズ例

### 圧縮してエクスポート

```python
import gzip
import json

def export_to_json_gz(data, filename):
    with gzip.open(filename + '.gz', 'wt', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```

### 特定期間のデータのみエクスポート

```python
from datetime import datetime, timedelta

def filter_by_date(data, hours=1):
    """過去N時間のデータのみ"""
    cutoff = datetime.now() - timedelta(hours=hours)

    return [
        record for record in data
        if datetime.fromisoformat(record['timestamp']) > cutoff
    ]
```

### Excel形式でエクスポート

```python
import pandas as pd

def export_to_excel(data, filename):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
```

## 📊 データの活用例

### Excelでグラフ作成

1. CSVファイルをExcelで開く
2. データを選択
3. 「挿入」→「グラフ」を選択
4. 折れ線グラフを作成

### Pythonで分析

```python
import pandas as pd
import matplotlib.pyplot as plt

# CSVを読み込み
df = pd.read_csv('sensor_data_20251111_153045.csv')

# 温度データのみ抽出
temp_df = df[df['type'] == 'temperature']

# グラフ表示
plt.plot(temp_df['timestamp'], temp_df['value'])
plt.xlabel('時刻')
plt.ylabel('温度 (°C)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

### JSONをAPIで送信

```python
import requests
import json

# JSONファイルを読み込み
with open('sensor_data_20251111_153045.json', 'r') as f:
    data = json.load(f)

# APIに送信
response = requests.post(
    'https://api.example.com/data',
    json=data
)
```

## 🎓 学習ポイント

1. **ファイル操作**: Python のファイル入出力
2. **データ形式**: CSV vs JSON の使い分け
3. **エンコーディング**: UTF-8 の重要性
4. **データの永続化**: メモリからストレージへ
5. **外部ツール連携**: Excel, Pandas, API等

## 🔗 関連ドキュメント

- [../../study/step5/05_応用コード集.md](../../../../study/step5/05_応用コード集.md)
