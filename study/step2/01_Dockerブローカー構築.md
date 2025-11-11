# 第2章：DockerでMQTT Brokerを構築

## 🎯 この章で学ぶこと（学習時間：1.5時間）

- Eclipse MosquittoをDockerで起動する方法
- Mosquittoの設定ファイル（mosquitto.conf）の書き方
- ボリュームマウントによるデータ永続化
- ブローカーの動作確認とテスト
- Dockerコンテナの基本的な操作

---

## 📋 前提条件

この章を始める前に、以下が準備されていることを確認してください：

- ✅ Docker Desktopがインストールされている
- ✅ Docker Desktopが起動している
- ✅ 第1章のMQTT基礎知識を理解している
- ✅ コマンドライン（Git Bash/PowerShell）が使える

### Docker Desktopの確認

```bash
# Dockerのバージョン確認
docker --version
# 出力例: Docker version 24.0.7, build afdd53b

# Dockerが動作しているか確認
docker ps
# エラーが出なければOK
```

---

## 🦟 Eclipse Mosquittoとは

**Eclipse Mosquitto**は、オープンソースのMQTTブローカー実装です。

### 特徴
- ✅ **軽量**: 組み込みデバイスから大規模サーバーまで対応
- ✅ **高速**: 数万クライアントの同時接続に対応
- ✅ **標準準拠**: MQTT 3.1、3.1.1、5.0をサポート
- ✅ **豊富な機能**: 認証、TLS/SSL、WebSocket対応
- ✅ **無料**: EPL/EDL ライセンス

### なぜDockerを使うのか
- 環境構築が簡単（1コマンドで起動）
- クリーンな環境（ホストOSを汚さない）
- 複数バージョンの管理が容易
- 本番環境との互換性が高い

---

## 🚀 ステップ1：プロジェクト構造の準備

### 1-1. 必要なディレクトリを作成

MQTTプロジェクトのルートディレクトリに、Mosquitto用のフォルダを作成します。

```bash
# プロジェクトルートで実行
mkdir -p mqtt/config
mkdir -p mqtt/data
mkdir -p mqtt/log
```

**作成されるディレクトリ構造**:
```
D:\Develop\python\StudyMQTT\
├── mqtt/
│   ├── config/      # Mosquittoの設定ファイル
│   ├── data/        # メッセージの永続化データ
│   └── log/         # ログファイル
├── study/
└── docs/
```

### 1-2. ディレクトリの役割

