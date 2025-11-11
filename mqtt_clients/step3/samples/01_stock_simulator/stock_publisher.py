import paho.mqtt.client as mqtt
import random
import time

BROKER = "localhost"
stocks = {
    "AAPL": 150.0,
    "GOOGL": 2800.0,
    "TSLA": 700.0
}

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.connect(BROKER, 1883, 60)

print("📈 株価シミュレータを開始...")
print("-" * 50)

try:
    while True:
        for symbol, price in stocks.items():
            # -2%〜+2%のランダムな変動
            change = random.uniform(-0.02, 0.02)
            new_price = round(price * (1 + change), 2)
            stocks[symbol] = new_price

            message = f"{new_price}"
            client.publish(f"stock/{symbol}", message)
            print(f"📊 {symbol}: ${new_price}")

        print("-" * 50)
        time.sleep(2)
except KeyboardInterrupt:
    client.disconnect()
