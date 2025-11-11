# 🚗 サンプル5：配達トラッキングシステム

## 概要

配達車両の現在位置と進捗状況をリアルタイムで追跡するシステムです。配達車両（Vehicle）が位置情報を送信し、トラッカー（Tracker）がそれをプログレスバーで視覚化します。物流・配送業界で使われる実際のトラッキングシステムと同じ仕組みを体験できます。

## 動作説明

### システムアーキテクチャ

```
┌───────────────────────────┐         ┌───────────────────────────┐
│  delivery_vehicle.py      │         │  delivery_tracker.py      │
│  (配達車両)               │────────>│  (追跡システム)           │
├───────────────────────────┤         ├───────────────────────────┤
│  ・位置情報の生成         │         │  ・位置情報の受信         │
│  ・進捗状況の計算         │         │  ・プログレスバー表示     │
│  ・定期的な更新送信       │         │  ・完了検知               │
└───────────────────────────┘         └───────────────────────────┘
         │                                         │
         │  delivery/van01/location                │
         └─────────────────────────────────────────┘
                  MQTT Broker経由
```

### 配達の進行シーケンス

```
配達ルート（6つのポイント）:

倉庫 → 高速道路 → SA(休憩中) → 市街地 → 配達先エリア → 配達完了
 0%      20%        40%        60%        80%         100%

┌─────────────────────────────────────────────────────────┐
│ Timeline                                                 │
├─────────────────────────────────────────────────────────┤
│ 0s:  📍 倉庫            [░░░░░░░░░░░░░░░░░░░░] 0%       │
│ 2s:  📍 高速道路        [████░░░░░░░░░░░░░░░░] 20%      │
│ 4s:  📍 SA（休憩中）     [████████░░░░░░░░░░░░] 40%      │
│ 6s:  📍 市街地          [████████████░░░░░░░░] 60%      │
│ 8s:  📍 配達先エリア     [████████████████░░░░] 80%      │
│ 10s: 📍 配達完了        [████████████████████] 100%     │
└─────────────────────────────────────────────────────────┘
```

### データフロー

```
Vehicle (Publisher)              Tracker (Subscriber)
       │                                │
       │ ① 倉庫に到着                    │
       ├─ "倉庫|0" ───────────────────>│
       │                                ├─ 🚚 倉庫 [░░░...] 0%
       │                                │
       │ (2秒待機)                      │
       │                                │
       │ ② 高速道路に到着                │
       ├─ "高速道路|20" ──────────────>│
       │                                ├─ 🚚 高速道路 [████...] 20%
       │                                │
       │ (以下同様に進行)                │
       │                                │
       │ ⑥ 配達完了                     │
       ├─ "配達完了|100" ─────────────>│
       │                                ├─ 🚚 配達完了 [████████] 100%
       │                                ├─ ✅ 荷物が配達されました！
       │                                └─ (切断)
```

## 技術的なポイント

### 1. データ形式の設計（パイプ区切り）

**ペイロード構造**:
```python
# 形式: "位置|進捗率"
message = f"{location}|{progress}"

# 例:
"倉庫|0"
"高速道路|20"
"配達完了|100"
```

**パース処理**:
```python
def on_message(client, userdata, msg):
    data = msg.payload.decode().split('|')
    location = data[0]    # "高速道路"
    progress = int(data[1])  # 20
```

**この形式の利点**:
- シンプルで軽量
- 簡単にパース可能
- 人間が読みやすい

**代替案（JSON）**:
```python
import json

# JSONフォーマット（より構造化）
data = {
    "location": "高速道路",
    "progress": 20,
    "timestamp": "2024-01-15T10:30:00"
}
message = json.dumps(data)
```

### 2. 進捗率の計算

```python
locations = [
    "倉庫",           # 0/5 = 0%
    "高速道路",       # 1/5 = 20%
    "SA（休憩中）",   # 2/5 = 40%
    "市街地",         # 3/5 = 60%
    "配達先エリア",   # 4/5 = 80%
    "配達完了"        # 5/5 = 100%
]

for i, location in enumerate(locations):
    # インデックスから進捗率を計算
    progress = int((i / (len(locations) - 1)) * 100)
    # i=0: 0%, i=1: 20%, ..., i=5: 100%
```

**計算式の詳細**:
```
progress = (現在位置のインデックス / (総位置数 - 1)) × 100

例: 総位置数が6の場合
  i=0: (0 / 5) × 100 = 0%
  i=1: (1 / 5) × 100 = 20%
  i=5: (5 / 5) × 100 = 100%
```

### 3. プログレスバーの実装

