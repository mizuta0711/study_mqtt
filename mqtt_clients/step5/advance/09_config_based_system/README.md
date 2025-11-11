# 応用例9：設定管理システム

## 📊 概要

JSON設定ファイルを使って、複数のセンサーとシステムの動作を柔軟に管理できるシステムです。

## 🎯 学習目標

- 設定ファイルの設計
- JSON形式の活用
- 設定駆動の開発
- 保守性の向上

## 📁 ファイル構成

```
09_config_based_system/
├── README.md                # このファイル
├── config.json              # 設定ファイル
└── config_based_system.py   # 設定ベースシステム
```

## 🚀 実行方法

### 1. 設定ファイルの編集

`config.json` を編集して、センサーやアラートの設定をカスタマイズします。

### 2. システムの起動

```bash
python mqtt_clients/step5/advance/09_config_based_system/config_based_system.py
```

## ✨ 主な機能

### 設定ファイル管理
- ✅ **ブローカー設定**: ホスト、ポート、認証情報
- ✅ **センサー設定**: 複数センサーの一括管理
- ✅ **閾値設定**: センサーごとの警告レベル
- ✅ **アラート設定**: 通知方法の選択

### 柔軟なカスタマイズ
- ✅ **コードなしで設定変更**: JSON編集のみで動作変更
- ✅ **センサーの追加/削除**: 設定ファイルで管理
- ✅ **複数環境対応**: 開発/本番で設定を切り替え

## 📊 設定ファイル (config.json)

### 基本構造

```json
{
  "broker": {
    "host": "localhost",
    "port": 1883,
    "username": null,
    "password": null
  },
  "sensors": [
    {
      "id": "living-room-temp",
      "type": "temperature",
      "location": "リビング",
      "topic": "sensors/living-room/temperature",
      "interval": 1,
      "qos": 0,
      "thresholds": {
        "min": 18.0,
        "max": 30.0
      }
    }
  ],
  "alerts": {
    "enabled": true,
    "console": true,
    "email": false,
    "slack": false
  }
}
```

### ブローカー設定

```json
"broker": {
  "host": "localhost",      // MQTTブローカーのホスト
  "port": 1883,             // ポート番号
  "username": null,         // 認証が必要な場合
  "password": null
}
```

### センサー設定

```json
"sensors": [
  {
    "id": "living-room-temp",           // センサーの一意なID
    "type": "temperature",               // センサータイプ
    "location": "リビング",              // 設置場所
    "topic": "sensors/living-room/temperature",  // MQTTトピック
    "interval": 1,                       // データ送信間隔（秒）
    "qos": 0,                           // QoSレベル
    "thresholds": {                     // 閾値設定
      "min": 18.0,                      // 最小値
      "max": 30.0                       // 最大値
    }
  }
]
```

### アラート設定

```json
"alerts": {
  "enabled": true,      // アラート機能の有効/無効
  "console": true,      // コンソールに表示
  "email": false,       // メール通知（未実装）
  "slack": false        // Slack通知（未実装）
}
```

## 💡 実装のポイント

### 1. 設定ファイルの読み込み

```python
import json

def load_config(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config('config.json')
```

### 2. センサーの動的生成

```python
sensors = []
for sensor_config in config['sensors']:
    sensor = Sensor(
        sensor_id=sensor_config['id'],
        sensor_type=sensor_config['type'],
        thresholds=sensor_config['thresholds']
    )
    sensors.append(sensor)
```

### 3. 設定の検証

```python
def validate_config(config):
    """設定の妥当性をチェック"""
    required_keys = ['broker', 'sensors', 'alerts']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"設定に {key} がありません")

    # ブローカー設定のチェック
    if 'host' not in config['broker']:
        raise ValueError("ブローカーのホストが指定されていません")
```

## 📊 使用例

### 複数センサーの管理

```json
"sensors": [
  {
    "id": "living-room-temp",
    "type": "temperature",
    "location": "リビング",
    "topic": "sensors/living-room/temperature",
    "thresholds": {"min": 18.0, "max": 30.0}
  },
  {
    "id": "bedroom-humid",
    "type": "humidity",
    "location": "寝室",
    "topic": "sensors/bedroom/humidity",
    "thresholds": {"min": 30.0, "max": 70.0}
  },
  {
    "id": "kitchen-light",
    "type": "light",
    "location": "キッチン",
    "topic": "sensors/kitchen/light",
    "thresholds": {"min": 0, "max": 1000}
  }
]
```

### 環境別設定

**開発環境 (config.dev.json)**
```json
{
  "broker": {
    "host": "localhost",
    "port": 1883
  }
}
```

**本番環境 (config.prod.json)**
```json
{
  "broker": {
    "host": "mqtt.example.com",
    "port": 8883,
    "username": "production_user",
    "password": "secure_password"
  }
}
```

## 🔧 カスタマイズ例

### 新しいセンサーの追加

1. `config.json` にセンサー設定を追加

```json
{
  "id": "garage-door",
  "type": "door",
  "location": "ガレージ",
  "topic": "sensors/garage/door",
  "qos": 2,
  "states": ["open", "closed"]
}
```

2. プログラムを再起動（コード変更不要）

### アラート閾値の変更

```json
"thresholds": {
  "min": 20.0,  // 18.0 → 20.0
  "max": 28.0   // 30.0 → 28.0
}
```

### データ送信間隔の変更

```json
"interval": 5  // 1秒 → 5秒
```

## 🎓 学習ポイント

1. **設定の外部化**: コードと設定の分離
2. **JSON の活用**: 構造化データの表現
3. **保守性の向上**: 設定変更でコード修正不要
4. **拡張性**: 新機能を設定で追加
5. **環境管理**: 開発/本番の設定切り替え

## 🔗 関連ドキュメント

- [../../study/step5/04_実践的な設計パターン.md](../../../../study/step5/04_実践的な設計パターン.md)
- [../../study/step5/05_応用コード集.md](../../../../study/step5/05_応用コード集.md)
