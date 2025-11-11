# Dockerコマンド クイックリファレンス

## 🚀 このドキュメントについて

MQTTブローカー（Mosquitto）の開発でよく使うDockerコマンドをまとめたリファレンスです。
コピー&ペーストですぐに使えるようになっています。

---

## 📦 コンテナの基本操作

### コンテナの起動

```bash
# 基本的な起動
docker run -d --name mqtt-broker \
  -p 1883:1883 \
  eclipse-mosquitto

# ボリュームマウント付き
docker run -d --name mqtt-broker \
  -p 1883:1883 \
  -v "$(pwd)/mqtt/config:/mosquitto/config" \
  -v "$(pwd)/mqtt/data:/mosquitto/data" \
  -v "$(pwd)/mqtt/log:/mosquitto/log" \
  eclipse-mosquitto

# 停止したコンテナを再起動
docker start mqtt-broker
```

### コンテナの停止

```bash
# 通常の停止（10秒待機してから強制停止）
docker stop mqtt-broker

# 即座に停止
docker kill mqtt-broker
```

### コンテナの再起動

```bash
# 再起動（設定変更後など）
docker restart mqtt-broker

# すべてのコンテナを再起動
docker restart $(docker ps -q)
```

### コンテナの削除

```bash
# コンテナを削除（停止後）
docker stop mqtt-broker
docker rm mqtt-broker

# 強制削除（起動中でも削除）
docker rm -f mqtt-broker

# 停止中のすべてのコンテナを削除
docker container prune

# 確認なしで削除
docker container prune -f
```

---

## 🔍 コンテナの情報確認

### コンテナの一覧表示

```bash
# 起動中のコンテナのみ
docker ps

# すべてのコンテナ（停止中も含む）
docker ps -a

# コンテナIDのみ表示
docker ps -q

# 特定のコンテナを検索
docker ps | grep mqtt
docker ps -a | grep mosquitto
```

### コンテナの詳細情報

```bash
# コンテナの詳細情報（JSON形式）
docker inspect mqtt-broker

# IPアドレスのみ取得
docker inspect mqtt-broker | grep IPAddress

# ポートマッピングを確認
docker port mqtt-broker
```

### リソース使用状況

```bash
# リアルタイムでリソース使用状況を表示
docker stats mqtt-broker

# すべてのコンテナの統計
docker stats

# 1回だけ表示（ストリーミングなし）
docker stats --no-stream mqtt-broker
```

---

## 📋 ログ管理

### ログの表示

```bash
# すべてのログを表示
docker logs mqtt-broker

# 最新100行だけ表示
docker logs --tail 100 mqtt-broker

# リアルタイムでログを追跡（Ctrl+Cで終了）
docker logs -f mqtt-broker

# タイムスタンプ付きで表示
docker logs -t mqtt-broker

# 特定の時刻以降のログ
docker logs --since 2024-01-01T10:00:00 mqtt-broker

# 過去1時間のログ
docker logs --since 1h mqtt-broker
```

### ログのフィルタリング

```bash
# エラーのみ表示
docker logs mqtt-broker 2>&1 | grep -i error

# 特定のキーワードを含む行
docker logs mqtt-broker | grep "connection"

# 除外して表示
docker logs mqtt-broker | grep -v "debug"
```

### ログのエクスポート

```bash
# ログをファイルに保存
docker logs mqtt-broker > mqtt-broker.log

# タイムスタンプ付きで保存
docker logs -t mqtt-broker > mqtt-broker-$(date +%Y%m%d).log
```

---

## 🔧 コンテナ内でのコマンド実行

### インタラクティブシェル

```bash
# シェルに入る（shを使用）
docker exec -it mqtt-broker sh

# bashが使える場合
docker exec -it mqtt-broker bash

# 特定のディレクトリで起動
docker exec -it -w /mosquitto/config mqtt-broker sh
```

### ワンライナーコマンド

```bash
# コンテナ内でコマンド実行
docker exec mqtt-broker mosquitto_sub -t test/topic -C 1

# ファイルの内容を確認
docker exec mqtt-broker cat /mosquitto/config/mosquitto.conf

# プロセスを確認
docker exec mqtt-broker ps aux

# ネットワークを確認
docker exec mqtt-broker netstat -tulpn
```

### ファイル操作

```bash
# コンテナからホストにファイルをコピー
docker cp mqtt-broker:/mosquitto/config/mosquitto.conf ./mosquitto.conf

# ホストからコンテナにファイルをコピー
docker cp ./mosquitto.conf mqtt-broker:/mosquitto/config/mosquitto.conf

# ディレクトリごとコピー
docker cp mqtt-broker:/mosquitto/log ./logs-backup
```

---

## 🖼️ イメージ管理

### イメージの取得

```bash
# 最新版をダウンロード
docker pull eclipse-mosquitto:latest

# 特定のバージョン
docker pull eclipse-mosquitto:2.0.18

# すべてのタグを表示
docker search eclipse-mosquitto
```

### イメージの一覧