```python
def on_message(client, userdata, msg):
    data = msg.payload.decode().split('|')
    location = data[0]
    progress = int(data[1])

    # プログレスバーを生成
    bar_length = 20
    filled = int(bar_length * progress / 100)  # 塗りつぶし部分
    bar = "█" * filled + "░" * (bar_length - filled)  # バーを構築

    # \r で行頭に戻り、上書き表示
    print(f"\r🚚 {location:20} [{bar}] {progress}%", end="", flush=True)
```

**キーポイント**:
- `\r`: キャリッジリターン（行頭に戻る）
- `end=""`: 改行を抑制
- `flush=True`: 即座にバッファをフラッシュ
- `{location:20}`: 20文字幅で左詰め（位置を揃える）

**文字の選択**:
```python
# Unicode文字でビジュアル表現
"█"  # U+2588: 完全ブロック（塗りつぶし）
"░"  # U+2591: 薄いブロック（未完了）

# 代替文字
"■" + "□"  # 黒四角 + 白四角
"#" + "-"  # ASCII文字のみ
```

### 4. リアルタイム更新と上書き表示

**通常の表示（改行あり）**:
```python
print("Line 1")
print("Line 2")
print("Line 3")

# 出力:
# Line 1
# Line 2
# Line 3
```

**上書き表示（改行なし）**:
```python
print("\rLine 1", end="", flush=True)
time.sleep(1)
print("\rLine 2", end="", flush=True)
time.sleep(1)
print("\rLine 3", end="", flush=True)

# 出力（同じ行に上書き）:
# Line 3  ← 最終的にこれだけ表示
```

### 5. 完了検知と自動切断

```python
def on_message(client, userdata, msg):
    # ... プログレスバー表示 ...

    if progress == 100:
        print("\n✅ 荷物が配達されました！")
        client.disconnect()  # 自動的に切断
```

**利点**:
- 配達完了時に自動終了
- リソースの適切な解放
- ユーザーの手動操作不要

### 6. トピック設計（車両ID含む）

```
delivery/                    ← サービスカテゴリ
  └─ van01/                 ← 車両ID
      └─ location           ← データタイプ
```

**拡張例（複数車両）**:
```
delivery/
  ├─ van01/location
  ├─ van02/location
  └─ van03/location

# 全車両を追跡
client.subscribe("delivery/#")

# 特定車両のみ追跡
client.subscribe("delivery/van01/#")
```

## 設計・実装のポイント

### アーキテクチャ上の工夫

1. **シンプルな一方向通信**
   - Vehicle → Tracker の単純なフロー
   - 応答不要で低遅延
   - ネットワーク負荷が小さい

2. **時系列データの表現**
   ```python
   # 状態遷移を順次送信
   for location in locations:
       send_update(location, progress)
       time.sleep(2)  # 次の更新まで待機
   ```

3. **視覚的フィードバック**
   - プログレスバーで直感的に理解
   - 絵文字でユーザー体験向上
   - リアルタイム更新で臨場感

### 実際の物流システムとの対応

| このサンプル | 実際のシステム | 説明 |
|------------|---------------|------|
| locations配列 | GPSデータ | 実際は緯度経度 |
| 2秒間隔 | リアルタイム | 実際は数秒〜数分間隔 |
| delivery_vehicle.py | 車載デバイス | GPS + LTE/4G |
| delivery_tracker.py | 配送管理アプリ | Web/モバイルアプリ |

### 拡張可能な設計

**1. GPS座標の使用**:
```python
import json

location_data = {
    "lat": 35.6812,
    "lon": 139.7671,
    "address": "東京都渋谷区",
    "progress": 60
}
client.publish("delivery/van01/location", json.dumps(location_data))
```

**2. 複数車両の管理**:
```python
# トラッカー側で車両IDごとに表示
vehicles = {}

def on_message(client, userdata, msg):
    vehicle_id = msg.topic.split('/')[1]  # "van01"
    vehicles[vehicle_id] = parse_location(msg.payload)
    display_all_vehicles(vehicles)
```

**3. 追加情報の送信**:
```python
data = {
    "location": "高速道路",
    "progress": 20,
    "speed": 80,        # 速度 (km/h)
    "eta": "11:30",     # 到着予定時刻
    "driver": "田中"    # ドライバー名
}
```

**4. アラート機能**:
```python
# 予定時刻を超過したら通知
if current_time > eta:
    client.publish("delivery/van01/alert", "配達遅延")
```

## 使用方法

### 前提条件

- MQTTブローカー（Mosquitto）が起動していること
- paho-mqttライブラリがインストール済みであること

