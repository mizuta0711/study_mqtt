# 📚 MQTTサンプルコード集

このディレクトリには、MQTTプロトコルの様々な活用例を示す6つのサンプルプログラムが含まれています。各サンプルは独立して動作し、段階的にMQTTの機能を学べるように設計されています。

## 📋 サンプル一覧

### 01. 📊 リアルタイム株価シミュレータ
**難易度**: ⭐☆☆☆☆

株式市場の価格変動をリアルタイムで配信・監視するシステムです。

**学習内容**:
- 基本的なPub/Subパターン
- トピック階層の活用
- ワイルドカード購読（`#`）

**ファイル**:
- `stock_publisher.py` - 価格データ配信
- `stock_monitor.py` - 価格監視

**詳細**: [01_stock_simulator/README.md](./01_stock_simulator/README.md)

---

### 02. 🎲 サイコロゲーム
**難易度**: ⭐⭐☆☆☆

2人のプレイヤーがMQTT経由でサイコロを振り合う対戦ゲームです。

**学習内容**:
- 双方向通信
- 状態管理（グローバル変数）
- 複数クライアント間の協調動作

**ファイル**:
- `dice_player1.py` - 後攻プレイヤー（シンプルなPublisher）
- `dice_player2.py` - 先攻プレイヤー（Publisher + Subscriber）

**詳細**: [02_dice_game/README.md](./02_dice_game/README.md)

---

### 03. 💬 簡易チャットルーム
**難易度**: ⭐⭐⭐☆☆

複数ユーザーがリアルタイムでメッセージを交換できるチャットシステムです。

**学習内容**:
- マルチユーザー通信
- マルチスレッド処理（`loop_start()`）
- ブロードキャスト配信

**ファイル**:
- `chat_client.py` - チャットクライアント（複数起動可能）

**詳細**: [03_chat_room/README.md](./03_chat_room/README.md)

---

### 04. 🏠 スマートホームシミュレータ
**難易度**: ⭐⭐⭐☆☆

IoTデバイス（照明、エアコン、ドア）を遠隔制御するシステムです。

**学習内容**:
- コマンド/ステータスの分離設計
- IoTアーキテクチャの基礎
- 双方向フィードバックループ

**ファイル**:
- `smart_home_devices.py` - デバイス側（状態管理）
- `smart_home_controller.py` - コントローラー側（コマンド送信）

**詳細**: [04_smart_home/README.md](./04_smart_home/README.md)

---

### 05. 🚗 配達トラッキングシステム
**難易度**: ⭐⭐⭐⭐☆

配達車両の位置情報をリアルタイムで追跡し、プログレスバーで表示します。

**学習内容**:
- 時系列データの送信
- プログレスバー実装（上書き表示）
- データフォーマット（パイプ区切り）

**ファイル**:
- `delivery_vehicle.py` - 配達車両シミュレータ
- `delivery_tracker.py` - 追跡ダッシュボード

**詳細**: [05_delivery_tracking/README.md](./05_delivery_tracking/README.md)

---

### 06. 📈 センサーダッシュボード（JSON使用）
**難易度**: ⭐⭐⭐⭐☆

複数センサー（温度、湿度、気圧）のデータをJSON形式で送受信します。

**学習内容**:
- JSON形式によるデータ交換
- 複数データの一括送信
- データのシリアライゼーション/デシリアライゼーション

**ファイル**:
- `multi_sensor.py` - センサーデータ送信
- `sensor_dashboard.py` - ダッシュボード表示

**詳細**: [06_sensor_dashboard/README.md](./06_sensor_dashboard/README.md)

---

## 🚀 はじめ方

### 前提条件

1. **MQTTブローカー（Mosquitto）の起動**:
   ```bash
   docker run -it -p 1883:1883 -v ./mqtt/config:/mosquitto/config -v ./mqtt/data:/mosquitto/data -v ./mqtt/log:/mosquitto/log eclipse-mosquitto
   ```

2. **Python環境**:
   ```bash
   pip install paho-mqtt
   ```

### 実行順序（推奨）

初心者の方は、以下の順序で学習することをお勧めします：

1. **01_stock_simulator** - Pub/Subの基本を理解
2. **02_dice_game** - 双方向通信を体験
3. **03_chat_room** - マルチユーザー通信を学ぶ
4. **04_smart_home** - IoT制御の基礎を学ぶ
5. **05_delivery_tracking** - 時系列データと可視化
6. **06_sensor_dashboard** - JSON形式でのデータ交換

## 📖 学習マトリックス

