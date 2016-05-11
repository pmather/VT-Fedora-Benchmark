import pika
import sys
import traceback
import os

from commons import RabbitMQClient, GoogleDriveDownloader, S3Downloader

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
        if body == "FULL_INGESTION" or body == "PROXY_INGESTION":
            if not props.headers and (
                                "fedoraUrl" not in props.headers or "storageType" not in props.headers or "storageFolder" not in props.headers):
                print "Missing necessary headers (fedoraUrl, storageType, storageFolder)"
                return
            fedora_url = props.headers["fedoraUrl"]
            downloader = create_remote_downloader(props.headers["storageType"], props.headers["storageFolder"])
            client = RabbitMQClient(connection, work_queue_name)
            print "Starting " + body
            if body == "FULL_INGESTION":
                import full_ingestion
                full_ingestion.run(fedora_url, downloader, client)
            else:
                import proxy_ingestion
                proxy_ingestion.run(fedora_url, downloader, client)
            print "Finished running " + body + ". Acknowledging success"
            acknowledge(ch, props.reply_to, props.correlation_id)
        elif body == "FULL_RETRIEVAL" or body == "PROXY_RETRIEVAL":
            client = RabbitMQClient(connection, work_queue_name)
            print "Starting " + body
            if body == "FULL_RETRIEVAL":
                import full_retrieval
                full_retrieval.run(client)
            else:
                import proxy_retrieval
                proxy_retrieval.run(client)
            print "Finished running " + body + ". Acknowledging success"
            acknowledge(ch, props.reply_to, props.correlation_id)
        elif body == "SHUTDOWN":
            if os.path.isfile("fedoraurls.txt"):
                import clear_all
                print "Performing cleanup"
                clear_all.main("fedoraurls.txt")
            print "Disconnecting from control topic"
            acknowledge(ch, props.reply_to, props.correlation_id)
            ch.queue_delete(queue=temp_queue_name)
            ch.close()
            connection.close()
        else:
            print "Unrecognized command"
    except:
        print "Error occurred: " + traceback.format_exc()


def acknowledge(ch, reply_to, correlation_id):
    ch.basic_publish(exchange='',
                     routing_key=reply_to,
                     properties=pika.BasicProperties(correlation_id=correlation_id),
                     body=str(host_id))


def create_remote_downloader(storage_type, storage_folder):
    if storage_type == "GOOGLE_DRIVE":
        return GoogleDriveDownloader(storage_folder)
    elif storage_type == "S3":
        return S3Downloader(storage_folder)
    else:
        raise ValueError("Unexpected storage type: " + storage_type)


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
        acknowledge(channel, acknowledge_queue, correlation_id)

    channel.start_consuming()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6],
         sys.argv[7] if len(sys.argv) > 7 and sys.argv[7] != "None" else None,
         sys.argv[8] if len(sys.argv) > 8 and sys.argv[7] != "None" else None)
