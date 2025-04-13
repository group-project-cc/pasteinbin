from confluent_kafka import Consumer, KafkaException
import json

conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'combined_consumer_group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
consumer.subscribe(['auth_topic', 'paste_topic', 'access_topic' ])

print("Kafka Consumer listening to 'auth_topic', 'paste_topic', and 'access_topic' ...\n")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())
        try:
            decoded_value = json.loads(msg.value().decode('utf-8'))
            print(f"[{msg.topic().upper()}] {decoded_value}")
        except json.JSONDecodeError:
            print(f"[ERROR] Failed to decode JSON: {msg.value()}")
except KeyboardInterrupt:
    print("\nConsumer shutdown requested by user.")
finally:
    consumer.close()
