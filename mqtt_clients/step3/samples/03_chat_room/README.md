# 💬 サンプル3：簡易チャットルーム

## 概要

複数のユーザーがリアルタイムでメッセージを交換できる簡易チャットアプリケーションです。MQTTのPub/Subパターンを活用し、ユーザー間の非同期通信を実現します。

## 動作説明

### システムの動作フロー

```
チャットルームの全体像:

┌─────────────────────┐
│  chat_client.py     │
│  (User: Alice)      │──┐
└─────────────────────┘  │
                         │
┌─────────────────────┐  │         ┌─────────────────┐
│  chat_client.py     │  ├────────>│  MQTT Broker    │
│  (User: Bob)        │──┤         │  (localhost)    │
└─────────────────────┘  │         └─────────────────┘
                         │                 │
┌─────────────────────┐  │                 │
│  chat_client.py     │  │                 ↓
│  (User: Carol)      │──┘         全員に配信される
└─────────────────────┘            (ブロードキャスト)
```

### メッセージフロー

```
時系列での動作:

1. Alice が接続
   └─> chat/lobby/# を購読

2. Bob が接続
   └─> chat/lobby/# を購読

3. Alice が "Hello!" を送信
   ├─> chat/lobby/Alice に Publish
   └─> Bob と Carol が受信

4. Bob が "Hi Alice!" を返信
   ├─> chat/lobby/Bob に Publish
   └─> Alice と Carol が受信

各ユーザーは自分のメッセージ以外を画面に表示
```

### 詳細な動作シーケンス

```
User: Alice
────────────────────────────────────────────────────
1. ユーザー名入力: "Alice"
2. ブローカーに接続
3. "chat/lobby/#" を購読
4. ループ開始（バックグラウンドスレッド）
5. メッセージ入力待ち

User input: "Hello everyone!"
   ↓
6. Publish: chat/lobby/Alice → "Hello everyone!"
   ↓
7. ブローカーが全購読者に配信
   ↓
8. Alice自身も受信するが、自分のIDと一致するため表示しない
   ↓
9. Bob、Carolは受信して画面に表示
```

## 技術的なポイント

### 1. マルチスレッド処理

**バックグラウンドループ**:
```python
client.loop_start()  # 別スレッドでメッセージ受信を開始

# メインスレッドではユーザー入力を処理
try:
    while True:
        message = input("あなた> ")
        # ...
except KeyboardInterrupt:
    pass

client.loop_stop()   # ループを停止
```

**スレッド構造**:
```
┌─ Main Thread ─────────┐    ┌─ Network Thread ────┐
│                        │    │                      │
│  input() で待機        │    │  loop_start()        │
│  ↓                     │    │  ↓                   │
│  メッセージ入力        │    │  メッセージ受信待機  │
│  ↓                     │    │  ↓                   │
│  publish()             │    │  on_message()呼び出し│
│  ↓                     │    │  ↓                   │
│  再度 input() へ       │    │  画面に表示          │
└────────────────────────┘    └──────────────────────┘
```

### 2. 自分のメッセージをフィルタリング

```python
def on_message(client, userdata, msg):
    sender = msg.topic.split('/')[-1]  # トピックから送信者名を取得
    message = msg.payload.decode()

    # 自分のメッセージは表示しない
    if sender != client._client_id.decode():
        print(f"\n💬 {sender}: {message}")
        print("あなた> ", end="", flush=True)  # プロンプト再表示
```

**重要な技術**:
- `client._client_id`: クライアントIDにアクセス
- `flush=True`: バッファをフラッシュして即座に表示
- `end=""`: 改行を制御

### 3. トピック設計

```
chat/                    ← アプリケーションカテゴリ
  └─ lobby/              ← チャットルーム名
      ├─ Alice           ← ユーザー名（送信者識別）
      ├─ Bob
      └─ Carol
```

