from kafka import KafkaConsumer
import json

def main():
    consumer = KafkaConsumer(
        'processed-logins',
        bootstrap_servers=['localhost:29092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='processed-logins-viewer',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    print("Waiting for messages in 'processed-logins' topic...")
    for message in consumer:
        print("\nReceived processed login:")
        print(json.dumps(message.value, indent=2))

if __name__ == "__main__":
    main()