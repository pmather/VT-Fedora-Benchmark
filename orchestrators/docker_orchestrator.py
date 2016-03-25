import pika
import sys
import uuid
import os
from subprocess import call

rabbitmq_host = None
rabbitmq_username = None
rabbitmq_password = None
host_id = None

running_containers_file = None


def start_docker(id, control_topic_name, work_queue_name):
    call("docker run -d --privileged --name={} dedocibula/fedora-benchmark python "
         "experiment_coordinator.py {} {} {} {} {} {}".format(id, rabbitmq_host, rabbitmq_username, rabbitmq_password,
                                                              id, control_topic_name, work_queue_name))


def stop_docker(name):
    call("docker stop {} && docker rm {}".format(name, name))


def fetch_results():
    docker_containers = running_containers_file.readlines()
    for i in range(0, len(docker_containers)):
        base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), str(i + 1))
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        for file in os.listdir(base_path):
            file_path = os.path.join(base_path, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception, e:
                print e
        call("docker cp {}:/vt-fedora-benchmark/experiments/. {}".format(docker_containers[i], base_path), shell=True)
        with open(os.path.join(base_path, "experiment.out"), "w") as f, open(os.devnull, 'w') as fnull:
            call(["docker", "logs", docker_containers[i]], stdout=f, stderr=fnull)
        for file in os.listdir(base_path):
            print os.path.join(base_path, file)


def on_request(ch, method, props, body):
    print "Received command: " + body

    if body == "ADD_WORKERS" and props.correlation_id:
        if not props.headers and ("controlTopicName" not in props.headers or "workQueueName" not in props.headers):
            print "Missing necessary headers (controlTopicName and workQueueName)"
            return

        global running_containers_file
        for container in running_containers_file.readlines():
            stop_docker(container)
        running_containers_file.seek(0)
        running_containers_file.truncate()

        work_queue_name = props.headers["workQueueName"]
        control_topic_name = props.headers["controlTopicName"]
        worker_count = int(props.headers["workerCount"]) if "workerCount" in props.headers else 1

        for i in range(0, worker_count):
            name = "{}_fedora_benchmark_{}".format(host_id, str(i))
            start_docker(name, control_topic_name, work_queue_name)
            running_containers_file.write(name + "\n")
            ch.basic_publish(exchange='',
                             routing_key=props.reply_to,
                             properties=pika.BasicProperties(correlation_id=props.correlation_id),
                             body=str(name))

        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        print "Unrecognized command: " + body


def main():
    global rabbitmq_host
    global rabbitmq_username
    global rabbitmq_password
    global host_id
    global running_containers_file

    rabbitmq_host = sys.argv[1]
    rabbitmq_username = sys.argv[2]
    rabbitmq_password = sys.argv[3]
    host_id = uuid.uuid4()

    credentials = pika.PlainCredentials(rabbitmq_username, rabbitmq_password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue='wait_queue', durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(on_request, queue='wait_queue')

    print "Listening for commands on the wait queue. CTRL + C to exit"

    running_containers_file = open("running-containers.txt", "r+")
    channel.start_consuming()
    running_containers_file.close()


if __name__ == "__main__": main()
