import pika
import sys
import traceback
import os

from commons import RabbitMQClient, GoogleDriveDownloader

connection = None
work_queue_name = None
host_id = None
temp_queue_name = None


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
            print "Starting experiment 1"
            experiment1.run(fedora_url, downloader, client)
            print "Finished running experiment 1. Acknowledging success"
            acknowledge(ch, props)
        elif body == "EXPERIMENT2":
            import experiment2
            client = RabbitMQClient(connection, work_queue_name)
            print "Starting experiment 2"
            experiment2.run(client)
            print "Finished running experiment 2. Acknowledging success"
            acknowledge(ch, props)
        elif body == "EXPERIMENT3":
            import experiment3
            client = RabbitMQClient(connection, work_queue_name)
            print "Starting experiment 3"
            experiment3.run(client)
            print "Finished running experiment 3. Acknowledging success"
            acknowledge(ch, props)
        elif body == "SHUTDOWN":
            if os.path.isfile("fedoraurls.txt"):
                import clear_all
                print "Performing cleanup"
                clear_all.main("fedoraurls.txt")
            print "Disconnecting from control topic"
            acknowledge(ch, props)
            ch.queue_delete(queue=temp_queue_name)
            ch.close()
            connection.close()
        else:
            print "Unrecognized command"
    except:
        print "Error occurred: " + traceback.format_exc()


def acknowledge(ch, props):
    ch.basic_publish(exchange='',
                     routing_key=props["reply_to"],
                     properties=pika.BasicProperties(correlation_id=props["correlation_id"]),
                     body=str(host_id))


def main(rabbitmq_host, rabbitmq_username, rabbitmq_password, worker_id, control_topic, work_queue,
         acknowledge_queue=None, correlation_id=None):
    global connection
    global host_id
    global work_queue_name
    global temp_queue_name

    host_id = worker_id
    work_queue_name = work_queue

    credentials = pika.PlainCredentials(rabbitmq_username, rabbitmq_password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials))

    channel = connection.channel()
    channel.exchange_declare(exchange=control_topic, type='fanout')
    result = channel.queue_declare(exclusive=True)
    temp_queue_name = result.method.queue
    channel.queue_bind(exchange=control_topic, queue=temp_queue_name)

    print "Listening for commands on the control topic. CTRL + C to exit"

    channel.basic_consume(handle_control_message, queue=temp_queue_name, no_ack=True)
    if acknowledge_queue and correlation_id:
        acknowledge(channel, {"reply_to": acknowledge_queue, "correlation_id": correlation_id})

    channel.start_consuming()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6],
         sys.argv[7] if len(sys.argv) > 7 else None, sys.argv[8] if len(sys.argv) > 8 else None)
