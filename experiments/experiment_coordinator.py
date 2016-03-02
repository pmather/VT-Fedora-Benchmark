import pika
import sys
import traceback
import uuid
import os

from commons import RabbitMQClient, GoogleDriveDownloader

connection = None
work_queue_name = None
host_id = None


def on_request(ch, method, props, body):
    print "Received command: " + body

    if body == "ADD_WORKER" and props.correlation_id:
        if not props.headers and ("controlTopicName" not in props.headers or "workQueueName" not in props.headers):
            print "Missing necessary headers (controlTopicName and workQueueName)"
            return

        global work_queue_name
        work_queue_name = props.headers["workQueueName"]
        control_topic_name = props.headers["controlTopicName"]

        channel = connection.channel()
        channel.exchange_declare(exchange=control_topic_name, type='fanout')
        result = channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange=control_topic_name, queue=queue_name)

        print "Beginning processing messages on control topic."

        channel.basic_consume(handle_control_message, queue=queue_name, no_ack=True)
        channel.start_consuming()

        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id=props.correlation_id),
                         body=str(host_id))
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        print "Unrecognized command: " + body


def handle_control_message(ch, method, props, body):
    if not body:
        print "Unrecognized message"
        return
    try:
        print "Received command: " + body + " , parameters: " + str(props.headers)
        if body == "EXPERIMENT1":
            if not props.headers and ("fedoraUrl" not in props.headers or "storageFolder" not in props.headers):
                print "Missing necessary headers (controlTopicName and workQueueName)"
                return
            import experiment1
            fedora_url = props.headers["fedoraUrl"]
            downloader = GoogleDriveDownloader(props.headers["storageFolder"])
            client = RabbitMQClient(connection, work_queue_name)
            experiment1.run(fedora_url, downloader, client)
        elif body == "EXPERIMENT2":
            import experiment2
            client = RabbitMQClient(connection, work_queue_name)
            experiment2.run(client)
        elif body == "EXPERIMENT3":
            import experiment3
            client = RabbitMQClient(connection, work_queue_name)
            experiment3.run(client)
        elif body == "SHUTDOWN":
            if os.path.isfile("fedoraurls.txt"):
                import clear_all
                clear_all.main("fedoraurls.txt")
            ch.close()
        else:
            print "Unrecognized command"
    except:
        print "Error occurred: " + traceback.format_exc()


def main():
    global connection
    global host_id

    host_id = uuid.uuid4()

    credentials = pika.PlainCredentials(sys.argv[2], sys.argv[3])
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=sys.argv[1], credentials=credentials))
    channel = connection.channel()

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(on_request, queue='wait_queue')

    print "Listening for commands on the wait queue. CTRL + C to exit."


if __name__ == "__main__": main()
