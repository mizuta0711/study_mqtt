# 応用例2：高度なダッシュボード

## 📊 概要

複数グラフを同時表示し、統計情報や閾値ライン、データ保存機能を備えた高機能ダッシュボードです。

## 🎯 学習目標

- matplotlibによる複雑なレイアウトの作成
- リアルタイムでの統計情報計算と表示
- データの自動保存機能の実装
- センサーステータスの視覚的な監視

## 📁 ファイル構成

```
02_advanced_dashboard/
├── README.md                # このファイル
└── advanced_dashboard.py    # 高度なダッシュボード
```

## 🚀 実行方法

### 1. 前提条件

センサーPublisherが起動していること（サンプル01を参照）

```bash
# センサーを起動
python mqtt_clients/step5/advance/01_multi_sensor_system/multi_sensor_publisher.py
```

### 2. ダッシュボードの起動

```bash
python mqtt_clients/step5/advance/02_advanced_dashboard/advanced_dashboard.py
```

## ✨ 主な機能

### 基本機能
- ✅ **3つのグラフ同時表示**: 温度、湿度、照度をリアルタイム表示
- ✅ **統計情報表示**: 平均値、最大値、最小値、範囲を計算して表示
- ✅ **閾値ライン表示**: 警告レベルを視覚的に確認
- ✅ **センサーステータス監視**: タイトルバーにステータス表示

### 高度な機能
- ✅ **データの自動保存**: 受信したデータをCSVファイルに保存
- ✅ **グラフの自動スケール調整**: データ量に応じてX軸を調整
- ✅ **色分けされた閾値**: 警告レベルを色で識別
- ✅ **タイムスタンプ記録**: 各データに受信時刻を記録

## 📊 グラフの構成

### 温度グラフ (上段)
- **色**: 赤色
- **Y軸範囲**: 15°C〜35°C
- **警告ライン**:
  - 高温警告: 30°C (赤色破線)
  - 低温警告: 18°C (青色破線)

### 湿度グラフ (中段)
- **色**: 青色
- **Y軸範囲**: 20%〜80%
- **警告ライン**:
  - 高湿度警告: 70% (赤色破線)
  - 低湿度警告: 30% (青色破線)

### 照度グラフ (下段)
- **色**: 緑色
- **Y軸範囲**: 0〜1000 lux
- **警告ライン**: なし

## 💾 データ保存機能

### 保存形式: CSV

```csv
timestamp,sensor_id,temperature,humidity,light
2025-11-11 15:30:45,MultiSensor01,25.3,52.1,480
2025-11-11 15:30:46,MultiSensor01,25.5,51.8,475
```

### 保存場所
- **ファイル名**: `sensor_data_YYYYMMDD_HHMMSS.csv`
- **保存先**: 実行ディレクトリ

### 保存タイミング
- プログラム終了時に自動保存
- Ctrl+Cで停止した場合も保存される

## 📊 統計情報の計算

### 表示される統計
- **最新値**: 最後に受信したデータ
- **平均値**: データの平均
- **最小値**: データの最小値
- **最大値**: データの最大値
- **範囲**: 最大値 - 最小値

### 計算コード
```python
def get_stats(data):
    if len(data) == 0:
        return "N/A", "N/A", "N/A", "N/A"

    latest = data[-1]
    avg = sum(data) / len(data)
    min_val = min(data)
    max_val = max(data)

    return latest, avg, min_val, max_val
```

## 🎨 グラフのカスタマイズ

### グラフサイズの変更
```python
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
# figsize=(幅, 高さ) をインチで指定
```

### 色の変更
```python
# 温度グラフの色を青に変更
line1, = ax1.plot([], [], 'b-', linewidth=2)
```

### 閾値の変更
```python
# 高温警告を28°Cに変更
ax1.axhline(y=28, color='r', linestyle='--', alpha=0.5)
```

## 💡 実装のポイント

### 1. リアルタイムアニメーション
```python
ani = animation.FuncAnimation(
    fig, update_plot, init_func=init_plot,
    interval=1000,  # 1秒ごとに更新
    blit=True,
    cache_frame_data=False
)
```

### 2. データのバッファリング
```python
# 最大50個のデータを保持
temp_data = deque(maxlen=50)
humid_data = deque(maxlen=50)
light_data = deque(maxlen=50)
```

### 3. グリッド表示
```python
ax1.grid(True, alpha=0.3)  # 透明度30%のグリッド
```

## 📈 期待される動作

1. ダッシュボードが起動し、ブローカーに接続
2. 3つのグラフが表示される
3. センサーデータが届くとリアルタイムでグラフが更新
4. タイトルバーに統計情報が表示される
5. データが自動的にバッファリングされる
6. プログラム終了時にCSVファイルに保存

## 🔧 トラブルシューティング

### グラフが表示されない
```bash
# matplotlibが正しくインストールされているか確認
pip show matplotlib
```

### データが受信されない
```bash
# センサーPublisherが起動しているか確認
# ブローカーが起動しているか確認
docker ps
```

### CSVファイルが保存されない
- プログラムを正常終了（Ctrl+C）していることを確認
- 実行ディレクトリへの書き込み権限を確認

## 🔄 カスタマイズ例

### グラフの追加
```python
# 4つのグラフに変更
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 12))

# 気圧グラフを追加
line4, = ax4.plot([], [], 'm-', linewidth=2)
ax4.set_ylabel('気圧 (hPa)', fontsize=10)
```

### グラフタイプの変更
```python
# 棒グラフに変更
ax1.bar(range(len(temp_data)), list(temp_data), color='r')
```

## 🎓 学習ポイント

1. **matplotlibの高度な使用**: サブプロット、アニメーション、カスタマイズ
2. **統計情報の計算**: リアルタイムでのデータ分析
3. **データの永続化**: CSVファイルへのエクスポート
4. **ユーザーインターフェース**: 情報を効果的に表示する方法

## 🔗 関連ドキュメント

- [../../study/step5/03_データ可視化詳細.md](../../../../study/step5/03_データ可視化詳細.md)
- [../../study/step5/05_応用コード集.md](../../../../study/step5/05_応用コード集.md)
