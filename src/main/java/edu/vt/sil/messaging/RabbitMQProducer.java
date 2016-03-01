package edu.vt.sil.messaging;

import com.rabbitmq.client.*;

import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Author: dedocibula
 * Created on: 16.2.2016.
 */
public final class RabbitMQProducer implements AutoCloseable {
    private static final String WAIT_QUEUE_NAME = "wait_queue";
    private static final String WAIT_QUEUE_CALLBACK = "wait_queue_callback";
    private static final String CONTROL_TOPIC_NAME = "control_topic";
    private static final String CONTROL_TOPIC_CALLBACK = "control_topic_callback";
    private static final String WORK_QUEUE_NAME = "work_queue";

    private static final String ARGUMENTS_JOINER = "|,|";

    private Connection connection;
    private Channel channel;
    private QueueingConsumer waitQueueConsumer;
    private QueueingConsumer controlTopicConsumer;

    public RabbitMQProducer(String host, String userName, String password) throws Exception {
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost(host);
        factory.setUsername(userName);
        factory.setPassword(password);

        connection = factory.newConnection();
        channel = connection.createChannel();

        channel.queueDeclare(WAIT_QUEUE_NAME, true, false, false, null);
        channel.queueDeclare(WAIT_QUEUE_CALLBACK, false, true, true, null);
        waitQueueConsumer = new QueueingConsumer(channel);
        channel.basicConsume(WAIT_QUEUE_CALLBACK, true, waitQueueConsumer);

        channel.exchangeDeclare(CONTROL_TOPIC_NAME, "fanout");
        channel.queueDeclare(CONTROL_TOPIC_CALLBACK, false, true, true, null);
        controlTopicConsumer = new QueueingConsumer(channel);
        channel.basicConsume(CONTROL_TOPIC_CALLBACK, true, controlTopicConsumer);

        channel.queueDeclare(WORK_QUEUE_NAME, true, false, false, null);
    }

    public String addWorker() throws Exception {
        AMQP.BasicProperties properties = MessageProperties.TEXT_PLAIN
                .builder()
                .correlationId(UUID.randomUUID().toString())
                .replyTo(WAIT_QUEUE_CALLBACK)
                .build();
        channel.basicPublish("", WAIT_QUEUE_NAME, properties, "addWorker".getBytes(StandardCharsets.UTF_8));

        return waitForHostAcknowledgements(waitQueueConsumer, properties.getCorrelationId(), 1).get(0);
    }

    public List<String> sendControlMessage(String command, String[] arguments, int waitAcknowledgements) throws Exception {
        Objects.requireNonNull(command);
        Objects.requireNonNull(arguments);

        Map<String, Object> headers = new HashMap<>();
        headers.put("command", command);

        AMQP.BasicProperties properties = MessageProperties.TEXT_PLAIN
                .builder()
                .headers(headers)
                .correlationId(UUID.randomUUID().toString())
                .replyTo(CONTROL_TOPIC_CALLBACK)
                .build();
        byte[] payload = Arrays.stream(arguments).collect(Collectors.joining(ARGUMENTS_JOINER)).getBytes(StandardCharsets.UTF_8);
        channel.basicPublish(CONTROL_TOPIC_NAME, "", properties, payload);

        return waitForHostAcknowledgements(controlTopicConsumer, properties.getCorrelationId(), waitAcknowledgements);
    }

    public void sendWorkItem(String workItem) throws Exception {
        Objects.requireNonNull(workItem);

        channel.basicPublish("", WORK_QUEUE_NAME, MessageProperties.TEXT_PLAIN, workItem.getBytes(StandardCharsets.UTF_8));
        channel.waitForConfirms();
    }

    public void purgeWorkItems() throws Exception {
        channel.queuePurge(WORK_QUEUE_NAME);
    }

    private List<String> waitForHostAcknowledgements(QueueingConsumer consumer, String correlationId, int waitAcknowledgements) throws InterruptedException {
        List<String> result = new ArrayList<>();

        while (result.size() < waitAcknowledgements) {
            QueueingConsumer.Delivery delivery = consumer.nextDelivery();
            if (delivery.getProperties().getCorrelationId().equals(correlationId))
                result.add(new String(delivery.getBody()));
        }

        return result;
    }

    @Override
    public void close() throws Exception {
        channel.close();
        connection.close();
    }
}
