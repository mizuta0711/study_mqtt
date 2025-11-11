# 🏠 サンプル4：スマートホームシミュレータ

## 概要

スマートホームのIoTデバイス（照明、エアコン、ドア）を遠隔制御するシステムです。コントローラーからコマンドを送信し、デバイスが応答する双方向通信を実装しています。実際のIoTシステムと同じアーキテクチャを体験できます。

## 動作説明

### システムアーキテクチャ

```
┌──────────────────────────────┐         ┌──────────────────────────────┐
│  smart_home_controller.py    │         │  smart_home_devices.py       │
│  (コントローラー)            │         │  (デバイス群)                │
├──────────────────────────────┤         ├──────────────────────────────┤
│  ・コマンド送信              │         │  ・照明（Light）             │
│  ・状態確認                  │         │  ・エアコン（AC）            │
│  ・ユーザーインターフェース  │         │  ・ドア（Door）              │
└──────────────────────────────┘         └──────────────────────────────┘
         │                                           │
         │ ① Control Command                        │
         ├──> home/control/light "on" ──────────────>│
         │                                           │
         │                                 ② 状態変更 & 確認
         │                                           │
         │ ③ Status Feedback                        │
         │<──────────── home/status/light "on" ─────┤
         │                                           │


        中央: MQTT Broker (localhost:1883)
```

### 通信フロー詳細

```
シーケンス図:

Controller                Broker              Devices
    │                       │                    │
    │ ①購読開始             │                    │
    ├─subscribe("home/status/#")─>│             │
    │                       │                    │
    │                       │      ②購読開始     │
    │                       │<─subscribe("home/control/#")
    │                       │                    │
    │ ③コマンド送信         │                    │
    ├─publish("home/control/light", "on")─>│    │
    │                       │                    │
    │                       ├──────────────────>│ ④コマンド受信
    │                       │                    ├─ 照明をON
    │                       │                    │
    │                       │      ⑤状態通知     │
    │                       │<─publish("home/status/light", "on")
    │                       │                    │
    │ ⑥状態受信             │                    │
    │<────────────────────  │                    │
    ├─ "✅ lightの状態: on" │                    │
```

### デバイス状態管理

```python
# Devices側の状態テーブル
devices = {
    "light": "off",    # 照明: off / on
    "ac": "off",       # エアコン: off / on
    "door": "locked"   # ドア: locked / unlocked
}

# コマンド受信時の状態遷移
light: off → on → off → on ...
ac:    off → on → off → on ...
door:  locked → unlocked → locked ...
```

## 技術的なポイント

### 1. トピック設計（コマンド/ステータス分離）

**制御用トピック（Controller → Devices）**:
```
home/control/
  ├─ light       # 照明制御
  ├─ ac          # エアコン制御
  └─ door        # ドア制御
```

**状態通知トピック（Devices → Controller）**:
```
home/status/
  ├─ light       # 照明状態
  ├─ ac          # エアコン状態
  └─ door        # ドア状態
```

**この設計の利点**:
- 制御と状態を明確に分離
- 一方向のメッセージフローが明確
- セキュリティ設定が容易（将来的にACLを設定可能）

### 2. デバイス側の実装（状態管理）

```python
# デバイスの状態をディクショナリで管理
devices = {
    "light": "off",
    "ac": "off",
    "door": "locked"
}

def on_message(client, userdata, msg):
    # トピックからデバイス名を抽出
    device = msg.topic.split('/')[-1]  # "home/control/light" → "light"
    command = msg.payload.decode()     # "on"

    if device in devices:
        devices[device] = command  # 状態更新

        # デバイスごとの処理
        if device == "light":
            emoji = "💡" if command == "on" else "🌙"
            print(f"{emoji} 照明を{command}にしました")

        # 状態フィードバックを送信
        client.publish(f"home/status/{device}", command)
```

### 3. コントローラー側の実装（コマンド送信）

```python
# 非同期でループを開始
client.loop_start()

try:
    while True:
        command = input("\nコマンド> ").strip().split()

        if len(command) == 2:
            device, action = command
            # 制御コマンドを送信
            client.publish(f"home/control/{device}", action)
        else:
            print("❌ 使い方: <device> <action>")

except KeyboardInterrupt:
    pass
finally:
    client.loop_stop()
    client.disconnect()
```

