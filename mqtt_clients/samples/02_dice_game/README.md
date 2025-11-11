# 🎲 サンプル2：サイコロゲーム

## 概要

2人のプレイヤーがMQTTを通じてサイコロを振り合い、大きい数字を出した方が勝ちという対戦型ゲームです。MQTTの双方向通信と、複数クライアント間の協調動作を体験できます。

## 動作説明

### ゲームの流れ

```
時系列での動作フロー:

1. Player2がSubscriberとして起動
   └─> game/dice/# を購読開始

2. Player2がサイコロを振る
   └─> game/dice/player2 に自分の出目を送信 (例: 4)

3. Player1がサイコロを振る
   └─> game/dice/player1 に自分の出目を送信 (例: 5)

4. Player2がPlayer1の出目を受信
   └─> 両者の出目を比較
   └─> 勝敗を判定して表示
```

### アーキテクチャ図

```
┌─────────────────────┐         ┌─────────────────┐         ┌─────────────────────┐
│  dice_player1.py    │         │  MQTT Broker    │         │  dice_player2.py    │
│  (後攻プレイヤー)   │         │  (localhost)    │         │  (先攻プレイヤー)   │
└─────────────────────┘         └─────────────────┘         └─────────────────────┘
         │                             │                              │
         │                             │                              │ ①購読開始
         │                             │<─────subscribe("game/dice/#")│
         │                             │                              │
         │                             │                              │ ②サイコロを振る
         │                             │<──publish("game/dice/player2", "4")
         │                             │                              │
         │ ③サイコロを振る             │                              │
         ├──publish("game/dice/player1", "5")────────>│              │
         │                             │               │              │
         │                             ├──────────────>│ ④メッセージ受信
         │                             │               │  "player1: 5"
         │                             │               │
         │                             │               │ ⑤勝敗判定
         │                             │               │  4 < 5 → 負け
         │                             │               └─> 結果表示
```

### Player1（後攻）の動作

1. **シンプルなPublisher**として動作
2. Enterキー入力待ち
3. サイコロを振る（1〜6のランダム値）
4. 結果を`game/dice/player1`トピックに送信
5. 即座に切断（勝敗判定はPlayer2が行う）

### Player2（先攻）の動作

1. **Publisher + Subscriber**の複合的な動作
2. 接続と同時に`game/dice/#`を購読
3. Enterキー入力後、サイコロを振る
4. 自分の結果を`game/dice/player2`に送信
5. Player1の結果を待機
6. Player1の出目を受信したら勝敗を判定
7. 結果を表示して切断

## 技術的なポイント

### 1. 非対称な設計パターン

**Player1（シンプル）**:
```python
client = mqtt.Client("Player1")
client.connect("localhost", 1883, 60)

# サイコロを振って送信するだけ
dice = random.randint(1, 6)
client.publish("game/dice/player1", str(dice))

client.disconnect()  # すぐに切断
```

**Player2（複雑）**:
```python
# グローバル変数で状態管理
player1_dice = None
player2_dice = None

def on_message(client, userdata, msg):
    global player1_dice, player2_dice

    # Player1の出目を受信
    if msg.topic == "game/dice/player1":
        player1_dice = int(msg.payload.decode())

    # 両方揃ったら勝敗判定
    if player1_dice and player2_dice:
        # 勝敗ロジック
        if player2_dice > player1_dice:
            print("🎉 あなたの勝ち！")
        # ...
```

### 2. 状態管理の実装

**グローバル変数による状態共有**:
```python
player1_dice = None  # 初期状態: 未受信
player2_dice = None

def on_message(client, userdata, msg):
    global player1_dice, player2_dice  # グローバル変数にアクセス
    # 状態を更新
```

**利点**:
- コールバック関数内から状態にアクセス可能
- 両プレイヤーの出目が揃った時点で判定

**注意点**:
- スレッドセーフではない（このサンプルでは問題なし）
- より複雑なケースではuserdataを活用

### 3. トピック命名規則

```
game/              ← ゲームカテゴリ
  └─ dice/         ← ゲーム種別
      ├─ player1   ← プレイヤー識別
      └─ player2
```

**設計のポイント**:
- 階層構造で管理しやすい
- ワイルドカード購読が可能: `game/dice/#`
- 拡張性: 他のゲーム（`game/poker/`, `game/chess/`）も追加可能

### 4. loop_forever() vs 手動切断

**Player1（即座に切断）**:
```python
client.publish(...)
client.disconnect()  # メッセージ送信後すぐ切断
```

**Player2（ループして待機）**:
```python
client.loop_start()  # バックグラウンドでループ開始
# メインスレッドでサイコロを振る
client.loop_forever()  # メッセージ受信を待ち続ける
```

### 5. 同期処理と非同期処理の混在

```python
# 非同期: バックグラウンドで受信待機
client.loop_start()

# 同期: メインスレッドでユーザー入力待ち
input("Enterキーでサイコロを振ります...")
dice = random.randint(1, 6)
client.publish(...)

# 非同期: コールバックで勝敗判定
client.loop_forever()
```

