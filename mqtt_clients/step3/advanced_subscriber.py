# advanced_subscriber.py
import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc):
    print(f"🔌 接続: rc={rc}")
    if rc == 0:
        print("✅ 接続成功")
        client.subscribe("test/#")
    else:
        error_messages = {
            1: "不正なプロトコルバージョン",
            2: "クライアントIDが拒否されました",
            3: "サーバーが利用できません",
            4: "ユーザー名またはパスワードが間違っています",
            5: "認証されていません"
        }
        print(f"❌ 接続失敗: {error_messages.get(rc, '不明なエラー')}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("⚠️ 切断されました。再接続します...")
        time.sleep(5)
        try:
            client.reconnect()
        except:
            print("❌ 再接続に失敗しました")


def on_message(client, userdata, msg):
    print(f"📨 メッセージ: [{msg.topic}] {msg.payload.decode()}")

def on_subscribe(client, userdata, mid, granted_qos):
    print(f"✅ 購読成功: QoS={granted_qos[0]}")

def on_log(client, userdata, level, buf):
    print(f"📝 ログ: {buf}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.on_log = on_log

try:
    client.connect("localhost", 1883, 60)
    client.loop_forever()
except Exception as e:
    print(f"⚠️ エラーが発生しました: {e}")
