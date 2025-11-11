# MQTT実験コード集 - Step4 Labs

## 📖 概要

このディレクトリには、MQTT（Message Queuing Telemetry Transport）プロトコルの主要機能を学ぶための5つの実践的な実験プログラムが含まれています。各実験は独立して実行可能で、段階的にMQTTの理解を深められるよう設計されています。

## 🎯 学習目標

- QoS（Quality of Service）レベルの理解と使い分け
- Retain（保持）メッセージの活用方法
- Last Will（遺言）機能を使った監視システム
- 実践的なIoTセンサーの実装パターン
- MQTTトラフィックの分析手法

## 📁 実験一覧

### [Lab 1: QoS性能比較ベンチマーク](./lab1_qos_benchmark/)

**難易度**: ⭐☆☆☆☆ (初級)

QoS 0、1、2の性能差を計測するベンチマークツール。各QoSレベルで100個のメッセージを送信し、配信速度の違いを体感できます。

**主な学習内容**:
- QoSレベルによる性能トレードオフ
- 適切なQoS選択の判断基準
- ベンチマーク測定の実装方法

**実行コマンド**:
```bash
cd lab1_qos_benchmark
python qos_benchmark.py
```

---

### [Lab 2: Retain削除ツール](./lab2_retain_cleaner/)

**難易度**: ⭐⭐☆☆☆ (初中級)

MQTTブローカーに蓄積されたRetainメッセージを検索・削除するメンテナンスツール。ワイルドカード購読を活用した実践的なツールです。

**主な学習内容**:
- Retainメッセージの仕組みと削除方法
- ワイルドカード購読（`#`）の活用
- メッセージフラグの判定方法

**実行コマンド**:
```bash
cd lab2_retain_cleaner
python clear_retained.py
```

---

### [Lab 3: Last Will監視システム](./lab3_lastwill_monitor/)

**難易度**: ⭐⭐⭐☆☆ (中級)

Last Will機能を活用したデバイス監視システム。複数デバイスのオンライン/オフライン状態をリアルタイムで監視し、異常切断を検出します。

**主な学習内容**:
- Last Will（遺言）機能の実装
- ワイルドカード購読（`+`）の使い方
- デバイス監視システムの設計パターン
- トピック階層構造の活用

**実行コマンド**:
```bash
cd lab3_lastwill_monitor
python lastwill_monitor_system.py
```

---

### [Lab 4: 全機能統合センサー](./lab4_ultimate_sensor/)

**難易度**: ⭐⭐⭐⭐☆ (中上級)

QoS、Retain、Last Willをすべて統合した実践的な温度センサーシミュレータ。実際のIoTデバイスで使用される設計パターンを学べます。

**主な学習内容**:
- 各機能を適材適所で組み合わせる実装
- データの重要度に応じたQoS選択
- プロダクションレディなコード設計
- 複数インスタンスの管理

**実行コマンド**:
```bash
cd lab4_ultimate_sensor
python ultimate_sensor.py Sensor01
```

---

### [Lab 5: メッセージカウンター](./lab5_message_counter/)

**難易度**: ⭐⭐☆☆☆ (初中級)

MQTTトラフィックをリアルタイムで監視し、QoSレベルごとの統計情報を表示する分析ツール。システムの特性把握に役立ちます。

**主な学習内容**:
- リアルタイムメッセージ監視の実装
- トラフィック分析手法
- メッセージメタデータの活用
- デバッグツールの開発

**実行コマンド**:
```bash
cd lab5_message_counter
python message_counter.py
```

---

## 🚀 クイックスタート

### 前提条件

1. **Docker Desktop** がインストールされ、起動していること
2. **Python 3.x** がインストールされていること
3. **paho-mqtt** ライブラリのインストール

```bash
pip install paho-mqtt
```

### MQTTブローカーの起動

```bash
# Mosquittoコンテナの起動
docker run -it -p 1883:1883 eclipse-mosquitto
```

または、プロジェクトルートのMosquitto設定を使用：

```bash
cd ../../..  # プロジェクトルートへ
docker run -it -p 1883:1883 \
  -v ./mqtt/config:/mosquitto/config \
  -v ./mqtt/data:/mosquitto/data \
  -v ./mqtt/log:/mosquitto/log \
  eclipse-mosquitto
```

### 動作確認

ブローカーが起動したら、別のターミナルで実験を開始：

```bash
# Lab 1を試す
cd mqtt_clients/step4/labs/lab1_qos_benchmark
python qos_benchmark.py
```

## 📚 推奨学習順序

### 初心者向け

