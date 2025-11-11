# subscriber.py
import paho.mqtt.client as mqtt

# 接続設定
BROKER = "localhost"
PORT = 1883
TOPIC = "test/1/#"

# メッセージを受信したときの処理
def on_message(client, userdata, msg):
    """
    メッセージが届いたら、この関数が自動的に呼ばれます
    """
    message = msg.payload.decode('utf-8')
    topic = msg.topic
    print(f"📨 受信: [{topic}] {message}")

# 接続成功時の処理
def on_connect(client, userdata, flags, rc):
    """
    ブローカーに接続できたら、この関数が自動的に呼ばれます
    """
    if rc == 0:
        print("✅ ブローカーに接続しました")
        print(f"📻 トピック '{TOPIC}' を購読開始...")
        client.subscribe(TOPIC)
    else:
        print(f"❌ 接続失敗: エラーコード {rc}")

# MQTTクライアントを作成
client = mqtt.Client()

# コールバック関数を登録
client.on_connect = on_connect
client.on_message = on_message

print("🔌 MQTTブローカーに接続中...")
client.connect(BROKER, PORT, 60)

print("⏳ メッセージを待っています... (Ctrl+Cで終了)")
print("-" * 50)

# メッセージを待ち続ける
client.loop_forever()
