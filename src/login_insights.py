import json
from kafka import KafkaConsumer
import logging
import pprint
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    consumer = KafkaConsumer(
        'login-insights',
        bootstrap_servers=['localhost:29092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='insights-viewer',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    logger.info("Waiting for messages in 'login-insights' topic...")
    
    try:
        for message in consumer:
            insights = message.value
            logger.info("\nReceived login insights:")
            logger.info("Timestamp: %s", datetime.fromtimestamp(message.timestamp / 1000.0).strftime('%Y-%m-%d %H:%M:%S'))
            logger.info("\nDevice Type Distribution:")
            logger.info(pprint.pformat(insights['device_type_distribution'], indent=2, width=100))
            logger.info("\nHourly Login Trend:")
            logger.info(pprint.pformat(insights['hourly_login_trend'], indent=2, width=100))
            logger.info("\nUsers with Multiple IPs: %d", insights['users_with_multiple_ips'])
            logger.info("\n" + "="*50)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        consumer.close()

if __name__ == "__main__":
    main()