**利点**:
- ルーム別の購読が可能: `chat/general/#`, `chat/developers/#`
- 送信者がトピック名で識別できる
- ワイルドカード購読で全メッセージを受信

### 4. ユーザーインターフェースの工夫

**プロンプトの維持**:
```python
print(f"\n💬 {sender}: {message}")
print("あなた> ", end="", flush=True)  # 入力プロンプトを再表示
```

**問題点**:
- 入力中にメッセージが届くと表示が乱れる
- 非同期入出力の難しさ

**改善案**:
```python
# cursesライブラリやreadlineを使用
import readline
# または、GUIフレームワーク（tkinter、PyQt5）を使用
```

### 5. クライアントID = ユーザー名

```python
username = input("ユーザー名を入力: ")
client = mqtt.Client(username)  # ユーザー名をクライアントIDに
```

**利点**:
- シンプルな実装
- ユーザー識別が容易

**注意点**:
- 同じユーザー名で複数接続すると、古い接続が切断される
- 実運用ではUUIDなどを使用し、ユーザー名はペイロードに含める

### 6. メッセージのブロードキャスト

**Pub/Subの威力**:
```python
# 送信側: 送信先を意識しない
client.publish(f"{ROOM}/{username}", message)

# 受信側: 全員が受信（自動配信）
# ブローカーが自動的に全購読者に配信
```

**従来のチャット（ソケット通信）との比較**:
```python
# ソケット方式（複雑）:
for user in connected_users:
    socket.send(user, message)  # 手動で全員に送信

# MQTT方式（シンプル）:
client.publish(topic, message)  # ブローカーが自動配信
```

## 設計・実装のポイント

### アーキテクチャ上の工夫

1. **対称的な設計**
   - 全クライアントが同じコードで動作
   - Publisher + Subscriber の両方の役割
   - サーバーレスアーキテクチャ

2. **スケーラビリティ**
   ```python
   # ユーザー数に制限なし
   # クライアントの追加・削除が動的
   # ブローカーが全ての負荷を処理
   ```

3. **リアルタイム性**
   - メッセージは即座に全員に配信
   - QoS 0（デフォルト）で最低遅延
   - loop_start()による非同期処理

### 拡張可能な設計

**複数ルーム対応**:
```python
ROOM = input("参加するルームを入力: ")  # "lobby", "developers", など
client.subscribe(f"chat/{ROOM}/#")
client.publish(f"chat/{ROOM}/{username}", message)
```

**プライベートメッセージ**:
```python
# 特定ユーザーへのDM
if message.startswith("@"):
    target_user = message.split()[0][1:]  # @Bob → Bob
    actual_message = " ".join(message.split()[1:])
    client.publish(f"chat/private/{target_user}",
                  f"From {username}: {actual_message}")
```

**入退室通知**:
```python
# Last Will（遺言）機能を活用
client.will_set(f"chat/{ROOM}/system",
                f"{username} が退室しました",
                qos=1)

# 入室通知
client.publish(f"chat/{ROOM}/system",
              f"{username} が入室しました")
```

### エラーハンドリング

```python
try:
    while True:
        message = input("あなた> ")
        if message.lower() == "quit":
            break
        if message.strip():  # 空メッセージを送信しない
            client.publish(f"{ROOM}/{username}", message)
except KeyboardInterrupt:
    pass
except Exception as e:
    print(f"エラー: {e}")
finally:
    client.loop_stop()
    client.disconnect()
    print("\n👋 チャットを終了しました")
```

## 使用方法

### 前提条件

- MQTTブローカー（Mosquitto）が起動していること
- paho-mqttライブラリがインストール済みであること

### 実行手順

1. **ターミナル1でAliceとして接続**:
   ```bash
   cd mqtt_clients/samples/03_chat_room
   python chat_client.py
   ```

   ```
   ユーザー名を入力: Alice

   👋 ようこそ、Aliceさん！
   💬 メッセージを入力してください（'quit'で終了）

   あなた>
   ```

