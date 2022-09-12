import time
from confluent_kafka import Producer
from psycopg2 import connect, extras

from time import sleep
import json


class KafkaProducer:
    broker = "kafka:29092"
    topic = "payment"
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
                callback=lambda err, original_msg=msg: self.delivery_report(err, original_msg),
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


class PaymentNotify:
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
            cursor.execute(f"SELECT id, customer_id, amount, created_at FROM payment where created_at > current_timestamp - interval '30 seconds';")
            records = cursor.fetchall()
            cursor.close()
            conn.close()

            for record in records:
                print(record)
                record['type'] = 'payment'
                json_object = json.dumps(record, indent=4, sort_keys=True, default=str)
                self.producer.send_msg_async(str(json_object))
            sleep(30)


time.sleep(30)
obj = PaymentNotify()
obj.run()


# class ExampleConsumer:
#     broker = "kafka:29092"
#     topic = "payment"
#     group_id = "consumer-1"
#
#     def start_listener(self):
#         consumer_config = {
#             'bootstrap.servers': self.broker,
#             'group.id': self.group_id,
#             'auto.offset.reset': 'earliest',
#             'enable.auto.commit': 'false',
#             'max.poll.interval.ms': '86400000'
#         }
#
#         consumer = Consumer(consumer_config)
#         consumer.subscribe([self.topic])
#
#         try:
#             while True:
#                 print("Listening")
#                 # read single message at a time
#                 msg = consumer.poll(0)
#
#                 if msg is None:
#                     sleep(5)
#                     continue
#                 if msg.error():
#                     print("Error reading message : {}".format(msg.error()))
#                     continue
#                 # You can parse message and save to data base here
#                 print(msg.value())
#                 consumer.commit()
#
#         except Exception as ex:
#             print("Kafka Exception : {}", ex)
#
#         finally:
#             print("closing consumer")
#             consumer.close()
#
# #RUNNING CONSUMER FOR READING MESSAGE FROM THE KAFKA TOPIC
# my_consumer = ExampleConsumer()
# my_consumer.start_listener()