1. **Lab 1** (QoS性能比較) → QoSの基本を理解
2. **Lab 5** (メッセージカウンター) → トラフィック監視の基礎
3. **Lab 2** (Retain削除ツール) → Retainメッセージの操作
4. **Lab 3** (Last Will監視) → 監視システムの構築
5. **Lab 4** (全機能統合センサー) → 統合的な実装

### 実践演習向け

**シナリオ1: システム全体を動かす**

```bash
# ターミナル1: 監視システム起動
cd lab3_lastwill_monitor
python lastwill_monitor_system.py

# ターミナル2: センサー1起動
cd lab4_ultimate_sensor
python ultimate_sensor.py Sensor01

# ターミナル3: センサー2起動
cd lab4_ultimate_sensor
python ultimate_sensor.py Sensor02

# ターミナル4: トラフィック分析
cd lab5_message_counter
python message_counter.py
```

**シナリオ2: パフォーマンステスト**

```bash
# ターミナル1: カウンター起動
cd lab5_message_counter
python message_counter.py

# ターミナル2: ベンチマーク実行
cd lab1_qos_benchmark
python qos_benchmark.py
```

**シナリオ3: メンテナンス作業**

```bash
# 1. 現在のRetainメッセージを確認
cd lab2_retain_cleaner
python clear_retained.py

# 2. センサーを起動してRetainメッセージを生成
cd lab4_ultimate_sensor
python ultimate_sensor.py TestSensor

# 3. 再度確認して削除
cd lab2_retain_cleaner
python clear_retained.py
```

## 🔬 実験の組み合わせ例

### 実験A: Last Will機能の検証

1. Lab 3の監視システムを起動
2. Lab 4のセンサーを起動
3. センサーをCtrl+Cで強制終了
4. 監視システムでOFFLINE通知を確認

### 実験B: QoSレベルの効果測定

1. Lab 5のカウンターを起動
2. Lab 1のベンチマークを実行
3. 各QoSレベルのメッセージ数を確認
4. 性能とメッセージ配信の関係を分析

### 実験C: マルチセンサー環境の構築

1. Lab 5のカウンターを起動
2. Lab 4のセンサーを複数起動（異なるID）
3. Lab 3の監視システムで状態を確認
4. トラフィックパターンを分析

## 🛠️ トラブルシューティング

### ブローカーに接続できない

```bash
# ポート1883が使用されているか確認
netstat -an | grep 1883

# Dockerコンテナの状態確認
docker ps

# ブローカーの再起動
docker restart <container_id>
```

### メッセージが受信されない

```bash
# mosquitto_subで直接確認
mosquitto_sub -h localhost -p 1883 -t "#" -v

# ファイアウォールの確認
# Windows: Windowsファイアウォールの設定を確認
# Mac/Linux: iptablesやufwの設定を確認
```

### Pythonライブラリのエラー

```bash
# paho-mqttの再インストール
pip uninstall paho-mqtt
pip install paho-mqtt

# バージョン確認
pip show paho-mqtt
```

## 📖 各実験の詳細

各実験のフォルダには、詳細な`README.md`が含まれています：

- 実験の目的と学習目標
- コードの詳細な解説
- 実行方法と実行例
- 応用例とカスタマイズ方法
- トラブルシューティング

必ず各実験のREADME.mdを参照してください。

## 🎓 さらなる学習

### 推奨リソース

- [MQTT公式仕様](https://mqtt.org/mqtt-specification/)
- [Eclipse Paho Documentation](https://www.eclipse.org/paho/)
- [HiveMQ MQTT Essentials](https://www.hivemq.com/mqtt-essentials/)

### 次のステップ

1. **セキュリティ**: TLS/SSL、認証・認可の実装
2. **スケーラビリティ**: 負荷分散、クラスタリング
3. **データ処理**: データベース保存、リアルタイム分析
4. **可視化**: Webダッシュボード、グラフ表示
5. **本番運用**: 監視、ログ、エラーハンドリング

### 応用プロジェクト例

- スマートホームシミュレーター
- 工場設備監視システム
- リアルタイムチャットアプリケーション
- 車両テレメトリシステム
- 農業IoT（温湿度・土壌センサー）

## 📝 フィードバック・貢献

バグ報告や改善提案は、GitHubのIssueまでお願いします。

## ⚖️ ライセンス

このプロジェクトは学習目的で作成されています。自由に使用・改変してください。

---

## 🎉 最後に

これらの実験を通じて、MQTTの基礎から実践的な応用まで、体系的に学ぶことができます。各実験を順番に試しながら、IoT通信の世界を楽しんでください！

**Happy Hacking! 🚀**
