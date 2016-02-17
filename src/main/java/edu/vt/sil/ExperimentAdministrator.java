package edu.vt.sil;

import edu.vt.sil.messaging.RabbitMQCommand;
import edu.vt.sil.messaging.RabbitMQProducer;

import java.util.Arrays;
import java.util.Scanner;
import java.util.stream.Collectors;

/**
 * Author: dedocibula
 * Created on: 16.2.2016.
 */
public class ExperimentAdministrator {
    public static void main(String[] args) throws Exception {
        if (args.length != 3) {
            System.out.println("Please use parameters: <rabbitmq-host> <userName> <password>");
            System.exit(0);
        }

        String host = args[0];
        if (host == null || host.isEmpty()) {
            System.out.println("Cannot use null/empty host");
            System.exit(0);
        }

        String userName = args[1];
        if (userName == null || userName.isEmpty()) {
            System.out.println("Cannot use null/empty userName");
            System.exit(0);
        }

        String password = args[2];
        if (password == null || password.isEmpty()) {
            System.out.println("Cannot use null/empty password");
            System.exit(0);
        }

        try (RabbitMQProducer producer = new RabbitMQProducer(host, userName, password)) {
            try (Scanner scanner = new Scanner(System.in)) {
                String line;
                printHeader();
                while (!(line = scanner.nextLine()).isEmpty())
                    sendCommand(producer, line);
            }
        }
    }

    private static void printHeader() {
        System.out.println("--------------------------------");
        System.out.println("Please enter your command (CTRL+C to exit):");
        System.out.println("    experiment1 <parameters>");
        System.out.println("    experiment2 <parameters>");
        System.out.println("    experiment3 <parameters>");
        System.out.println("    clear_all");
        System.out.println("--------------------------------");
    }

    private static void sendCommand(RabbitMQProducer producer, String line) {
        String[] parts = line.trim().split(" ");
        if (parts.length < 1) {
            System.out.println("Too few arguments");
            return;
        }
        RabbitMQCommand command;
        try {
            command = RabbitMQCommand.valueOf(parts[0].toUpperCase());
        } catch (IllegalArgumentException e) {
            System.out.println("Unrecognized command: " + parts[0]);
            return;
        }
        producer.sendControlMessage(command,
                Arrays.stream(parts).skip(1).collect(Collectors.joining("|,|")));
        System.out.println("Command sent. Enter new command (CTRL+C to exit):");
    }
}
