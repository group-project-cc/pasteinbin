from confluent_kafka.admin import AdminClient, NewTopic

admin = AdminClient({
    "bootstrap.servers": "localhost:9092"
})

topics = [
    NewTopic("auth_topic", num_partitions=3, replication_factor=1),
    NewTopic("paste_topic", num_partitions=4, replication_factor=1),
    NewTopic("access_topic", num_partitions=2, replication_factor=1),
    NewTopic("error_topic", num_partitions=1, replication_factor=1),
    NewTopic("pastebin_api_logs", num_partitions=1, replication_factor=1)
]

fs = admin.create_topics(topics)

for topic, f in fs.items():
    try:
        f.result()
        print(f"Topic '{topic}' created successfully.")
    except Exception as e:
        print(f"Failed to create topic '{topic}': {e}")
