import json
from datetime import datetime
from collections import defaultdict
from kafka import KafkaConsumer, KafkaProducer
import logging
import pprint

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global variables for storing aggregated data
device_type_counts = defaultdict(int)
hourly_login_counts = defaultdict(int)
user_ip_map = defaultdict(set)

def process_message(message):
    global device_type_counts, hourly_login_counts, user_ip_map
    
    device_type = message.get('device_type', 'unknown')
    device_type_counts[device_type] += 1
    
    timestamp = int(message.get('timestamp', 0))
    hour = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:00')
    hourly_login_counts[hour] += 1
    
    user_id = message.get('user_id', 'unknown')
    ip = message.get('ip', 'unknown')
    user_ip_map[user_id].add(ip)
    
    processed_data = {
        'user_id': user_id,
        'timestamp': timestamp,
        'device_type': device_type,
        'app_version': message.get('app_version', 'unknown'),
        'ip_count': len(user_ip_map[user_id])
    }
    
    return processed_data

def generate_insights():
    insights = {
        'device_type_distribution': dict(device_type_counts),
        'hourly_login_trend': dict(hourly_login_counts),
        'users_with_multiple_ips': sum(1 for ips in user_ip_map.values() if len(ips) > 1)
    }
    return insights

def main():
    consumer = KafkaConsumer(
        'user-login',
        bootstrap_servers=['localhost:29092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='my-consumer-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    producer = KafkaProducer(
        bootstrap_servers=['localhost:29092'],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )

    message_count = 0
    processed_count = 0
    skipped_count = 0

    try:
        for message in consumer:
            message_count += 1
            try:
                processed_data = process_message(message.value)
                producer.send('processed-logins', value=processed_data)
                processed_count += 1
                
                if message_count % 100 == 0:
                    insights = generate_insights()
                    producer.send('login-insights', value=insights)
                    logger.info(f"\nProcessed {message_count} messages. Latest insights:")
                    logger.info(pprint.pformat(insights, indent=2, width=100))
                    logger.info(f"\nProcessed: {processed_count}, Skipped: {skipped_count}")
                
            except Exception as e:
                logger.warning(f"Error processing message: {str(e)}")
                skipped_count += 1

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        logger.info(f"\nFinal count - Processed: {processed_count}, Skipped: {skipped_count}")
        consumer.close()
        producer.close()

if __name__ == "__main__":
    main()