2. **ターミナル2でBobとして接続**:
   ```bash
   python chat_client.py
   ```

   ```
   ユーザー名を入力: Bob

   👋 ようこそ、Bobさん！
   💬 メッセージを入力してください（'quit'で終了）

   あなた>
   ```

3. **ターミナル3でCarolとして接続（オプション）**:
   ```bash
   python chat_client.py
   ```

4. **メッセージを送信**:

   Alice側:
   ```
   あなた> Hello everyone!
   ```

   Bob側（自動表示）:
   ```
   💬 Alice: Hello everyone!
   あなた>
   ```

   Carol側（自動表示）:
   ```
   💬 Alice: Hello everyone!
   あなた>
   ```

5. **終了**: 各ターミナルで `quit` と入力するか、`Ctrl+C`

### 使用例

```
Alice: Hello everyone!
Bob: Hi Alice! How are you?
Carol: Hey guys!
Alice: I'm good, thanks! Working on MQTT project.
Carol: Cool! MQTT is awesome!
Bob: Agreed! This chat is so smooth.
```

## 学習ポイント

### 初級レベル

- ✅ **ブロードキャスト通信**: 1対多の通信パターン
- ✅ **トピック階層**: ルーム/ユーザー構造
- ✅ **リアルタイム通信**: 即座にメッセージが届く

### 中級レベル

- ✅ **マルチスレッド**: loop_start()の活用
- ✅ **UI制御**: プロンプト表示の工夫
- ✅ **フィルタリング**: 自分のメッセージを除外

### 上級レベル

- ✅ **サーバーレス設計**: ブローカーのみでチャット実現
- ✅ **スケーラブルアーキテクチャ**: 無制限のユーザー対応
- ✅ **拡張性**: 機能追加が容易な設計

## 応用アイデア

1. **複数ルーム対応**:
   ```python
   # ユーザーが参加するルームを選択
   rooms = ["lobby", "developers", "gaming"]
   ```

2. **タイムスタンプ追加**:
   ```python
   import datetime
   timestamp = datetime.datetime.now().strftime("%H:%M:%S")
   print(f"[{timestamp}] 💬 {sender}: {message}")
   ```

3. **メッセージ履歴**:
   ```python
   # Retained Messageで最後のメッセージを保持
   client.publish(topic, message, retain=True)
   ```

4. **ユーザーリスト表示**:
   ```python
   # 定期的にハートビートを送信
   # 一定時間応答のないユーザーをオフラインとみなす
   ```

5. **GUI版の実装**:
   ```python
   # tkinterやPyQt5でグラフィカルなチャットウィンドウ
   ```

6. **ファイル送信**:
   ```python
   # Base64エンコードでファイルを送信
   import base64
   ```

7. **絵文字・リアクション**:
   ```python
   # 特定のコマンドで絵文字を送信
   if message == ":+1:":
       message = "👍"
   ```

## トラブルシューティング

### よくある問題

1. **メッセージが重複して表示される**:
   - 自分のメッセージフィルタリングが動作していない
   - client._client_idとusernameが一致しているか確認

2. **入力中に表示が乱れる**:
   - これは現在の実装の制限事項
   - readlineやcursesライブラリで改善可能

3. **同じユーザー名で複数接続できない**:
   - これは意図的な設計（クライアントID重複防止）
   - 異なるユーザー名を使用してください

4. **終了時にエラーが出る**:
   - KeyboardInterruptの処理を確認
   - loop_stop()とdisconnect()が正しく呼ばれているか確認

## まとめ

このサンプルでは、MQTTを使ったマルチユーザーアプリケーションの基本を学べます。サーバーレスで動作するチャットシステムは、IoTデバイス間の通信やリアルタイムダッシュボードなど、様々な応用が可能です。シンプルな実装でありながら、実用的なチャットアプリケーションの基礎が詰まっています。
