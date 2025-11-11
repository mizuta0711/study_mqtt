# 第1章：MQTTの基礎理解

## 🎯 この章で学ぶこと
- MQTTとは何か、なぜIoTで使われるのか
- MQTTの基本構成（Publisher、Subscriber、Broker）
- トピックとメッセージの仕組み
- QoS（品質保証レベル）について
- Retain と Last Will の機能
- 通信ポートについて

---

## 📖 MQTTとは何か

**MQTT（Message Queuing Telemetry Transport）** は、**軽量で効率的なメッセージング・プロトコル**です。

### 特徴
- **軽量**: データ量が少なく、低帯域幅のネットワークでも動作
- **Pub/Sub型**: 送信側と受信側が直接接続する必要がない（疎結合）
- **シンプル**: 実装が簡単で、組み込み機器でも利用可能
- **双方向通信**: デバイス間での双方向メッセージングが可能

### 身近な例で理解する
MQTTは **「雑誌の出版と購読」** に例えられます：

```
出版社（Publisher） → 本屋さん（Broker） → 読者（Subscriber）
```

- **出版社**：雑誌を発行する（メッセージを送信）
- **本屋さん**：雑誌を管理して、購読者に配達（メッセージを仲介）
- **読者**：興味のある雑誌を購読（メッセージを受信）

読者は出版社を知らなくても、本屋さんを通じて雑誌を受け取れます。これが **Pub/Sub（パブリッシュ/サブスクライブ）型** の仕組みです。

---

## 🌐 なぜIoTで使われるのか

### IoTデバイスの課題
- **限られたリソース**: バッテリー駆動、低メモリ、低処理能力
- **不安定なネットワーク**: Wi-Fi、モバイル回線の断続的な接続
- **大量のデバイス**: 数千〜数百万のセンサーが同時に通信

### MQTTが解決すること
✅ **省電力**: 軽量プロトコルでバッテリー消費を抑える
✅ **低帯域幅**: 小さなデータサイズで通信コストを削減
✅ **耐障害性**: 一時的な切断にも対応できる設計
✅ **スケーラビリティ**: 多数のデバイスを効率的に管理

### 実際の活用例
- **スマートホーム**: 温度センサー、照明制御、ドアロック
- **産業IoT**: 工場の機械監視、予知保全
- **農業IoT**: 土壌湿度センサー、自動灌漑システム
- **位置追跡**: 物流トラッキング、車両管理

---

## 🏗️ MQTTの基本構成

MQTTは **3つの主要コンポーネント** で構成されます：

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│  Publisher  │ ------> │   Broker    │ ------> │ Subscriber  │
│  (送信側)   │         │  (仲介者)   │         │  (受信側)   │
└─────────────┘         └─────────────┘         └─────────────┘
```

### 1️⃣ Publisher（パブリッシャー／送信側）
- **役割**: メッセージを作成し、特定のトピックに送信
- **例**: 温度センサーが「sensor/temperature」トピックに温度データを送信

```python
# Publisherの例
client.publish("sensor/temperature", "25.5")
```

### 2️⃣ Broker（ブローカー／仲介サーバー）
- **役割**: すべてのメッセージを受け取り、購読者に配信
- **機能**:
  - トピックごとにメッセージを管理
  - クライアントの接続状態を監視
  - メッセージの永続化（オプション）
- **代表的な実装**: Eclipse Mosquitto、HiveMQ、EMQX

### 3️⃣ Subscriber（サブスクライバー／受信側）
- **役割**: 興味のあるトピックを購読し、メッセージを受信
- **例**: ダッシュボードアプリが「sensor/temperature」を購読して温度を表示

```python
# Subscriberの例
client.subscribe("sensor/temperature")
```

### 重要なポイント
💡 **Publisher と Subscriber は直接接続しない**
すべての通信はBrokerを経由します。これにより、送信側と受信側が独立して動作できます。

---

## 📬 トピック（Topic）とメッセージ構造

### トピックとは
**トピック**は、メッセージの「宛先」を表す文字列です。階層構造を持ち、スラッシュ（`/`）で区切ります。

```
home/livingroom/temperature
home/bedroom/humidity
factory/machine1/status
factory/machine2/vibration
```

### トピックの階層構造
```
home/
├── livingroom/
│   ├── temperature
│   ├── humidity
│   └── light
└── bedroom/
    ├── temperature
    └── humidity
