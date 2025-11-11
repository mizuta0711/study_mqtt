# Docker Compose 使い方ガイド

## 📖 このドキュメントについて

docker-compose.ymlを使うと、長いDockerコマンドを入力せずに、簡単なコマンドでMQTT Brokerを起動・停止できます。

---

## 🎯 docker-compose.ymlとは

**docker-compose.yml**は、複数のDockerコンテナを定義・管理するための設定ファイルです。

### メリット

✅ **コマンドが簡単**
- `docker-compose up -d` で起動
- `docker-compose down` で停止

✅ **設定を一元管理**
- ポート、ボリューム、ネットワークをファイルで管理
- チーム開発で共有しやすい

✅ **再現性が高い**
- 誰でも同じ環境を構築できる

---

## 📁 docker-compose.ymlの内容

プロジェクトルートに作成した`docker-compose.yml`の内容：

```yaml
version: '3.8'

services:
  mqtt-broker:
    image: eclipse-mosquitto:latest
    container_name: mqtt-broker
    ports:
      - "1883:1883"      # MQTT
      - "9001:9001"      # WebSocket (将来使う場合のため)
    volumes:
      - ./mqtt/config:/mosquitto/config
      - ./mqtt/data:/mosquitto/data
      - ./mqtt/log:/mosquitto/log
    restart: unless-stopped
    networks:
      - mqtt-network

networks:
  mqtt-network:
    driver: bridge
```

### 設定の説明

| 項目 | 説明 |
|:---|:---|
| `version: '3.8'` | Docker Composeのバージョン |
| `services:` | 起動するコンテナの定義 |
| `mqtt-broker:` | サービス名（任意の名前） |
| `image:` | 使用するDockerイメージ |
| `container_name:` | コンテナ名 |
| `ports:` | ポートマッピング（ホスト:コンテナ） |
| `volumes:` | ボリュームマウント |
| `restart: unless-stopped` | コンテナが停止したら自動再起動 |
| `networks:` | 使用するネットワーク |

---

## 🚀 基本的な使い方

### 前提条件

```bash
# プロジェクトルートにいることを確認
pwd
# 出力: /d/Develop/python/StudyMQTT (Git Bash)
# または: D:\Develop\python\StudyMQTT (PowerShell)
```

### 1. コンテナを起動

```bash
docker-compose up -d
```

**オプション説明**:
- `-d`: デタッチモード（バックグラウンド実行）

**出力例**:
```
Creating network "studymqtt_mqtt-network" with driver "bridge"
Creating mqtt-broker ... done
```

### 2. 起動確認

```bash
docker-compose ps
```

**出力例**:
```
    Name                 Command             State                    Ports
------------------------------------------------------------------------------------------
mqtt-broker   /docker-entrypoint.sh /usr ...   Up      0.0.0.0:1883->1883/tcp,
                                                        0.0.0.0:9001->9001/tcp
```

### 3. ログを確認

```bash
# すべてのログを表示
docker-compose logs

# リアルタイムでログを追跡
docker-compose logs -f

# 最新50行だけ表示
docker-compose logs --tail 50

# 特定のサービスのログ
docker-compose logs mqtt-broker
```

### 4. コンテナを停止

```bash
docker-compose stop
```

コンテナは停止しますが、削除されません。データは保持されます。

### 5. コンテナを停止＋削除

```bash
docker-compose down
```

**注意**: ボリュームマウントしているので、データ（mqtt/config、mqtt/data、mqtt/log）は削除されません。

### 6. コンテナを再起動

```bash
docker-compose restart
```

設定ファイルを変更した後などに使います。

---

## 🔧 よく使うコマンド

### コンテナの状態確認

```bash
# docker-composeで管理しているコンテナの状態
docker-compose ps

# 詳細情報
docker-compose ps -a
```

### コンテナ内でコマンド実行

```bash
# シェルに入る
docker-compose exec mqtt-broker sh

# ワンライナーコマンド
docker-compose exec mqtt-broker mosquitto_sub -t test/topic -C 1
```

### ログ管理

```bash
# すべてのログ
docker-compose logs

# リアルタイム
docker-compose logs -f

# タイムスタンプ付き
docker-compose logs -t

# 特定の時刻以降
docker-compose logs --since 2024-01-15T10:00:00
```

### イメージの更新

```bash
# 最新イメージを取得
docker-compose pull

# 取得したイメージでコンテナを再作成
docker-compose up -d
```

### 完全クリーンアップ

```bash
# コンテナ、ネットワーク、ボリューム（匿名）をすべて削除
docker-compose down -v

# イメージも削除
docker-compose down --rmi all
```

---

## 📊 従来のコマンドとの比較

### 起動