### 実行手順

1. **ターミナル1でTrackerを起動**:
   ```bash
   cd mqtt_clients/samples/05_delivery_tracking
   python delivery_tracker.py
   ```

   出力:
   ```
   📡 配達トラッカー開始
   ```

2. **ターミナル2でVehicleを起動**:
   ```bash
   cd mqtt_clients/samples/05_delivery_tracking
   python delivery_vehicle.py
   ```

   Vehicle側の出力:
   ```
   🚚 配達車両シミュレータ
   --------------------------------------------------
   📍 現在地: 倉庫 (0%)
   --------------------------------------------------
   📍 現在地: 高速道路 (20%)
   --------------------------------------------------
   ...
   ```

3. **Tracker側でリアルタイム更新を確認**:
   ```
   📡 配達トラッカー開始
   🚚 倉庫                  [░░░░░░░░░░░░░░░░░░░░] 0%
   🚚 高速道路              [████░░░░░░░░░░░░░░░░] 20%
   🚚 SA（休憩中）          [████████░░░░░░░░░░░░] 40%
   🚚 市街地                [████████████░░░░░░░░] 60%
   🚚 配達先エリア          [████████████████░░░░] 80%
   🚚 配達完了              [████████████████████] 100%
   ✅ 荷物が配達されました！
   ```

4. **自動終了**: Tracker側は配達完了時に自動的に終了

### カスタマイズ例

**配達ルートの変更**:
```python
# delivery_vehicle.py を編集
locations = [
    "集荷センター",
    "A地区",
    "B地区",
    "C地区",
    "最終目的地"
]
```

**更新間隔の変更**:
```python
time.sleep(2)  # 2秒 → 5秒に変更
time.sleep(5)
```

## 学習ポイント

### 初級レベル

- ✅ **位置情報の送信**: センサーデータの基本
- ✅ **データ形式**: 構造化データの送信
- ✅ **視覚化**: プログレスバー表示

### 中級レベル

- ✅ **上書き表示**: \r を使ったUI制御
- ✅ **進捗計算**: 位置から進捗率への変換
- ✅ **文字列フォーマット**: 整形表示のテクニック

### 上級レベル

- ✅ **時系列データ**: イベントストリームの処理
- ✅ **自動制御**: 条件による自動切断
- ✅ **スケーラビリティ**: 複数車両への拡張

## 応用アイデア

1. **地図表示**:
   ```python
   # folium や matplotlib で地図上にプロット
   import folium
   map = folium.Map(location=[lat, lon])
   ```

2. **履歴記録**:
   ```python
   # SQLiteに位置履歴を保存
   import sqlite3
   conn.execute("INSERT INTO tracking_history VALUES (?, ?, ?)",
                (timestamp, location, progress))
   ```

3. **複数車両の同時追跡**:
   ```python
   # ダッシュボードで全車両を一覧表示
   vehicles = {
       "van01": {"location": "高速道路", "progress": 20},
       "van02": {"location": "市街地", "progress": 60},
       "van03": {"location": "配達完了", "progress": 100}
   }
   ```

4. **到着予定時刻（ETA）計算**:
   ```python
   # 現在の速度と残り距離からETAを算出
   eta = current_time + (remaining_distance / average_speed)
   ```

5. **アラート通知**:
   ```python
   # 遅延時にメール/プッシュ通知
   if delay > threshold:
       send_notification("配達が遅れています")
   ```

6. **温度監視**:
   ```python
   # 冷蔵・冷凍配送での温度管理
   data = {
       "location": location,
       "progress": progress,
       "temperature": -5.2  # 冷凍温度
   }
   ```

## トラブルシューティング

### よくある問題

1. **プログレスバーが表示されない**:
   - Tracker側が起動しているか確認
   - ブローカーが起動しているか確認
   - トピック名が一致しているか確認

2. **表示が乱れる**:
   - ターミナルのUnicode対応を確認
   - 文字幅（`{location:20}`）を調整

3. **更新が遅い/速い**:
   - `time.sleep(2)` の値を調整
   - ネットワーク遅延を考慮

4. **完了後も終了しない**:
   - progress == 100 の条件を確認
   - データ型（文字列 vs 整数）に注意

## まとめ

このサンプルでは、MQTTを使った位置情報トラッキングシステムの基本を学べます。シンプルながら、実際の物流・配送システムで使われる重要な概念（時系列データ、進捗管理、リアルタイム可視化）が詰まっています。プログレスバーによる視覚的フィードバックは、ユーザー体験を大きく向上させる重要な要素です。