```

### ワイルドカード
複数のトピックを一度に購読できます：

| ワイルドカード | 意味 | 例 |
|:---:|:---|:---|
| `+` | 1階層のマッチ | `home/+/temperature` → リビングと寝室の温度 |
| `#` | すべての下位階層 | `home/#` → home配下のすべてのトピック |

```python
# すべての部屋の温度を購読
client.subscribe("home/+/temperature")

# homeのすべてのデータを購読
client.subscribe("home/#")
```

### メッセージ構造
MQTTメッセージは以下の要素で構成されます：

- **トピック**: メッセージの送信先
- **ペイロード**: 実際のデータ（文字列、JSON、バイナリなど）
- **QoS**: 配信品質レベル
- **Retain**: 保持フラグ

```
トピック: sensor/temperature
ペイロード: {"value": 25.5, "unit": "C", "timestamp": "2025-01-15T10:30:00Z"}
QoS: 1
Retain: false
```

---

## 🎚️ QoS（品質保証レベル）

**QoS（Quality of Service）** は、メッセージの配信保証レベルを指定します。

### QoS 0：最大1回（At most once）
- **配信保証**: なし（Fire and Forget）
- **速度**: 最速
- **用途**: リアルタイム性が重要で、たまにデータが欠けても問題ない場合

```
Publisher → Broker → Subscriber
（確認応答なし）
```

**例**: 1秒ごとに送信される温度データ（1つ欠けても次が来る）

### QoS 1：最低1回（At least once）
- **配信保証**: 確実に届く（重複の可能性あり）
- **速度**: 中程度
- **用途**: データの欠損が許容できない場合

```
Publisher → Broker → Subscriber
         ← ACK（確認応答）
```

**例**: センサーの異常値通知（確実に届ける必要がある）

### QoS 2：正確に1回（Exactly once）
- **配信保証**: 重複なく確実に1回だけ届く
- **速度**: 最も遅い（4回のやり取り）
- **用途**: 課金システムなど、重複が許されない場合

```
Publisher → Broker → Subscriber
         ← PUBREC
         → PUBREL
         ← PUBCOMP
```

**例**: 決済トランザクション、重要なコマンド

### QoSレベルの選び方

| 要件 | おすすめQoS |
|:---|:---:|
| リアルタイム性重視、データ欠損OK | **0** |
| データ欠損NG、重複は処理で対応可能 | **1** |
| 重複も欠損も絶対NG | **2** |

---

## 🔖 Retain（保持）機能

### Retainとは
**最後のメッセージをBrokerが保持し、新規Subscriberに即座に送信する機能**です。

### 動作の流れ
```
1. Publisher が "sensor/status" に "online" を送信（Retain=true）
2. Broker がこのメッセージを保持
3. 新しいSubscriberが "sensor/status" を購読
4. → 即座に "online" を受信（待機不要）
```

### 使用例
```python
# Retainメッセージの送信
client.publish("device/status", "online", retain=True)
```

### 活用シーン
- **デバイスの状態**: オンライン/オフライン
- **最新の設定値**: 照明の明るさ、エアコンの温度設定
- **最後の測定値**: センサーの最新データ

### 注意点
⚠️ 空のペイロード（`""`）をRetain=trueで送信すると、保存されたメッセージが削除されます。

```python
# Retainメッセージの削除
client.publish("device/status", "", retain=True)
```

---

## 💀 Last Will（遺言）機能

### Last Willとは
**クライアントが予期せず切断された際に、Brokerが自動的に送信するメッセージ**です。

### 仕組み
```
1. クライアントが接続時にLast Willを設定
2. 正常に切断 → Last Willは送信されない
3. 異常切断（ネットワーク障害、クラッシュ）→ Brokerが自動送信
```