| 従来のコマンド（PowerShell） | Docker Compose |
|:---|:---|
| `docker run -d --name mqtt-broker -p 1883:1883 -v "${PWD}\mqtt\config:/mosquitto/config" -v "${PWD}\mqtt\data:/mosquitto/data" -v "${PWD}\mqtt\log:/mosquitto/log" eclipse-mosquitto` | `docker-compose up -d` |

### 停止

| 従来のコマンド | Docker Compose |
|:---|:---|
| `docker stop mqtt-broker` | `docker-compose stop` |

### 削除

| 従来のコマンド | Docker Compose |
|:---|:---|
| `docker rm -f mqtt-broker` | `docker-compose down` |

### ログ確認

| 従来のコマンド | Docker Compose |
|:---|:---|
| `docker logs -f mqtt-broker` | `docker-compose logs -f` |

---

## 🛠️ 応用的な使い方

### 環境変数を使う

`.env`ファイルを作成すると、環境変数を設定できます。

**.envファイル**:
```env
MQTT_PORT=1883
WEBSOCKET_PORT=9001
TZ=Asia/Tokyo
```

**docker-compose.yml**:
```yaml
services:
  mqtt-broker:
    image: eclipse-mosquitto:latest
    container_name: mqtt-broker
    ports:
      - "${MQTT_PORT}:1883"
      - "${WEBSOCKET_PORT}:9001"
    environment:
      - TZ=${TZ}
    volumes:
      - ./mqtt/config:/mosquitto/config
      - ./mqtt/data:/mosquitto/data
      - ./mqtt/log:/mosquitto/log
```

### 複数のサービスを追加

将来的にMQTTクライアントやデータベースを追加する場合：

```yaml
version: '3.8'

services:
  mqtt-broker:
    image: eclipse-mosquitto:latest
    container_name: mqtt-broker
    ports:
      - "1883:1883"
    volumes:
      - ./mqtt/config:/mosquitto/config
      - ./mqtt/data:/mosquitto/data
      - ./mqtt/log:/mosquitto/log
    networks:
      - mqtt-network

  # 将来的に追加するサービスの例
  # mqtt-client:
  #   build: ./client
  #   depends_on:
  #     - mqtt-broker
  #   networks:
  #     - mqtt-network

networks:
  mqtt-network:
    driver: bridge
```

---

## 🔍 トラブルシューティング

### エラー: "Cannot start service mqtt-broker: driver failed"

**原因**: ポートが既に使用されている

**解決方法**:
```bash
# 既存のコンテナを確認
docker ps -a

# 既存のコンテナを削除
docker rm -f mqtt-broker

# 再度起動
docker-compose up -d
```

### エラー: "yaml: line X: mapping values are not allowed in this context"

**原因**: docker-compose.ymlの文法エラー

**解決方法**:
- インデント（スペース2個）を確認
- タブではなくスペースを使用
- オンラインYAMLバリデーターでチェック

### コンテナが起動してもすぐ停止する

**確認方法**:
```bash
# ログを確認
docker-compose logs

# 設定ファイルの検証
docker-compose config
```

### ボリュームのパーミッション問題

```bash
# ディレクトリのパーミッションを確認
ls -la mqtt/

# パーミッションを変更
chmod -R 755 mqtt/
```

---

## 📝 ベストプラクティス

### 1. docker-compose.ymlをバージョン管理に含める

```bash
git add docker-compose.yml
git commit -m "Add docker-compose configuration"
```

### 2. .envファイルは含めない

**`.gitignore`に追加**:
```
.env
```

### 3. ドキュメントを作成

`README.md`にdocker-composeの使い方を記載する。

### 4. 定期的にイメージを更新

```bash
# 月に1回程度
docker-compose pull
docker-compose up -d
```

---

## 🎯 まとめ

### docker-compose.ymlを使うメリット

✅ **簡単**: `docker-compose up -d` だけで起動
✅ **再現可能**: 誰でも同じ環境を構築できる
✅ **管理しやすい**: 設定を一元管理
✅ **チーム開発**: 設定を共有しやすい

### 基本コマンド

| 操作 | コマンド |
|:---|:---|
| 起動 | `docker-compose up -d` |
| 停止 | `docker-compose stop` |
| 削除 | `docker-compose down` |
| 再起動 | `docker-compose restart` |
| ログ | `docker-compose logs -f` |
| 状態確認 | `docker-compose ps` |

---

## 📚 参考資料

- [Docker Compose公式ドキュメント](https://docs.docker.com/compose/)
- [Compose File Reference](https://docs.docker.com/compose/compose-file/)
- [Docker Composeベストプラクティス](https://docs.docker.com/develop/dev-best-practices/)

---

**次のステップ**: docker-compose.ymlを使ってMQTT Brokerを起動してみましょう！
