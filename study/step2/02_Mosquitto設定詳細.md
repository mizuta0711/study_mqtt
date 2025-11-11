# Mosquitto設定ファイル完全ガイド

## 📖 このドキュメントについて

このドキュメントでは、`mosquitto.conf`の設定項目を詳しく解説します。
基本設定から応用的な設定まで、実例とともに説明します。

---

## 🔧 基本構造

mosquitto.confは、以下のセクションで構成されます：

```conf
# コメント行（#で始まる）

# 一般設定
設定項目名 値

# リスナー設定
listener ポート番号
protocol プロトコル名

# セキュリティ設定
allow_anonymous true/false
password_file ファイルパス

# 永続化設定
persistence true/false
persistence_location ディレクトリパス

# ログ設定
log_dest 出力先
log_type ログタイプ
```

---

## 🎧 リスナー設定

### listener（リスニングポート）

**構文**: `listener [ポート番号] [バインドアドレス]`

**説明**: MQTTクライアントからの接続を待ち受けるポートとアドレスを指定します。

**例**:
```conf
# すべてのインターフェースでポート1883をリッスン
listener 1883

# ローカルホストのみでリッスン
listener 1883 127.0.0.1

# 複数のリスナーを設定
listener 1883        # MQTT
listener 8883        # MQTT over TLS
listener 9001        # WebSocket
```

### protocol（プロトコル）

**構文**: `protocol [mqtt|websockets]`

**説明**: リスナーで使用するプロトコルを指定します。

**例**:
```conf
listener 1883
protocol mqtt

listener 9001
protocol websockets
```

**使い分け**:
- `mqtt`: 通常のMQTTクライアント用
- `websockets`: Webブラウザからの接続用

---

## 🔐 セキュリティ設定

### allow_anonymous（匿名アクセス）

**構文**: `allow_anonymous [true|false]`

**説明**: 認証なしでの接続を許可するかどうか。

```conf
# 学習用：認証なしで接続可能
allow_anonymous true

# 本番用：認証必須
allow_anonymous false
```

⚠️ **セキュリティ警告**: 本番環境では必ず `false` に設定してください。

### password_file（パスワードファイル）

**構文**: `password_file [ファイルパス]`

**説明**: ユーザー名とパスワードを記録したファイルのパス。

**設定例**:
```conf
allow_anonymous false
password_file /mosquitto/config/passwd
```

**パスワードファイルの作成**:
```bash
# コンテナ内で実行
mosquitto_passwd -c /mosquitto/config/passwd username1

# 既存ファイルにユーザー追加
mosquitto_passwd /mosquitto/config/passwd username2
```

**パスワードファイルの形式**:
```
username1:$6$encrypted_password_hash
username2:$6$encrypted_password_hash
```

### acl_file（アクセス制御リスト）

**構文**: `acl_file [ファイルパス]`

**説明**: トピックごとのアクセス権限を定義したファイル。

**設定例**:
```conf
acl_file /mosquitto/config/acl.conf
```

**ACLファイルの例** (`acl.conf`):
```conf
# ユーザー "sensor" はsensor/配下に発行のみ可能
user sensor
topic write sensor/#

# ユーザー "dashboard" はsensor/配下を購読のみ可能
user dashboard
topic read sensor/#

# ユーザー "admin" はすべて可能
user admin
topic readwrite #
```

**アクセス権限の種類**:
- `read`: 購読のみ（Subscribe）
- `write`: 発行のみ（Publish）
- `readwrite`: 購読と発行の両方

---

## 💾 永続化設定

### persistence（永続化の有効化）

**構文**: `persistence [true|false]`

**説明**: Retainメッセージや購読情報をディスクに保存するか。

```conf
# 永続化を有効にする（推奨）
persistence true

# 永続化を無効にする（テスト用）
persistence false
```

**永続化されるデータ**:
- Retainフラグ付きメッセージ
- QoS 1/2のメッセージキュー
- クライアントの購読情報

### persistence_location（保存場所）

**構文**: `persistence_location [ディレクトリパス]`

**説明**: 永続化データを保存するディレクトリ。

```conf
persistence true
persistence_location /mosquitto/data/
```

### autosave_interval（自動保存間隔）

**構文**: `autosave_interval [秒数]`

**説明**: メモリ上のデータをディスクに書き込む間隔（秒）。

```conf
# 5分ごとに保存
autosave_interval 300

# 自動保存を無効化（シャットダウン時のみ保存）
autosave_interval 0
```

### persistence_file（永続化ファイル名）

**構文**: `persistence_file [ファイル名]`

**説明**: 永続化データを保存するファイル名。

```conf
persistence_file mosquitto.db
```

---

## 📋 ログ設定

### log_dest（ログ出力先）

**構文**: `log_dest [stdout|stderr|file ファイルパス|syslog|topic]`

**説明**: ログの出力先を指定。複数指定可能。

**例**:
```conf
# 標準出力に表示
log_dest stdout

# ファイルに保存
log_dest file /mosquitto/log/mosquitto.log

# 複数指定
log_dest stdout
log_dest file /mosquitto/log/mosquitto.log
log_dest topic $SYS/broker/log
```

**出力先の種類**:
- `stdout`: 標準出力（docker logsで確認可能）
- `file`: ファイルに保存
- `syslog`: システムログ
- `topic`: MQTTトピックに発行

### log_type（ログの種類）

**構文**: `log_type [all|error|warning|notice|information|debug|subscribe|unsubscribe]`

**説明**: 記録するログの種類。複数指定可能。

**例**:
```conf
# すべてのログを記録
log_type all

# エラーと警告のみ
log_type error
log_type warning

# 接続情報も記録
log_type error
log_type warning
log_type notice
log_type information
```