## 設計・実装のポイント

### アーキテクチャ上の工夫

1. **役割の明確化**
   - Player1: 単純なPublisher（後攻）
   - Player2: Publisher + Subscriber（先攻、審判役）

2. **状態遷移の管理**
   ```
   Player2の状態遷移:

   [起動] → [接続] → [購読] → [サイコロ振る] → [送信]
      ↓
   [待機] → [Player1受信] → [判定] → [表示] → [切断]
   ```

3. **タイミング制御**
   - Player2が先に起動・購読する必要がある
   - Player1のメッセージを取りこぼさないための設計

### エラーハンドリングと制約

**現在の設計の制限**:
- Player2が先に起動していないと、Player1のメッセージを受信できない
- Player1は勝敗を知らない（改善の余地あり）

**改善案**:
```python
# Retained Messageを使用
client.publish("game/dice/player1", str(dice), retain=True)

# または、共通の審判クライアントを作成
# judge.py が両者の出目を受信して判定
```

### データ型とシリアライゼーション

**シンプルな文字列形式**:
```python
# 送信
client.publish("game/dice/player1", str(dice))

# 受信
dice_value = int(msg.payload.decode())
```

**将来の拡張を考慮した設計**:
```python
import json

# より詳細な情報を含める
data = {
    "player": "Player1",
    "dice": 5,
    "timestamp": time.time()
}
client.publish("game/dice/player1", json.dumps(data))
```

### クライアントIDの管理

```python
client = mqtt.Client("Player1")  # 固定ID
client = mqtt.Client("Player2")
```

**重要性**:
- クライアントIDが重複すると、古い接続が切断される
- 実用的にはUUIDやタイムスタンプを使用

## 使用方法

### 前提条件

- MQTTブローカー（Mosquitto）が起動していること
- paho-mqttライブラリがインストール済みであること

### 実行手順

1. **ターミナル1でPlayer2を起動（先攻）**:
   ```bash
   cd mqtt_clients/samples/02_dice_game
   python dice_player2.py
   ```

   出力:
   ```
   🎲 プレイヤー2です
   Enterキーでサイコロを振ります...
   ```

2. **Enterキーを押してサイコロを振る**:
   ```
   🎲 あなたの出目: 4
   ```

3. **ターミナル2でPlayer1を起動（後攻）**:
   ```bash
   cd mqtt_clients/samples/02_dice_game
   python dice_player1.py
   ```

   出力:
   ```
   🎲 プレイヤー1です
   Enterキーでサイコロを振ります...
   ```

4. **Enterキーを押してサイコロを振る**:
   ```
   🎲 あなたの出目: 5
   ```

5. **Player2の画面で勝敗が表示される**:
   ```
   🎲 プレイヤー1の出目: 5

   ==================================================
   😢 あなたの負け...
   ==================================================
   ```

### 注意事項

- **必ずPlayer2を先に起動**してください
- Player1を先に起動すると、Player2がメッセージを受信できません

## 学習ポイント

### 初級レベル

- ✅ **双方向通信**: PublishとSubscribeの組み合わせ
- ✅ **クライアントID**: 複数クライアントの識別
- ✅ **トピック命名**: 階層的な構造

### 中級レベル

- ✅ **状態管理**: グローバル変数を使った状態共有
- ✅ **loop制御**: loop_start()とloop_forever()の使い分け
- ✅ **タイミング制御**: メッセージ送受信の順序

### 上級レベル

- ✅ **非対称設計**: 役割分担による効率化
- ✅ **システム設計**: 先攻・後攻の概念実装
- ✅ **拡張性**: 多人数対応への発展可能性

## 応用アイデア

1. **審判クライアントの追加**:
   ```
   judge.py が両プレイヤーの出目を受信し、
   結果を game/dice/result に配信
   ```

2. **Retained Messageの活用**:
   ```python
   # 後から接続しても最後の出目を取得できる
   client.publish(topic, message, retain=True)
   ```

3. **マルチラウンド対応**:
   ```python
   # 3回勝負など
   for round in range(3):
       # ラウンドごとの処理
   ```

4. **GUI実装**: tkinterやPyQt5で視覚的なインターフェース

5. **ランキングシステム**: データベースで勝敗記録を保存

## トラブルシューティング

### よくある問題

1. **Player2がPlayer1の出目を受信しない**:
   - Player2を先に起動してください
   - ブローカーが起動しているか確認

2. **結果が表示されない**:
   - 両方のプレイヤーがサイコロを振ったか確認
   - グローバル変数の初期化を確認

3. **接続が切れる**:
   - 同じクライアントIDで複数起動していないか確認
   - ブローカーのログを確認

## まとめ

このサンプルでは、MQTTを使った対話型アプリケーションの実装方法を学べます。特に、複数クライアント間の協調動作、状態管理、タイミング制御など、実践的なスキルが身につきます。シンプルなゲームですが、チャットアプリやマルチプレイヤーゲームの基礎となる重要な概念が詰まっています。