### 設定例
```python
# Last Willの設定（接続前に実行）
client.will_set(
    topic="device/status",
    payload="offline",
    qos=1,
    retain=True
)
client.connect("localhost", 1883)
```

### 活用シーン
- **デバイス監視**: センサーの死活監視
- **アラート**: 異常切断の通知
- **状態管理**: オンライン/オフライン表示

### 具体例：センサーの死活監視
```python
# センサー側
client.will_set("sensor/status", "OFFLINE", qos=1, retain=True)
client.connect("broker", 1883)
client.publish("sensor/status", "ONLINE", retain=True)

# 監視側
def on_message(client, userdata, msg):
    if msg.payload.decode() == "OFFLINE":
        print("⚠️ センサーが切断されました！")
```

---

## 🔌 通信ポート

### デフォルトポート

| ポート | 用途 |
|:---:|:---|
| **1883** | MQTT（非暗号化） |
| **8883** | MQTT over TLS/SSL（暗号化） |
| **8083** | MQTT over WebSocket |
| **8084** | MQTT over WebSocket（暗号化） |

### ポート 1883（標準MQTT）
- **用途**: ローカル環境、テスト、学習
- **セキュリティ**: なし（平文通信）
- **接続例**:
  ```python
  client.connect("localhost", 1883, 60)
  ```

### ポート 8883（MQTT over TLS/SSL）
- **用途**: 本番環境、インターネット経由の通信
- **セキュリティ**: 暗号化、証明書認証
- **接続例**:
  ```python
  client.tls_set(ca_certs="ca.crt")
  client.connect("broker.example.com", 8883, 60)
  ```

### ポート選択のガイドライン

| 環境 | おすすめポート |
|:---|:---:|
| ローカル開発・学習 | **1883** |
| インターネット経由 | **8883** |
| Webアプリケーション | **8083/8084** |

⚠️ **本番環境では必ず暗号化ポート（8883）を使用してください！**

---

## 📝 まとめ

### この章で学んだこと

✅ **MQTTは軽量なPub/Sub型プロトコル** → IoTに最適
✅ **3つの構成要素** → Publisher、Broker、Subscriber
✅ **トピックで宛先を指定** → 階層構造とワイルドカード
✅ **QoS 0/1/2** → 配信保証レベルを用途に応じて選択
✅ **Retain** → 新規Subscriberに最後のメッセージを即座に配信
✅ **Last Will** → 異常切断時の自動通知
✅ **ポート 1883/8883** → 非暗号化/暗号化

### 次のステップ
第2章では、実際にDocker上でMQTT Broker（Eclipse Mosquitto）を動かしてみます！

---

## 🔍 理解度チェック

以下の質問に答えられるか確認してみましょう：

1. MQTTの「Pub/Sub型」とはどういう意味ですか？
2. PublisherとSubscriberは直接接続しますか？
3. トピック「home/+/temperature」は何を購読しますか？
4. QoS 0、1、2の違いを説明してください。
5. Retain機能はどんな場合に便利ですか？
6. Last Willメッセージはいつ送信されますか？

### 解答例
<details>
<summary>クリックして解答を表示</summary>

1. **Pub/Sub型**: 送信側（Publisher）と受信側（Subscriber）が直接接続せず、Brokerを介してメッセージをやり取りする方式。疎結合で柔軟性が高い。

2. **接続しません**。すべての通信はBrokerを経由します。

3. **home配下の任意の1階層のtemperatureトピック**（例: `home/livingroom/temperature`, `home/bedroom/temperature`）

4.
   - **QoS 0**: 配信保証なし（最速、データ欠損の可能性あり）
   - **QoS 1**: 最低1回配信（確実だが重複の可能性あり）
   - **QoS 2**: 正確に1回配信（重複なし、最も遅い）

5. **デバイスの最新状態を新規Subscriberに即座に通知したい場合**（例: センサーの最新値、デバイスのオンライン状態）

6. **クライアントが異常切断（予期しない切断）された時に自動送信**されます。正常切断では送信されません。

</details>

---

**次の章**: [第2章：Dockerブローカーのセットアップ](../step2/00_学習ガイド.md)