**ログタイプの説明**:
| タイプ | 説明 | 用途 |
|:---|:---|:---|
| `error` | エラーメッセージ | 本番環境で必須 |
| `warning` | 警告メッセージ | 潜在的な問題の検出 |
| `notice` | 重要な通知 | クライアントの接続/切断 |
| `information` | 一般情報 | 動作状況の把握 |
| `debug` | デバッグ情報 | 開発時のトラブルシューティング |
| `subscribe` | 購読イベント | トピックの購読状況を監視 |
| `unsubscribe` | 購読解除イベント | 購読解除の監視 |
| `all` | すべて | 学習・開発環境 |

### log_timestamp（タイムスタンプ形式）

**構文**: `log_timestamp [true|false]`

**説明**: ログにタイムスタンプを含めるか。

```conf
log_timestamp true
```

**出力例**:
```
1705305600: New connection from 172.17.0.1 on port 1883.
```

---

## 🔌 接続設定

### max_connections（最大接続数）

**構文**: `max_connections [数値]`

**説明**: 同時接続可能なクライアント数。-1で無制限。

```conf
# 無制限（デフォルト）
max_connections -1

# 最大100接続
max_connections 100
```

### max_queued_messages（最大キューメッセージ数）

**構文**: `max_queued_messages [数値]`

**説明**: クライアントごとのキューイング可能なQoS 1/2メッセージ数。

```conf
# デフォルトは1000
max_queued_messages 1000

# リソースが限られている場合
max_queued_messages 100
```

### keepalive_interval（キープアライブ間隔）

**構文**: `keepalive_interval [秒数]`

**説明**: クライアントとの接続維持確認の間隔。

```conf
# デフォルトは60秒
keepalive_interval 60
```

---

## 🌐 WebSocket設定

### WebSocketリスナーの設定

```conf
# WebSocket（非暗号化）
listener 9001
protocol websockets

# WebSocket over TLS（暗号化）
listener 9002
protocol websockets
certfile /mosquitto/certs/server.crt
keyfile /mosquitto/certs/server.key
```

**Webアプリケーションからの接続例**:
```javascript
const client = mqtt.connect('ws://localhost:9001');
```

---

## 🔒 TLS/SSL設定

### 基本的なTLS設定

```conf
listener 8883
protocol mqtt

# サーバー証明書
certfile /mosquitto/certs/server.crt
keyfile /mosquitto/certs/server.key

# CA証明書
cafile /mosquitto/certs/ca.crt

# クライアント証明書認証を要求
require_certificate true
```

### 自己署名証明書の作成例

```bash
# CA証明書の作成
openssl req -new -x509 -days 365 -extensions v3_ca \
  -keyout ca.key -out ca.crt

# サーバー証明書の作成
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out server.crt -days 365
```

---

## 🎛️ パフォーマンス設定

### sys_interval（$SYSトピック更新間隔）

**構文**: `sys_interval [秒数]`

**説明**: `$SYS/`配下のシステム情報トピックの更新間隔。

```conf
# デフォルトは10秒
sys_interval 10

# 無効化
sys_interval 0
```

### memory_limit（メモリ制限）

**構文**: `memory_limit [バイト数]`

**説明**: Mosquittoが使用可能なメモリの上限。

```conf
# 100MBに制限
memory_limit 104857600
```

---

## 📝 実践的な設定例

### 学習用設定（現在の設定）

```conf
listener 1883
protocol mqtt
allow_anonymous true
persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
log_dest stdout
log_type all
max_connections -1
```

### 開発環境用設定

```conf
# 基本リスナー
listener 1883
protocol mqtt

# WebSocket対応
listener 9001
protocol websockets

# 認証設定
allow_anonymous false
password_file /mosquitto/config/passwd

# 永続化
persistence true
persistence_location /mosquitto/data/
autosave_interval 300

# ログ設定
log_dest file /mosquitto/log/mosquitto.log
log_dest stdout
log_type error
log_type warning
log_type notice
log_timestamp true

# 接続設定
max_connections 1000
max_queued_messages 500
```

### 本番環境用設定

```conf
# TLS/SSLリスナー
listener 8883
protocol mqtt
certfile /mosquitto/certs/server.crt
keyfile /mosquitto/certs/server.key
cafile /mosquitto/certs/ca.crt
require_certificate true

# WebSocket over TLS
listener 9002
protocol websockets
certfile /mosquitto/certs/server.crt
keyfile /mosquitto/certs/server.key

# セキュリティ
allow_anonymous false
password_file /mosquitto/config/passwd
acl_file /mosquitto/config/acl.conf

# 永続化
persistence true
persistence_location /mosquitto/data/
autosave_interval 600

# ログ（エラーのみ）
log_dest file /mosquitto/log/mosquitto.log
log_type error
log_type warning
log_timestamp true

# リソース制限
max_connections 10000
max_queued_messages 1000
memory_limit 524288000  # 500MB
```

---

## 🔍 設定の検証

### 設定ファイルの文法チェック

```bash
# コンテナ内で実行
mosquitto -c /mosquitto/config/mosquitto.conf -v
```

**正常な場合**:
```
1705305600: mosquitto version 2.0.18 starting
1705305600: Config loaded from /mosquitto/config/mosquitto.conf.
```

**エラーがある場合**:
```
Error: Unknown configuration variable "invalid_option".
```

### 設定変更後の反映

```bash
# コンテナを再起動
docker restart mqtt-broker

# ログで確認
docker logs mqtt-broker
```

---

## 📚 参考資料

- [mosquitto.conf公式ドキュメント](https://mosquitto.org/man/mosquitto-conf-5.html)
- [Mosquittoセキュリティ設定ガイド](https://mosquitto.org/documentation/authentication-methods/)

---

**前の章**: [第2章メインドキュメント](./01_Dockerブローカー構築.md)