| サンプル | Pub/Sub | 双方向 | マルチ<br>ユーザー | JSON | IoT制御 | 可視化 |
|---------|---------|-------|-------------------|------|---------|--------|
| 01_株価 | ✅ | - | - | - | - | - |
| 02_サイコロ | ✅ | ✅ | - | - | - | - |
| 03_チャット | ✅ | ✅ | ✅ | - | - | - |
| 04_スマートホーム | ✅ | ✅ | - | - | ✅ | - |
| 05_配達 | ✅ | - | - | - | - | ✅ |
| 06_センサー | ✅ | - | - | ✅ | ✅ | ✅ |

## 🔑 主要な技術概念

### 1. Pub/Sub（発行/購読）パターン
すべてのサンプルで使用される基本パターンです。
- **Publisher**: メッセージを送信
- **Subscriber**: メッセージを受信
- **Broker**: メッセージを仲介

### 2. トピック階層
```
stock/AAPL              # 株価データ
game/dice/player1       # ゲームデータ
home/control/light      # デバイス制御
sensors/data            # センサーデータ
```

### 3. ワイルドカード
- `#` - すべてのサブトピック（例: `stock/#`）
- `+` - 単一レベル（例: `home/control/+`）

### 4. QoS（Quality of Service）
- **QoS 0**: 最大1回配信（デフォルト、これらのサンプルで使用）
- **QoS 1**: 最低1回配信（確認応答付き）
- **QoS 2**: 正確に1回配信（重複なし保証）

### 5. データフォーマット
- **文字列**: シンプルなデータ（01, 02, 03, 04, 05）
- **JSON**: 構造化データ（06）

## 🛠️ よくある使い方

### 基本的な実行パターン

```bash
# パターン1: Publisher/Subscriber型
# ターミナル1: Subscriberを先に起動
python subscriber.py

# ターミナル2: Publisherを起動
python publisher.py
```

```bash
# パターン2: 複数クライアント型
# ターミナル1
python client.py

# ターミナル2
python client.py

# ターミナル3
python client.py
```

### ブローカーの動作確認

```bash
# Subscriberとして接続
mosquitto_sub -t test/topic

# Publisherとして送信
mosquitto_pub -t test/topic -m "Hello MQTT"
```

## 💡 カスタマイズのヒント

### トピック名の変更
```python
# 変更前
TOPIC = "sensors/data"

# 変更後（複数センサー対応）
TOPIC = f"sensors/{room_name}/data"
```

### 更新頻度の調整
```python
# 変更前
time.sleep(2)  # 2秒間隔

# 変更後
time.sleep(5)  # 5秒間隔（負荷軽減）
```

### データフォーマットの拡張
```python
# 文字列 → JSON
import json

# 変更前
client.publish(topic, str(value))

# 変更後
data = {"value": value, "timestamp": time.time()}
client.publish(topic, json.dumps(data))
```

## 🐛 トラブルシューティング

### 接続エラー
```
ConnectionRefusedError: [Errno 111] Connection refused
```
**解決策**: Mosquittoブローカーが起動しているか確認

### メッセージが届かない
**チェックリスト**:
- [ ] ブローカーが起動している
- [ ] トピック名が送信側と受信側で一致している
- [ ] Subscriberが先に起動している（サンプルによる）
- [ ] ネットワーク接続が正常

### 文字化け
**解決策**: UTF-8エンコーディングを確認
```python
msg.payload.decode('utf-8')  # 明示的にUTF-8指定
```

## 📚 参考資料

- [MQTT公式サイト](https://mqtt.org/)
- [Eclipse Mosquitto](https://mosquitto.org/)
- [Paho MQTT Python Client](https://www.eclipse.org/paho/index.php?page=clients/python/index.php)

## 🎓 次のステップ

これらのサンプルを完了したら、以下のような発展的なトピックに挑戦してみましょう：

1. **QoSレベルの実験** - QoS 1, 2を試す
2. **Retained Messages** - 新規接続時の初期値配信
3. **Last Will（遺言）** - 予期しない切断時の通知
4. **セキュリティ** - ユーザー認証、TLS/SSL暗号化
5. **クラウド連携** - AWS IoT Core, Azure IoT Hubとの統合
6. **実デバイス** - Raspberry Pi, ESP32での実装

## 🤝 貢献

バグ報告や改善提案は、GitHubのIssueでお願いします。

## 📄 ライセンス

これらのサンプルコードは学習目的で自由に使用・改変できます。

---

**Happy MQTT Learning! 🚀**
