# 応用例10：完全統合システム

## 📊 概要

これまでの応用例（01〜09）のすべての機能を統合した総合IoTシステムです。

## 🎯 学習目標

- システム統合の手法
- マルチスレッドプログラミング
- 大規模システムの設計
- 実用的なIoTシステムの構築

## 📁 ファイル構成

```
10_integrated_system/
├── README.md              # このファイル
├── config.json            # システム設定ファイル
└── integrated_system.py   # 統合システム本体
```

## 🚀 実行方法

### 基本起動

```bash
python mqtt_clients/step5/advance/10_integrated_system/integrated_system.py
```

### オプション付き起動

```bash
# カスタム設定ファイルを使用
python mqtt_clients/step5/advance/10_integrated_system/integrated_system.py --config my_config.json

# デバッグモード
python mqtt_clients/step5/advance/10_integrated_system/integrated_system.py --debug

# ダッシュボードなし
python mqtt_clients/step5/advance/10_integrated_system/integrated_system.py --no-dashboard
```

## ✨ 統合された機能

### 1. 複数センサーシミュレーション（応用例01, 03）
- ✅ 温度、湿度、照度センサー
- ✅ リアルな時刻依存変化
- ✅ センサーステータス管理

### 2. リアルタイムダッシュボード（応用例02）
- ✅ 3つのグラフ同時表示
- ✅ 統計情報表示
- ✅ 閾値ライン表示

### 3. データロギング（応用例04）
- ✅ SQLiteデータベースに保存
- ✅ タイムスタンプ付き記録
- ✅ 統計情報の計算

### 4. アラートシステム（応用例05）
- ✅ 異常値の検出
- ✅ アラート履歴の管理
- ✅ 対処方法の提示

### 5. 統計分析（応用例06）
- ✅ リアルタイム統計計算
- ✅ トレンド検出
- ✅ 定期レポート

### 6. リモートコントロール（応用例07）
- ✅ デバイス制御機能
- ✅ コマンド送受信
- ✅ ステータス確認

### 7. データエクスポート（応用例08）
- ✅ CSV/JSON形式
- ✅ 定期的な自動保存
- ✅ 手動エクスポート

### 8. 設定管理（応用例09）
- ✅ JSON設定ファイル
- ✅ 柔軟なカスタマイズ
- ✅ 環境別設定

## 📊 システムアーキテクチャ

```
┌─────────────────────────────────────────────────┐
│         統合IoTシステム                          │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │センサー  │  │データ    │  │アラート  │     │
│  │シミュ    │─→│ロガー    │  │システム  │     │
│  │レーター  │  │(SQLite)  │  │          │     │
│  └──────────┘  └──────────┘  └──────────┘     │
│       │              │              │          │
│       ↓              ↓              ↓          │
│  ┌──────────────────────────────────────┐     │
│  │     MQTTブローカー (Mosquitto)      │     │
│  └──────────────────────────────────────┘     │
│       ↓              ↓              ↓          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ダッシュ  │  │統計分析  │  │エクスポ  │     │
│  │ボード    │  │ツール    │  │ーター    │     │
│  └──────────┘  └──────────┘  └──────────┘     │
│                                                 │
└─────────────────────────────────────────────────┘
```

## 💡 実装のポイント

### 1. マルチスレッド設計

```python
import threading

# センサーシミュレーションスレッド
sensor_thread = threading.Thread(target=run_sensors, daemon=True)
sensor_thread.start()

# 統計分析スレッド
stats_thread = threading.Thread(target=run_statistics, daemon=True)
stats_thread.start()

# ダッシュボードスレッド
dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
dashboard_thread.start()
```

### 2. 共有データの管理

```python
from threading import Lock

data_lock = Lock()
sensor_data = {}

def add_data(sensor_id, value):
    with data_lock:
        sensor_data[sensor_id] = value
```

### 3. グレースフルシャットダウン

```python
import signal

def signal_handler(sig, frame):
    print("\nシステムを停止します...")
    stop_all_threads()
    export_data()
    close_database()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
```

## 📊 実行例

### 起動時

```
==================================================
🚀 完全統合IoTシステム
==================================================
バージョン: 1.0.0
設定ファイル: config.json

【システム構成】
  ✅ センサーシミュレーター: 3個
  ✅ データロガー: 有効
  ✅ アラートシステム: 有効
  ✅ 統計分析: 有効
  ✅ ダッシュボード: 有効

【ブローカー接続】
  ホスト: localhost
  ポート: 1883

システム起動完了
==================================================
```

### 実行中

```
[15:30:45] 🌡️  25.3°C | 💧 52.1% | 💡 480 lux
[15:30:46] 🌡️  25.5°C | 💧 51.8% | 💡 475 lux

🚨 アラート発生！
  時刻: 15:35:12
  センサー: living-room-temp
  値: 31.2°C
  メッセージ: 高温警報

📊 統計レポート (15:40:00)
  温度: 平均 25.4°C, 範囲 18.2〜31.5°C
  湿度: 平均 52.3%, 範囲 35.4〜68.9%
  トレンド: 上昇傾向 ↗
```

## 🔧 コマンドラインオプション

```bash
# ヘルプ表示
python integrated_system.py --help

# 設定ファイル指定
python integrated_system.py --config production.json

# デバッグモード
python integrated_system.py --debug

# 機能の選択的起動
python integrated_system.py --no-dashboard --no-export

# データベースファイル指定
python integrated_system.py --db sensor_data.db
```

## 📊 期待される動作フロー

1. **起動**
   - 設定ファイルを読み込み
   - データベースを初期化
   - MQTTブローカーに接続

2. **センサーデータ送信**
   - 各センサーが定期的にデータを送信
   - データロガーがデータベースに保存

3. **リアルタイム監視**
   - ダッシュボードがグラフを更新
   - アラートシステムが異常値を検知

4. **定期処理**
   - 統計分析が1分ごとに実行
   - データが定期的にエクスポート

5. **停止**
   - 全スレッドを停止
   - 最終データをエクスポート
   - データベースをクローズ

## 🎓 学習ポイント

1. **システム統合**: 複数のコンポーネントを統合
2. **並行処理**: マルチスレッドでの並行実行
3. **データ同期**: スレッド間のデータ共有
4. **エラーハンドリング**: 全体的なエラー処理
5. **スケーラビリティ**: 拡張可能な設計

## 🔗 関連ドキュメント

- [../../study/step5/01_IoTシステム構築実践.md](../../../../study/step5/01_IoTシステム構築実践.md)
- [../../study/step5/04_実践的な設計パターン.md](../../../../study/step5/04_実践的な設計パターン.md)
- [../../study/step5/05_応用コード集.md](../../../../study/step5/05_応用コード集.md)

## 📝 注意事項

- システムリソースを多く使用します
- 長時間実行時はデータベースサイズに注意
- ダッシュボード表示にはGUI環境が必要
- 複数のスレッドが実行されるため、適切なCPUリソースが必要

---

**これで、MQTT学習の集大成となる完全統合システムの完成です！**

すべての機能を組み合わせることで、実用的なIoTシステムの全体像を理解できます。
