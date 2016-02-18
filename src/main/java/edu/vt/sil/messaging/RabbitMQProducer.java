package edu.vt.sil.messaging;

import com.rabbitmq.client.*;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

/**
 * Author: dedocibula
 * Created on: 16.2.2016.
 */
public class RabbitMQProducer implements AutoCloseable {
    private final static String TOPIC_NAME = "control_topic";
    private final static String QUEUE_NAME = "work_queue";

    private Connection connection;
    private Channel channel;

    public RabbitMQProducer(String host, String userName, String password) throws Exception {
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost(host);
        factory.setUsername(userName);
        factory.setPassword(password);

        connection = factory.newConnection();
        channel = connection.createChannel();

        channel.exchangeDeclare(TOPIC_NAME, "fanout");
        channel.queueDeclare(QUEUE_NAME, true, false, false, null);
    }

    public void sendControlMessage(RabbitMQCommand commandType, String remoteCommand) {
        try {
            AMQP.BasicProperties properties = MessageProperties.TEXT_PLAIN;
            Map<String, Object> headers = new HashMap<>();
            headers.put("command", commandType.name());
            channel.basicPublish(TOPIC_NAME, "", properties.builder().headers(headers).build(), remoteCommand.getBytes(StandardCharsets.UTF_8));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void sendWorkItem(String workItem) {
        try {
            channel.basicPublish("", QUEUE_NAME, MessageProperties.TEXT_PLAIN, workItem.getBytes(StandardCharsets.UTF_8));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    @Override
    public void close() throws Exception {
        channel.close();
        connection.close();
    }
}