```bash
# すべてのイメージ
docker images

# Mosquittoイメージのみ
docker images | grep mosquitto

# イメージサイズ順に表示
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | sort -k3 -h
```

### イメージの削除

```bash
# 特定のイメージを削除
docker rmi eclipse-mosquitto:latest

# 使われていないイメージをすべて削除
docker image prune

# すべての未使用イメージを削除（確認なし）
docker image prune -a -f
```

---

## 💾 ボリューム管理

### Named Volumeの作成

```bash
# Volumeを作成
docker volume create mqtt-config
docker volume create mqtt-data
docker volume create mqtt-logs

# Named Volumeを使用して起動
docker run -d --name mqtt-broker \
  -p 1883:1883 \
  -v mqtt-config:/mosquitto/config \
  -v mqtt-data:/mosquitto/data \
  -v mqtt-logs:/mosquitto/log \
  eclipse-mosquitto
```

### Volumeの確認

```bash
# Volumeの一覧
docker volume ls

# 特定のVolumeの詳細
docker volume inspect mqtt-data

# Volumeの保存場所を確認
docker volume inspect mqtt-data | grep Mountpoint
```

### Volumeのバックアップ

```bash
# Volumeの内容をtarアーカイブに保存
docker run --rm \
  -v mqtt-data:/data \
  -v "$(pwd):/backup" \
  ubuntu tar czf /backup/mqtt-data-backup.tar.gz -C /data .

# バックアップから復元
docker run --rm \
  -v mqtt-data:/data \
  -v "$(pwd):/backup" \
  ubuntu tar xzf /backup/mqtt-data-backup.tar.gz -C /data
```

### Volumeの削除

```bash
# 特定のVolumeを削除
docker volume rm mqtt-data

# 使われていないVolumeをすべて削除
docker volume prune

# 確認なしで削除
docker volume prune -f
```

---

## 🌐 ネットワーク管理

### ネットワークの作成

```bash
# カスタムネットワークを作成
docker network create mqtt-network

# カスタムネットワークでコンテナ起動
docker run -d --name mqtt-broker \
  --network mqtt-network \
  -p 1883:1883 \
  eclipse-mosquitto
```

### ネットワークの確認

```bash
# ネットワークの一覧
docker network ls

# 特定のネットワークの詳細
docker network inspect mqtt-network

# コンテナが接続しているネットワーク
docker inspect mqtt-broker | grep NetworkMode
```

### コンテナをネットワークに接続

```bash
# 既存のコンテナをネットワークに接続
docker network connect mqtt-network mqtt-broker

# ネットワークから切断
docker network disconnect mqtt-network mqtt-broker
```

---

## 🧹 クリーンアップ

### すべての未使用リソースを削除

```bash
# すべての未使用リソース（コンテナ、ネットワーク、イメージ、Volume）を削除
docker system prune

# Volumeも含めてすべて削除
docker system prune --volumes

# 確認なしで削除
docker system prune -a -f --volumes
```

### 特定のリソースを削除

```bash
# 停止中のコンテナを削除
docker container prune -f

# 未使用のイメージを削除
docker image prune -a -f

# 未使用のVolumeを削除
docker volume prune -f

# 未使用のネットワークを削除
docker network prune -f
```

### ディスク使用状況の確認

```bash
# Dockerが使用しているディスク容量
docker system df

# 詳細表示
docker system df -v
```

---

## 🔄 コンテナの環境変数とポート

### 環境変数の設定

```bash
# 環境変数を指定して起動
docker run -d --name mqtt-broker \
  -e TZ=Asia/Tokyo \
  -e MOSQUITTO_USERNAME=admin \
  -p 1883:1883 \
  eclipse-mosquitto

# 環境変数ファイルを使用
echo "TZ=Asia/Tokyo" > .env
docker run -d --name mqtt-broker \
  --env-file .env \
  -p 1883:1883 \
  eclipse-mosquitto
```

### ポートの公開

```bash
# 複数のポートを公開
docker run -d --name mqtt-broker \
  -p 1883:1883 \
  -p 8883:8883 \
  -p 9001:9001 \
  eclipse-mosquitto

# すべてのポートを公開
docker run -d --name mqtt-broker \
  -P \
  eclipse-mosquitto

# 公開されたポートを確認
docker port mqtt-broker
```

---

## 🛠️ トラブルシューティングコマンド

### コンテナが起動しない

```bash
# 起動を試みてログを確認
docker run --name mqtt-broker -p 1883:1883 eclipse-mosquitto
# エラーを確認

# または
docker run -d --name mqtt-broker -p 1883:1883 eclipse-mosquitto
docker logs mqtt-broker
```

### 設定ファイルの検証

```bash
# コンテナを起動せずに設定ファイルを検証
docker run --rm \
  -v "$(pwd)/mqtt/config:/mosquitto/config" \
  eclipse-mosquitto \
  mosquitto -c /mosquitto/config/mosquitto.conf -v
```

### ネットワーク接続のテスト

