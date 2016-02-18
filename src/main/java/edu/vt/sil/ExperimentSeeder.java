package edu.vt.sil;

import edu.vt.sil.messaging.RabbitMQProducer;

import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

/**
 * Author: dedocibula
 * Created on: 17.2.2016.
 */
public class ExperimentSeeder {
    public static void main(String[] args) throws Exception {
        if (args.length != 3) {
            System.out.println("Please use parameters: <fedora_url> <input_file> <number_of_workers>");
            System.exit(0);
        }

        String fedoraUrl = args[0];
        if (fedoraUrl == null || fedoraUrl.isEmpty()) {
            System.out.println("Cannot use null/empty fedora url");
            System.exit(0);
        }

        String input = args[1];
        Path inputFile = Paths.get(input);
        if (Files.notExists(inputFile, LinkOption.NOFOLLOW_LINKS) || !Files.isRegularFile(inputFile)) {
            System.out.println(String.format("No input file: %s", input));
            System.exit(0);
        }

        int workerCount = 1;
        try {
            workerCount = Integer.parseInt(args[2]);
        } catch (NumberFormatException e) {
            System.out.println(String.format("Illegal number of workers %s", args[2]));
            System.exit(0);
        }

        seedWorkItems(fedoraUrl, Files.readAllLines(inputFile), workerCount);
    }

    private static void seedWorkItems(String fedoraUrl, List<String> lines, int workerCount) throws Exception {
        try (RabbitMQProducer producer = new RabbitMQProducer("research.com", "admin", "admin")) {
            lines.forEach(producer::sendWorkItem);
            for (int i = 0; i < workerCount; i++)
                producer.sendWorkItem("");
            lines.stream()
                    .map(l -> String.format("%s/%s", fedoraUrl, l.substring(0, l.length() - 3)))
                    .forEach(producer::sendWorkItem);
            for (int i = 0; i < workerCount; i++)
                producer.sendWorkItem("");
            lines.stream()
                    .map(l -> String.format("%s/%s", fedoraUrl, l.substring(0, l.length() - 3)))
                    .forEach(producer::sendWorkItem);
            for (int i = 0; i < workerCount; i++)
                producer.sendWorkItem("");
        }
    }
}
