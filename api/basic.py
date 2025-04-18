from confluent_kafka import Consumer, KafkaException
import json
import psycopg2

# PostgreSQL DB connection
conn = psycopg2.connect(
    dbname="logs_db",
    user="admin",
    password="password",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Kafka consumer config
conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'pastebin_consumer_group',
    'auto.offset.reset': 'earliest'
}
consumer = Consumer(conf)
consumer.subscribe(['auth_topic', 'paste_topic', 'access_topic', 'pastebin_api_logs'])

print("📡 Kafka Consumer started. Listening to 4 topics...\n")

# Insert Functions
def insert_auth_log(data):
    cur.execute("""
        INSERT INTO auth_logs (event, username, timestamp, result, endpoint, method, status_code)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        data.get("event"),
        data.get("username"),
        data.get("timestamp"),
        data.get("result"),
        data.get("endpoint"),
        data.get("method"),
        data.get("status_code")
    ))
    conn.commit()

def insert_paste_log(data):
    # Provide a default value for endpoint if it's missing
    endpoint = data.get("endpoint", "N/A")  # or you can use 'null' or other placeholder
    try:
        cur.execute("""
            INSERT INTO paste_logs (event, username, paste_id, timestamp, endpoint, method, status_code, content, result)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get("event"),
            data.get("username"),
            data.get("paste_id"),
            data.get("timestamp"),
            endpoint,  # Use the default value if endpoint is missing
            data.get("method"),
            data.get("status_code"),
            data.get("content"),
            data.get("result")
        ))
        conn.commit()
    except Exception as e:
        print(f"[ERROR] Failed to insert paste log: {e}")
        conn.rollback()

def insert_access_log(data):
    cur.execute("""
        INSERT INTO access_logs (event, username, timestamp, endpoint, method, status_code, keyword, result_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data.get("event"),
        data.get("username"),
        data.get("timestamp"),
        data.get("endpoint"),
        data.get("method"),
        data.get("status_code"),
        data.get("keyword"),
        data.get("result_count")
    ))
    conn.commit()

def insert_request_log(data):
    cur.execute("""
        INSERT INTO request_logs (timestamp, endpoint, method, status_code, response_time_ms, error_message, username)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        data.get("timestamp"),
        data.get("endpoint"),
        data.get("method"),
        data.get("status_code"),
        data.get("response_time_ms"),
        data.get("error_message"),
        data.get("username")
    ))
    conn.commit()

#  Consume & Insert
try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())
        try:
            data = json.loads(msg.value().decode('utf-8'))
            topic = msg.topic()

            print(f"[{topic.upper()}] {data}")

            # Start transaction block
            cur.execute("BEGIN")

            if topic == "auth_topic":
                insert_auth_log(data)
            elif topic == "paste_topic":
                insert_paste_log(data)
            elif topic == "access_topic":
                insert_access_log(data)
            elif topic == "pastebin_api_logs":
                insert_request_log(data)

            # Commit the transaction if no errors
            cur.execute("COMMIT")

        except Exception as e:
            # Rollback on error
            cur.execute("ROLLBACK")
            print(f"[ERROR] {e} for topic {topic}, skipping this message.")

except KeyboardInterrupt:
    print("\n🛑 Consumer shutdown requested.")
finally:
    consumer.close()
    cur.close()
    conn.close()
