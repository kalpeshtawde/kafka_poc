from __future__ import print_function
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint
from confluent_kafka import Consumer
from time import sleep


class SendEmail:

    def run(self, data):
        # Configure API key authorization: api-key
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = ''

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration))
        subject = "My Subject"
        html_content = f"<html><body><h1>{str(data)}</h1></body></html>"
        sender = {"name": "John Doe", "email": "kalpeshtawde@gmail.com"}
        to = [{"email": "kalpeshtawde@outlook.com", "name": "Kalpesh Tawde"}]
        headers = {"Some-Custom-Name": "unique-id-1234"}
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to,
                                                       headers=headers,
                                                       html_content=html_content,
                                                       sender=sender,
                                                       subject=subject)

        try:
            api_response = api_instance.send_transac_email(send_smtp_email)
            pprint(api_response)
        except ApiException as e:
            print(
                "Exception when calling SMTPApi->send_transac_email: %s\n" % e)


class KafkaConsumer:
    broker = "kafka:29092"
    group_id = "consumer-1"

    def start_listener(self):
        consumer_config = {
            'bootstrap.servers': self.broker,
            'group.id': self.group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': 'false',
            'max.poll.interval.ms': '86400000'
        }

        consumer = Consumer(consumer_config)
        consumer.subscribe(['payment', 'delivery'])

        try:
            while True:
                print("Listening")
                # read single message at a time
                msg = consumer.poll(0)

                if msg is None:
                    sleep(5)
                    continue
                if msg.error():
                    print("Error reading message : {}".format(msg.error()))
                    continue
                # You can parse message and save to data base here
                print(msg.value())
                print("Sending email to client")
                sendemail = SendEmail()
                sendemail.run(msg.value())
                consumer.commit()

        except Exception as ex:
            print("Kafka Exception : {}", ex)

        finally:
            print("closing consumer")
            consumer.close()

#RUNNING CONSUMER FOR READING MESSAGE FROM THE KAFKA TOPIC
my_consumer = KafkaConsumer()
my_consumer.start_listener()