```bash
# コンテナ内からlocalhostに接続
docker exec mqtt-broker mosquitto_sub -h localhost -t test/topic -v

# 別のコンテナからの接続テスト
docker run -it --rm eclipse-mosquitto mosquitto_sub -h <mqtt-broker-ip> -t test/topic
```

### リソース制限

```bash
# メモリとCPUを制限して起動
docker run -d --name mqtt-broker \
  -p 1883:1883 \
  --memory="512m" \
  --cpus="1.0" \
  eclipse-mosquitto

# 制限を確認
docker stats mqtt-broker
```

---

## 📝 便利なエイリアス

以下を `.bashrc` または `.bash_profile` に追加すると便利です：

```bash
# Docker関連のエイリアス
alias dps='docker ps'
alias dpsa='docker ps -a'
alias di='docker images'
alias dl='docker logs'
alias dlf='docker logs -f'
alias dex='docker exec -it'
alias drm='docker rm -f'
alias dprune='docker system prune -a -f --volumes'

# MQTT関連のエイリアス
alias mqtt-start='docker start mqtt-broker'
alias mqtt-stop='docker stop mqtt-broker'
alias mqtt-restart='docker restart mqtt-broker'
alias mqtt-logs='docker logs -f mqtt-broker'
alias mqtt-shell='docker exec -it mqtt-broker sh'
alias mqtt-sub='docker exec mqtt-broker mosquitto_sub -h localhost'
alias mqtt-pub='docker exec mqtt-broker mosquitto_pub -h localhost'
```

**使用例**:
```bash
# 起動
mqtt-start

# ログ確認
mqtt-logs

# シェルに入る
mqtt-shell

# メッセージを購読
mqtt-sub -t test/topic
```

---

## 🎯 シナリオ別コマンド集

### シナリオ1: 開発環境のセットアップ

```bash
# 1. ディレクトリ作成
mkdir -p mqtt/{config,data,log}

# 2. 設定ファイル作成
cat > mqtt/config/mosquitto.conf << 'EOF'
listener 1883
allow_anonymous true
persistence true
persistence_location /mosquitto/data/
log_dest stdout
log_type all
EOF

# 3. イメージ取得
docker pull eclipse-mosquitto:latest

# 4. コンテナ起動
docker run -d --name mqtt-broker \
  -p 1883:1883 \
  -v "$(pwd)/mqtt/config:/mosquitto/config" \
  -v "$(pwd)/mqtt/data:/mosquitto/data" \
  -v "$(pwd)/mqtt/log:/mosquitto/log" \
  eclipse-mosquitto

# 5. 動作確認
docker logs mqtt-broker
docker exec mqtt-broker mosquitto_sub -t test/topic -C 1 &
docker exec mqtt-broker mosquitto_pub -t test/topic -m "Hello MQTT"
```

### シナリオ2: 設定変更とリロード

```bash
# 1. 設定ファイルを編集
nano mqtt/config/mosquitto.conf

# 2. 設定を検証
docker run --rm \
  -v "$(pwd)/mqtt/config:/mosquitto/config" \
  eclipse-mosquitto \
  mosquitto -c /mosquitto/config/mosquitto.conf -v

# 3. コンテナを再起動
docker restart mqtt-broker

# 4. ログで確認
docker logs --tail 50 mqtt-broker
```

### シナリオ3: データのバックアップと移行

```bash
# 1. コンテナを停止
docker stop mqtt-broker

# 2. データをバックアップ
tar czf mqtt-backup-$(date +%Y%m%d).tar.gz mqtt/

# 3. 新しい環境に移行
scp mqtt-backup-20240115.tar.gz user@new-server:~/
ssh user@new-server
tar xzf mqtt-backup-20240115.tar.gz

# 4. 新しいサーバーでコンテナ起動
docker run -d --name mqtt-broker \
  -p 1883:1883 \
  -v "$(pwd)/mqtt/config:/mosquitto/config" \
  -v "$(pwd)/mqtt/data:/mosquitto/data" \
  -v "$(pwd)/mqtt/log:/mosquitto/log" \
  eclipse-mosquitto
```

### シナリオ4: パフォーマンス調査

```bash
# 1. リソース使用状況を確認
docker stats mqtt-broker

# 2. コンテナ内のプロセスを確認
docker exec mqtt-broker ps aux

# 3. ネットワーク接続を確認
docker exec mqtt-broker netstat -an | grep 1883

# 4. ログで接続数を確認
docker logs mqtt-broker | grep "New connection" | wc -l

# 5. 詳細情報を取得
docker inspect mqtt-broker > mqtt-broker-inspect.json
```

---

## 📚 参考資料

- [Docker公式ドキュメント](https://docs.docker.com/)
- [Docker CLIリファレンス](https://docs.docker.com/engine/reference/commandline/cli/)
- [Eclipse Mosquitto Dockerイメージ](https://hub.docker.com/_/eclipse-mosquitto)

---

**前の章**: [第2章メインドキュメント](./01_Dockerブローカー構築.md)
