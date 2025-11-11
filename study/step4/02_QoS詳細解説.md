# QoS（品質保証レベル）詳細解説

## 📖 QoSレベルの仕組み

### QoS 0: At most once（最大1回）

```
Publisher → PUBLISH → Broker → PUBLISH → Subscriber
（確認応答なし）
```

**特徴**:
- 最速
- 配信保証なし
- ネットワーク障害でメッセージが失われる可能性

**コード例**:
```python
client.publish("topic", "message", qos=0)
```

---

### QoS 1: At least once（最低1回）

```
Publisher → PUBLISH → Broker → PUBLISH → Subscriber
         ← PUBACK ←        ← PUBACK ←
```

**特徴**:
- 確実に届く
- 重複する可能性がある
- 中程度の速度

**コード例**:
```python
client.publish("topic", "message", qos=1)
```

---

### QoS 2: Exactly once（正確に1回）

```
Publisher → PUBLISH → Broker → PUBLISH → Subscriber
         ← PUBREC ←        ← PUBREC ←
         → PUBREL →        → PUBREL →
         ← PUBCOMP ←       ← PUBCOMP ←
```

**特徴**:
- 重複なし、確実に1回だけ
- 4ウェイハンドシェイク
- 最も遅い

**コード例**:
```python
client.publish("topic", "message", qos=2)
```

---

## 🎯 使い分けガイド

| ユースケース | 推奨QoS | 理由 |
|:---|:---:|:---|
| センサーデータ（1秒ごと） | 0 | 次のデータが来るので欠けてもOK |
| イベント通知（ドア開閉） | 1 | 見逃せないが重複は処理で対応可能 |
| 課金トランザクション | 2 | 重複も欠損も絶対NG |
| チャットメッセージ | 1 | 確実に届けたい |
| 位置情報トラッキング | 0 | リアルタイム性重視 |

---

## ⚠️ 注意点

1. **PublisherとSubscriberの両方で指定**
   - 低い方のQoSが適用される
   - Publisher QoS 2 + Subscriber QoS 0 → 実際はQoS 0

2. **パフォーマンスへの影響**
   - QoS 2は約10倍遅い
   - 大量のデータにはQoS 0を推奨

3. **Retainとの組み合わせ**
   - Retainメッセージにもqosを指定できる
   ```python
   client.publish("topic", "msg", qos=1, retain=True)
   ```

---

**前の章**: [メインドキュメント](./01_MQTT機能実践.md)