### 4. 双方向フィードバックループ

```
Request-Response パターン:

1. Controller: コマンド送信
   └─> home/control/light "on"

2. Device: コマンド実行
   ├─> 内部状態を更新
   └─> 結果をフィードバック

3. Device: 状態通知
   └─> home/status/light "on"

4. Controller: 状態受信
   └─> "✅ lightの状態: on" を表示
```

**メリット**:
- コマンドが正しく実行されたか確認できる
- デバイスの現在状態を常に把握
- エラー時の検知が可能

### 5. デバイスごとの個別処理

```python
if device == "light":
    emoji = "💡" if command == "on" else "🌙"
    print(f"{emoji} 照明を{command}にしました")
elif device == "ac":
    emoji = "❄️" if command == "on" else "🔥"
    print(f"{emoji} エアコンを{command}にしました")
elif device == "door":
    emoji = "🔓" if command == "unlocked" else "🔒"
    print(f"{emoji} ドアを{command}にしました")
```

**拡張性**:
- 新しいデバイスの追加が容易
- デバイスごとに異なるロジックを実装可能
- プラグイン的な設計も可能

### 6. マルチスレッド処理（Controller側）

```python
client.loop_start()  # バックグラウンドで受信

# メインスレッドでユーザー入力を待機
while True:
    command = input("\nコマンド> ")
    # コマンド処理
```

**スレッド構造**:
```
Main Thread:           Network Thread:
  input() 待機    ←→    メッセージ受信
     ↓                       ↓
  publish()               on_message()
     ↓                       ↓
  再度input()へ            画面に表示
```

## 設計・実装のポイント

### IoTアーキテクチャのベストプラクティス

1. **トピックの命名規則**
   ```
   <namespace>/<function>/<device>

   home/control/light     # 制御
   home/status/light      # 状態
   home/config/light      # 設定（将来の拡張）
   home/telemetry/light   # テレメトリ（将来の拡張）
   ```

2. **状態同期**
   - デバイス側が状態の唯一の真実（Single Source of Truth）
   - コントローラーは状態通知を受けて表示
   - 状態の不整合を防ぐ

3. **冪等性の考慮**
   ```python
   # 同じコマンドを複数回送信しても安全
   # "on" → "on" は問題なし
   devices["light"] = "on"  # 常に同じ結果
   ```

### 実際のIoTシステムとの対応

| このサンプル | 実際のIoT | 説明 |
|------------|----------|------|
| smart_home_controller.py | スマホアプリ/Web UI | ユーザーインターフェース |
| MQTT Broker | AWS IoT Core / Azure IoT Hub | クラウドサービス |
| smart_home_devices.py | ESP32/Raspberry Pi | 物理デバイス |

### 拡張可能な設計

**1. センサー値の追加**:
```python
# 温度センサーなどを追加
client.publish("home/sensor/temperature", "22.5")
```

**2. JSONペイロードの使用**:
```python
import json

# より詳細な制御
command = {
    "action": "on",
    "brightness": 80,  # 明るさ
    "color": "warm"    # 色温度
}
client.publish("home/control/light", json.dumps(command))
```

**3. 認証・認可**:
```python
# MQTTブローカーの設定でACLを追加
# controller: home/control/* に Publish 可
# devices: home/control/* を Subscribe 可
```

**4. エラー処理**:
```python
def on_message(client, userdata, msg):
    try:
        device = msg.topic.split('/')[-1]
        command = msg.payload.decode()

        if device not in devices:
            error_msg = f"Unknown device: {device}"
            client.publish("home/error", error_msg)
            return

        # 正常処理
        # ...
    except Exception as e:
        client.publish("home/error", str(e))
```

## 使用方法

### 前提条件

- MQTTブローカー（Mosquitto）が起動していること
- paho-mqttライブラリがインストール済みであること

### 実行手順

1. **ターミナル1でデバイス側を起動**:
   ```bash
   cd mqtt_clients/samples/04_smart_home
   python smart_home_devices.py
   ```

   出力:
   ```
   🏠 スマートホームシステム起動
   ⏳ コマンドを待っています...
   ```

