package edu.vt.sil.administrator;

import edu.vt.sil.messaging.RabbitMQProducer;

import java.io.IOException;
import java.nio.file.*;
import java.util.Arrays;
import java.util.List;
import java.util.Scanner;
import java.util.stream.Collectors;

/**
 * Author: dedocibula
 * Created on: 16.2.2016.
 */
public final class ExperimentAdministrator {
//    public static void main(String[] args) throws Exception {
//        if (args.length != 3) {
//            System.out.println("Please use parameters: <rabbitmq-host> <user_name> <password>");
//            System.exit(0);
//        }
//
//        String host = args[0];
//        if (host == null || host.isEmpty()) {
//            System.out.println("Cannot use null/empty host");
//            System.exit(0);
//        }
//
//        String userName = args[1];
//        if (userName == null || userName.isEmpty()) {
//            System.out.println("Cannot use null/empty user_name");
//            System.exit(0);
//        }
//
//        String password = args[2];
//        if (password == null || password.isEmpty()) {
//            System.out.println("Cannot use null/empty password");
//            System.exit(0);
//        }
//
//        try (RabbitMQProducer producer = new RabbitMQProducer(host, userName, password)) {
//            try (Scanner scanner = new Scanner(System.in)) {
//                String line;
//                printHeader();
//                while (!(line = scanner.nextLine()).isEmpty())
//                    handleInput(producer, line);
//            }
//        }
//    }
//
//    private static void printHeader() {
//        System.out.println("--------------------------------");
//        System.out.println("Please enter your command (CTRL+C to exit):");
//        System.out.println("    experiment1 <parameters>");
//        System.out.println("    experiment2 <parameters>");
//        System.out.println("    experiment3 <parameters>");
//        System.out.println("    clear_all");
//        System.out.println("    seed <fedora_url> <input_file> <number_of_consumers>");
//        System.out.println("--------------------------------");
//    }
//
//    private static void handleInput(RabbitMQProducer producer, String line) {
//        String[] parts = line.trim().split(" ");
//        if (parts.length < 1) {
//            System.out.println("Too few arguments");
//            return;
//        }
//        Command command;
//        try {
//            command = Command.valueOf(parts[0].toUpperCase());
//        } catch (IllegalArgumentException e) {
//            System.out.println("Unrecognized command: " + parts[0]);
//            return;
//        }
//
//        if (command == Command.SEED) {
//            seedWorkItems(producer, Arrays.copyOfRange(parts, 1, parts.length));
//        } else {
//            producer.sendControlMessage(command,
//                    Arrays.stream(parts).skip(1).collect(Collectors.joining("|,|")));
//            System.out.println("Command sent. Enter new command (CTRL+C to exit):");
//        }
//    }
//
//    private static void seedWorkItems(RabbitMQProducer producer, String[] arguments) {
//        String fedoraUrl = arguments[0];
//        if (fedoraUrl == null || fedoraUrl.isEmpty()) {
//            System.out.println("Cannot use null/empty fedora url");
//            return;
//        }
//
//        String input = arguments[1];
//        Path inputFile;
//        try {
//            inputFile = Paths.get(input);
//            if (Files.notExists(inputFile, LinkOption.NOFOLLOW_LINKS) || !Files.isRegularFile(inputFile)) {
//                System.out.println(String.format("No input file: %s", input));
//                return;
//            }
//        } catch (InvalidPathException e) {
//            System.out.println(e.getMessage());
//            return;
//        }
//
//        List<String> lines;
//        try {
//            lines = Files.readAllLines(inputFile);
//        } catch (IOException e) {
//            System.out.println(String.format("File not readable %s", input));
//            return;
//        }
//
//        int workerCount;
//        try {
//            workerCount = Integer.parseInt(arguments[2]);
//        } catch (NumberFormatException e) {
//            System.out.println(String.format("Illegal number of workers %s", arguments[2]));
//            return;
//        }
//
//        lines.forEach(producer::sendWorkItem);
//        for (int i = 0; i < workerCount; i++)
//            producer.sendWorkItem("");
//        for (int j = 0; j < 2; j++) {
//            lines.stream()
//                    .map(l -> String.format("%s/%s", fedoraUrl, l.substring(0, l.length() - 3)))
//                    .forEach(producer::sendWorkItem);
//            for (int i = 0; i < workerCount; i++)
//                producer.sendWorkItem("");
//        }
//
//        System.out.println("Work Items seeded. Enter new command (CTRL+C to exit)");
//    }
}
