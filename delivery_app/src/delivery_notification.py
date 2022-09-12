import time
from confluent_kafka import Producer
from psycopg2 import connect, extras

from time import sleep
import json


class KafkaProducer:
    broker = "kafka:29092"
    topic = "delivery"
    producer = None

    def __init__(self):
        self.producer = Producer({
            'bootstrap.servers': self.broker,
            'socket.timeout.ms': 100,
            'api.version.request': 'false',
            'broker.version.fallback': '0.9.0',
        }
        )

    def delivery_report(self, err, msg):
        """ Called once for each message produced to indicate delivery result.
            Triggered by poll() or flush(). """
        if err is not None:
            print('Message delivery failed: {}'.format(err))
        else:
            print('Message delivered to {} [{}]'.format(
                msg.topic(), msg.partition()))

    def send_msg_async(self, msg):
        print("Send message asynchronously")
        try:
            self.producer.produce(
                self.topic,
                msg,
                callback=lambda err, original_msg=msg: self.delivery_report(err, original_msg
                                                                            ),
            )
        except Exception:
            pass
        else:
            self.producer.flush()

    def send_msg_sync(self, msg):
        print("Send message synchronously")
        self.producer.produce(
            self.topic,
            msg,
            callback=lambda err, original_msg=msg: self.delivery_report(
                err, original_msg
            ),
        )
        self.producer.flush()


class DeliveryNotify:
    def __init__(self):
        self.producer = KafkaProducer()

    def run(self):
        while True:
            conn = connect(
                dbname="postgres",
                user="postgres",
                host="192.168.55.12",
                port="5432",
                password="postgres"
            )
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute(f"SELECT id, customer_id, product_id, "
                                f"delivered_at "
                                f"FROM delivery where delivered_at > "
                                f"current_timestamp - interval '30 seconds';")
            records = cursor.fetchall()
            cursor.close()
            conn.close()

            for record in records:
                record['type'] = 'delivery'
                json_object = json.dumps(record, indent=4, sort_keys=True, default=str)
                self.producer.send_msg_async(str(json_object))
            sleep(30)


time.sleep(30)
obj = DeliveryNotify()
obj.run()