2. **ターミナル2でコントローラーを起動**:
   ```bash
   cd mqtt_clients/samples/04_smart_home
   python smart_home_controller.py
   ```

   出力:
   ```
   🎮 スマートホームコントローラー
   --------------------------------------------------
   コマンド:
     light on/off
     ac on/off
     door locked/unlocked
     quit - 終了
   --------------------------------------------------

   コマンド>
   ```

3. **コマンドを実行**:

   **照明をONにする**:
   ```
   コマンド> light on
   ```

   Devices側の出力:
   ```
   💡 照明をonにしました
   ```

   Controller側の出力:
   ```
   ✅ lightの状態: on
   ```

   **エアコンをONにする**:
   ```
   コマンド> ac on
   ```

   **ドアを解錠する**:
   ```
   コマンド> door unlocked
   ```

4. **終了**: Controller側で `quit` と入力

### コマンド一覧

| コマンド | 説明 |
|---------|------|
| `light on` | 照明をON |
| `light off` | 照明をOFF |
| `ac on` | エアコンをON |
| `ac off` | エアコンをOFF |
| `door locked` | ドアを施錠 |
| `door unlocked` | ドアを解錠 |
| `quit` | 終了 |

## 学習ポイント

### 初級レベル

- ✅ **IoT制御の基本**: デバイスの遠隔操作
- ✅ **双方向通信**: コマンドとフィードバック
- ✅ **トピック分離**: control/statusの分離設計

### 中級レベル

- ✅ **状態管理**: デバイスの状態を保持
- ✅ **コマンドパース**: トピックからデバイス名抽出
- ✅ **非同期UI**: loop_start()でバックグラウンド処理

### 上級レベル

- ✅ **IoTアーキテクチャ**: 実際のシステム設計
- ✅ **スケーラビリティ**: デバイス追加が容易
- ✅ **エラーハンドリング**: 不正なコマンドへの対応

## 応用アイデア

1. **センサーデータの統合**:
   ```python
   # 温度、湿度、人感センサーなどを追加
   sensors = {
       "temperature": 22.5,
       "humidity": 60,
       "motion": False
   }
   ```

2. **自動化ルール**:
   ```python
   # 温度が28度を超えたらエアコンON
   if temperature > 28:
       client.publish("home/control/ac", "on")
   ```

3. **スケジュール機能**:
   ```python
   import schedule
   # 毎日7時に照明をON
   schedule.every().day.at("07:00").do(turn_on_light)
   ```

4. **音声制御の統合**:
   ```python
   # Google Home / Alexa との連携
   # 音声コマンドをMQTTメッセージに変換
   ```

5. **Web UI**:
   ```python
   # Flask / FastAPI でWeb インターフェース
   # ブラウザからデバイス制御
   ```

6. **ログ記録**:
   ```python
   # 全てのコマンドと状態変化をデータベースに記録
   import sqlite3
   ```

7. **シーン機能**:
   ```python
   # "おやすみ"シーン: 照明OFF、エアコンOFF、ドア施錠
   scenes = {
       "おやすみ": [
           ("light", "off"),
           ("ac", "off"),
           ("door", "locked")
       ]
   }
   ```

## トラブルシューティング

### よくある問題

1. **コマンドを送信しても反応がない**:
   - Devices側が起動しているか確認
   - トピック名が正しいか確認（typoに注意）
   - ブローカーが起動しているか確認

2. **状態フィードバックが届かない**:
   - Controller側が `home/status/#` を購読しているか確認
   - Devices側が正しく状態を送信しているか確認

3. **不正なコマンドを送信するとエラー**:
   ```
   コマンド> lamp on
   (反応なし)
   ```
   - デバイス名は `light`, `ac`, `door` のみ有効

4. **複数のControllerから制御したい**:
   - 複数起動可能（異なるクライアントIDが自動生成される）
   - 全てのControllerが同じ状態通知を受信

## まとめ

このサンプルでは、MQTTを使った実践的なIoTシステムの基礎を学べます。制御コマンドと状態フィードバックを分離した設計は、実際のスマートホームシステムやインダストリアルIoTでも使われる標準的なパターンです。シンプルながら、拡張性が高く、実用的なアーキテクチャとなっています。
