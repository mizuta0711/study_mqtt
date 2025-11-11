# 応用例5：アラートシステム

## 📊 概要

異常値を検出して、アラートを受信・表示し、適切な対処方法を提示するアラート監視システムです。

## 🎯 学習目標

- アラートメッセージの購読と処理
- センサーステータスの監視
- アラート履歴の管理
- 異常時の対処方法の提示

## 📁 ファイル構成

```
05_alert_system/
├── README.md         # このファイル
└── alert_monitor.py  # アラート監視システム
```

## 🚀 実行方法

### 1. アラート監視システムの起動

```bash
python mqtt_clients/step5/advance/05_alert_system/alert_monitor.py
```

### 2. センサーの起動（別ターミナル）

```bash
# マルチセンサーを起動（アラート送信機能あり）
python mqtt_clients/step5/advance/01_multi_sensor_system/multi_sensor_publisher.py
```

## ✨ 主な機能

### アラート監視
- ✅ **アラート受信**: `alerts/#` トピックを購読
- ✅ **詳細表示**: アラートの種類、値、メッセージを表示
- ✅ **対処方法提示**: アラートに応じた対処方法を表示
- ✅ **アラート履歴**: すべてのアラートを記録

### ステータス監視
- ✅ **センサーステータス**: ONLINE/OFFLINE を監視
- ✅ **ダウン検知**: OFFLINEになったセンサーを検知
- ✅ **ステータス変更通知**: ステータス変更時に通知

### サマリー表示
- ✅ **総アラート数**: プログラム終了時に表示
- ✅ **種類別集計**: アラートの種類ごとに集計
- ✅ **最新アラート**: 直近5件のアラートを表示

## 🚨 アラート条件

### 温度アラート
| 条件 | アラート | 対処方法 |
|:---|:---|:---|
| > 30°C | 高温警報 | 冷房を強化してください |
| < 18°C | 低温警報 | 暖房を入れてください |

### 湿度アラート
| 条件 | アラート | 対処方法 |
|:---|:---|:---|
| > 70% | 高湿度警報 | 除湿器を使用してください |
| < 30% | 低湿度警報 | 加湿器を使用してください |

### センサーダウン
| 条件 | アラート | 対処方法 |
|:---|:---|:---|
| OFFLINE | デバイスダウン | センサーの状態を確認してください |

## 📊 アラート表示例

### アラート発生時

```
🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨
⚠️  アラート発生！
時刻: 2025-11-11 15:35:12
センサー: MultiSensor01
種類: temperature
値: 31.2
メッセージ: 高温警報
🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨

💡 対処: 冷房を強化してください
```

### センサーダウン時

```
🔴 [2025-11-11 16:00:00] MultiSensor01 がオフラインになりました
⚠️  MultiSensor01 のダウンを検知しました！
💡 対処: センサーの状態を確認してください
```

## 📊 サマリー表示例

プログラム終了時（Ctrl+C）に表示されます。

```
==================================================
📊 アラート監視サマリー
==================================================

総アラート数: 15

【種類別アラート数】
  temperature: 8件
  humidity: 7件

【最新のアラート（最大5件）】
  [2025-11-11 15:35:12] MultiSensor01: 高温警報
  [2025-11-11 15:36:45] MultiSensor01: 低湿度警報
  [2025-11-11 15:38:20] MultiSensor01: 高温警報
  [2025-11-11 15:40:15] MultiSensor01: 低温警報
  [2025-11-11 15:42:30] MultiSensor01: 高湿度警報

【センサーステータス】
  🟢 MultiSensor01: ONLINE
  🔴 RealisticSensor01: OFFLINE
==================================================
```

## 💡 実装のポイント

### 1. アラートデータの解析

```python
alert_data = json.loads(payload)
sensor_id = alert_data.get("sensor_id", "Unknown")
alert_type = alert_data.get("type", "unknown")
value = alert_data.get("value", 0)
alert_msg = alert_data.get("alert", "")
```

### 2. アラート履歴の管理

```python
alert_history.append({
    "timestamp": timestamp,
    "sensor_id": sensor_id,
    "type": alert_type,
    "value": value,
    "message": alert_msg
})
```

### 3. ステータス変更の検知

```python
previous_status = sensor_status.get(sensor_id, None)
sensor_status[sensor_id] = payload

if previous_status != payload:
    # ステータス変更を処理
    pass
```

## 🔧 カスタマイズ例

### 1. アラート通知先の追加

#### Slack通知
```python
import requests

def send_slack_alert(message):
    webhook_url = "YOUR_WEBHOOK_URL"
    payload = {"text": message}
    requests.post(webhook_url, json=payload)
```

#### メール通知
```python
import smtplib
from email.message import EmailMessage

def send_email_alert(subject, body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = "alert@example.com"
    msg['To'] = "admin@example.com"
    msg.set_content(body)

    with smtplib.SMTP('smtp.example.com', 587) as smtp:
        smtp.starttls()
        smtp.login("user", "password")
        smtp.send_message(msg)
```

### 2. アラート閾値のカスタマイズ

```python
# カスタム閾値
THRESHOLDS = {
    "temperature": {"high": 28.0, "low": 20.0},
    "humidity": {"high": 65.0, "low": 35.0}
}
```

### 3. アラート音の追加

```python
import winsound  # Windows
# または
import os  # Mac/Linux

def play_alert_sound():
    # Windows
    winsound.Beep(1000, 500)  # 1000Hz, 500ms

    # Mac/Linux
    # os.system('play --no-show-progress --null --channels 1 synth 0.5 sine 1000')
```

## 📊 統計情報の活用

### アラート頻度の分析

```python
def analyze_alert_frequency():
    """アラート頻度を分析"""
    from collections import Counter
    from datetime import datetime, timedelta

    # 過去1時間のアラートを集計
    one_hour_ago = datetime.now() - timedelta(hours=1)
    recent_alerts = [
        a for a in alert_history
        if datetime.fromisoformat(a['timestamp']) > one_hour_ago
    ]

    # センサーごとにカウント
    sensor_counts = Counter(a['sensor_id'] for a in recent_alerts)

    print("過去1時間のアラート:")
    for sensor_id, count in sensor_counts.items():
        print(f"  {sensor_id}: {count}件")
```

## 🎓 学習ポイント

1. **イベント駆動プログラミング**: アラート発生時の非同期処理
2. **データの集約**: アラート履歴の管理と統計
3. **状態管理**: センサーステータスの追跡
4. **ユーザー通知**: わかりやすいアラート表示
5. **エラーハンドリング**: 不正なデータの処理

## 🔗 関連ドキュメント

- [../../study/step5/01_IoTシステム構築実践.md](../../../../study/step5/01_IoTシステム構築実践.md)
- [../../study/step5/05_応用コード集.md](../../../../study/step5/05_応用コード集.md)
