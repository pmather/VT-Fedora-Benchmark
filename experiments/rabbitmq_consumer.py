import pika
import sys
import traceback

rabbitmqurl = None
rabbitmquser = None
rabbitmqpassword = None


def check_params(params, expected):
    if len(params) < expected:
        print "Illegal number of parameter. Expected number is " + expected
        return False
    return True


def handleMessage(ch, method, properties, body):
    if not properties.headers and "command" not in properties.headers:
        print "Unrecognized message"
        return
    command = properties.headers["command"]
    params = body.strip().split("|,|")
    try:
        print "Received command: " + command + " , parameters: " + ", ".join(params)
        if command == "EXPERIMENT1":
            if not check_params(params, 3):
                return
            import experiment1
            experiment1.main(params[0], params[1], params[2], rabbitmqurl, rabbitmquser, rabbitmqpassword)
        elif command == "EXPERIMENT2":
            if not check_params(params, 1):
                return
            import experiment2
            experiment2.main(params[0], rabbitmqurl, rabbitmquser, rabbitmqpassword)
        elif command == "EXPERIMENT3":
            if not check_params(params, 1):
                return
            import experiment3
            experiment3.main(params[0], rabbitmqurl, rabbitmquser, rabbitmqpassword)
        elif command == "CLEAR_ALL":
            import clear_all
            clear_all.main("fedoraurls.txt")
        else:
            print "Unrecognized command"
    except:
        print "Error occurred: " + traceback.format_exc()


def main():
    global rabbitmqurl
    global rabbitmquser
    global rabbitmqpassword
    rabbitmqurl = sys.argv[1]
    rabbitmquser = sys.argv[2]
    rabbitmqpassword = sys.argv[3]

    credentials = pika.PlainCredentials(rabbitmquser, rabbitmqpassword)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmqurl, credentials=credentials))

    channel = connection.channel()
    channel.exchange_declare(exchange='control_topic', type='fanout')

    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='control_topic', queue=queue_name)

    print "Beginning processing messages on control topic. Press CTRL+C to exit."

    channel.basic_consume(handleMessage, queue=queue_name, no_ack=True)
    channel.start_consuming()


if __name__ == "__main__": main()