| ディレクトリ | 役割 | 重要度 |
|:---|:---|:---:|
| **config/** | mosquitto.confなどの設定ファイルを配置 | ⭐⭐⭐ |
| **data/** | Retainメッセージなどの永続化データ | ⭐⭐ |
| **log/** | Mosquittoのログファイル | ⭐ |

### 1-3. 確認

```bash
# ディレクトリが作成されたか確認
ls -la mqtt/
```

**期待される出力**:
```
drwxr-xr-x  config/
drwxr-xr-x  data/
drwxr-xr-x  log/
```

---

## ⚙️ ステップ2：Mosquitto設定ファイルの作成

### 2-1. mosquitto.confを作成

学習用の基本的な設定ファイルを作成します。

```bash
# Windowsの場合はメモ帳やVS Codeで作成してもOK
```

**ファイルパス**: `mqtt/config/mosquitto.conf`

**設定内容** (以下をコピー):
```conf
# ========================================
# Mosquitto 設定ファイル（学習用）
# ========================================

# リスナー設定
listener 1883
protocol mqtt

# アクセス制御（学習用：認証なし）
allow_anonymous true

# 永続化設定
persistence true
persistence_location /mosquitto/data/

# ログ設定
log_dest file /mosquitto/log/mosquitto.log
log_dest stdout
log_type all

# 接続設定
max_connections -1
```

### 2-2. 設定の意味

| 設定項目 | 値 | 説明 |
|:---|:---|:---|
| `listener 1883` | 1883 | MQTTのデフォルトポートでリッスン |
| `protocol mqtt` | mqtt | MQTTプロトコルを使用 |
| `allow_anonymous true` | true | 認証なしで接続可能（学習用） |
| `persistence true` | true | Retainメッセージなどを永続化 |
| `persistence_location` | /mosquitto/data/ | データ保存先（コンテナ内） |
| `log_dest file` | /mosquitto/log/ | ログファイル出力先 |
| `log_dest stdout` | stdout | 標準出力にもログを表示 |
| `log_type all` | all | すべてのログを記録 |

⚠️ **本番環境では**: `allow_anonymous false` にして、ユーザー認証を設定してください。

### 2-3. 設定ファイルの確認

```bash
# 設定ファイルが作成されたか確認
cat mqtt/config/mosquitto.conf
```

詳細な設定解説は [02_Mosquitto設定詳細.md](./02_Mosquitto設定詳細.md) を参照してください。

---

## 🐳 ステップ3：Mosquittoイメージの取得

### 3-1. 公式イメージをダウンロード

```bash
docker pull eclipse-mosquitto:latest
```

**出力例**:
```
latest: Pulling from library/eclipse-mosquitto
31e352740f53: Pull complete
...
Status: Downloaded newer image for eclipse-mosquitto:latest
```

### 3-2. イメージの確認

```bash
docker images | grep mosquitto
```

**出力例**:
```
eclipse-mosquitto   latest   a1b2c3d4e5f6   2 weeks ago   15.2MB
```

### 3-3. イメージのサイズ

Mosquittoイメージは非常に軽量（約15MB）です。これがIoTに最適な理由の一つです。

---

## 🏃 ステップ4：Mosquittoコンテナの起動

### 4-1. コンテナを起動（基本コマンド）

**Windows（PowerShell）の場合**:
```powershell
docker run -d `
  --name mqtt-broker `
  -p 1883:1883 `
  -v ${PWD}/mqtt/config:/mosquitto/config `
  -v ${PWD}/mqtt/data:/mosquitto/data `
  -v ${PWD}/mqtt/log:/mosquitto/log `
  eclipse-mosquitto
```

### 4-2. コマンドの解説

| オプション | 説明 |
|:---|:---|
| `-d` | デタッチモード（バックグラウンド実行） |
| `--name mqtt-broker` | コンテナ名を指定（管理しやすくする） |
| `-p 1883:1883` | ポートマッピング（ホスト:コンテナ） |
| `-v [ホスト]:[コンテナ]` | ボリュームマウント（ディレクトリ共有） |
| `eclipse-mosquitto` | 使用するイメージ名 |

### 4-3. コンテナが起動したか確認

```bash
docker ps
```

**期待される出力**:
```
CONTAINER ID   IMAGE               STATUS         PORTS                    NAMES
abc123def456   eclipse-mosquitto   Up 10 seconds  0.0.0.0:1883->1883/tcp   mqtt-broker
```

**STATUSが "Up"** であればOKです！

### 4-4. ログを確認

```bash
docker logs mqtt-broker
```

**正常な出力例**:
```
1234567890: mosquitto version 2.0.18 starting
1234567890: Config loaded from /mosquitto/config/mosquitto.conf.
1234567890: Opening ipv4 listen socket on port 1883.
1234567890: Opening ipv6 listen socket on port 1883.
1234567890: mosquitto version 2.0.18 running
```

---

## ✅ ステップ5：ブローカーの動作確認

### 5-1. コンテナ内部に入る

```bash
docker exec -it mqtt-broker sh
```

プロンプトが変わり、コンテナ内部に入ります：
```
/ #
```

### 5-2. Mosquittoクライアントツールでテスト

#### ターミナル1：Subscriberを起動

コンテナ内で実行：
```sh
mosquitto_sub -t test/topic
```

このターミナルは待機状態になります。

#### ターミナル2：新しいターミナルを開いてPublisherを実行

別のターミナルを開き：
```bash
# 再度コンテナ内に入る
docker exec -it mqtt-broker sh
```

コンテナ内で実行：
```sh
mosquitto_pub -t test/topic -m "Hello MQTT!"
```

#### 結果確認

ターミナル1（Subscriber側）に以下が表示されればOK：
```
Hello MQTT!
```

🎉 **おめでとうございます！MQTTブローカーが正常に動作しています！**

### 5-3. コンテナから退出

```sh
exit
```

---

## 🧪 ステップ6：外部からの接続テスト

次の章（第3章）で作成するPythonクライアントの準備として、外部から接続できるか確認します。

### 6-1. MQTT Explorerをインストール（推奨）

**MQTT Explorer**は、GUIでMQTTを操作できる便利なツールです。

1. [MQTT Explorer公式サイト](http://mqtt-explorer.com/)からダウンロード
2. インストール
3. 起動して以下の設定で接続：
   - **Name**: Local Mosquitto
   - **Host**: localhost
   - **Port**: 1883
   - **Username/Password**: 空欄（認証なし）

4. "CONNECT"をクリック

### 6-2. MQTT Explorerでのテスト

1. **Publish**タブを開く
2. **Topic**: `test/hello` と入力
3. **Message**: `Hello from MQTT Explorer!` と入力
4. "PUBLISH"をクリック
5. 左側のツリーに `test/hello` が表示されればOK

### 6-3. コマンドラインでの外部接続テスト（代替方法）

MQTT Explorerがない場合、`mosquitto_sub`と`mosquitto_pub`をホストにインストールして使用できます。

**Windowsの場合**:
1. [Mosquitto公式サイト](https://mosquitto.org/download/)からWindows版をダウンロード
2. インストール
3. 以下のコマンドで接続：

```bash
# ターミナル1：Subscribe
mosquitto_sub -h localhost -p 1883 -t test/topic

# ターミナル2：Publish
mosquitto_pub -h localhost -p 1883 -t test/topic -m "Hello from host!"
```

---

## 🔄 よく使うDockerコマンド

### コンテナの管理

```bash
# コンテナの起動
docker start mqtt-broker

# コンテナの停止
docker stop mqtt-broker

# コンテナの再起動
docker restart mqtt-broker

# コンテナの削除（停止後）
docker rm mqtt-broker

# コンテナの強制削除（起動中でも削除）
docker rm -f mqtt-broker
```

### ログとステータス確認

```bash
# ログをリアルタイムで表示
docker logs -f mqtt-broker

# 最新100行のログを表示
docker logs --tail 100 mqtt-broker

# コンテナの詳細情報
docker inspect mqtt-broker

# コンテナのリソース使用状況
docker stats mqtt-broker
```

### トラブルシューティング

```bash
# コンテナ内でコマンド実行
docker exec mqtt-broker mosquitto_sub -t test/topic

# コンテナのシェルに入る
docker exec -it mqtt-broker sh

# すべてのコンテナを表示（停止中も含む）
docker ps -a

# 使わなくなったリソースをクリーンアップ
docker system prune
```

---

## 🛠️ トラブルシューティング

### エラー1: ポートが既に使用されている

**エラーメッセージ**:
```
Error: bind: address already in use
```

**原因**: ポート1883が他のプログラムで使用されている

**解決方法**:
```bash
# Windows: ポート1883を使用しているプロセスを確認
netstat -ano | findstr :1883

# プロセスを終了するか、別のポートを使用
docker run -d --name mqtt-broker -p 1884:1883 ...
```

### エラー2: 設定ファイルが読み込まれない

**症状**: ログに "Config file not found" が表示される

**解決方法**:
```bash
# 設定ファイルのパスを確認
ls mqtt/config/mosquitto.conf

# パーミッションを確認
chmod 644 mqtt/config/mosquitto.conf

# コンテナを再起動
docker restart mqtt-broker
```

### エラー3: ボリュームマウントのパスが間違っている

**症状**: データが保存されない、ログファイルが見えない

**解決方法**:
```bash
# 絶対パスで指定
docker run -d --name mqtt-broker \
  -p 1883:1883 \
  -v /d/Develop/python/StudyMQTT/mqtt/config:/mosquitto/config \
  -v /d/Develop/python/StudyMQTT/mqtt/data:/mosquitto/data \
  -v /d/Develop/python/StudyMQTT/mqtt/log:/mosquitto/log \
  eclipse-mosquitto
```

### エラー4: コンテナが起動してもすぐ停止する

**確認方法**:
```bash
# コンテナのログを確認
docker logs mqtt-broker

# 停止したコンテナも表示
docker ps -a
```

**よくある原因**:
- 設定ファイルの文法エラー
- ボリュームのパーミッション問題

詳細は [03_トラブルシューティング.md](./03_トラブルシューティング.md) を参照してください。

---

## 🔒 セキュリティに関する注意

現在の設定は**学習用**です。本番環境では以下を必ず実施してください：

### 本番環境への移行チェックリスト

- [ ] `allow_anonymous false` に変更
- [ ] ユーザー名/パスワード認証を設定
- [ ] TLS/SSL（ポート8883）を有効化
- [ ] クライアント証明書認証を実装
- [ ] ACL（アクセス制御リスト）で権限管理
- [ ] ファイアウォールでポートを制限
- [ ] 定期的なログ監視

**認証の設定例** (次のステップで学びます):
```conf
allow_anonymous false
password_file /mosquitto/config/passwd
```

---

## 📊 動作確認チェックリスト

以下がすべてできればこの章は完了です：

- [ ] Dockerが起動している
- [ ] `mqtt/config`、`mqtt/data`、`mqtt/log` ディレクトリが存在する
- [ ] `mosquitto.conf` が作成されている
- [ ] `docker pull eclipse-mosquitto` が成功
- [ ] `docker run` でコンテナが起動
- [ ] `docker ps` でコンテナが "Up" 状態
- [ ] `docker logs` でエラーがない
- [ ] コンテナ内で `mosquitto_sub/pub` のテストが成功
- [ ] MQTT Explorerまたは外部クライアントから接続できる

---

## 📝 まとめ

### この章で学んだこと

✅ **Eclipse Mosquittoの特徴と利点**
✅ **Dockerでのブローカー構築手順**
✅ **mosquitto.confの基本設定**
✅ **ボリュームマウントによるデータ永続化**
✅ **コンテナの起動・停止・ログ確認**
✅ **ブローカーの動作確認方法**

### 重要なポイント

💡 **ボリュームマウント**により、コンテナを削除してもデータが残る
💡 **ログ出力**を設定することで、問題の診断が容易になる
💡 **学習用設定**と**本番用設定**は大きく異なる
💡 **Dockerコマンド**を使いこなすことで効率的な開発が可能

### 次のステップ

次の第3章では、PythonでMQTTクライアント（PublisherとSubscriber）を実装します。
今回構築したブローカーを使って、実際にメッセージを送受信してみましょう！

**次の章**: [第3章：Pythonクライアントの実装](../step3/00_学習ガイド.md)

---

## 📚 参考資料

- [Eclipse Mosquitto公式ドキュメント](https://mosquitto.org/documentation/)
- [Docker公式ドキュメント](https://docs.docker.com/)
- [MQTT.orgチュートリアル](https://mqtt.org/getting-started/)
- [mosquitto.conf設定リファレンス](https://mosquitto.org/man/mosquitto-conf-5.html)

---

## 🎯 理解度チェック

この章の内容を理解できたか確認しましょう：
[第2章 理解度テスト](./06_理解度テスト.md)
