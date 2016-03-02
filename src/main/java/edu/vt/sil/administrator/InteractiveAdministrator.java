package edu.vt.sil.administrator;

import edu.vt.sil.components.Component;
import edu.vt.sil.components.ExperimentOrchestrator;
import edu.vt.sil.components.RemoteFileFetcher;
import edu.vt.sil.components.ResultParser;
import edu.vt.sil.messaging.RabbitMQProducer;
import edu.vt.sil.processor.EventComparisonProcessor;
import edu.vt.sil.processor.OverlapProcessor;
import edu.vt.sil.processor.SimpleDurationProcessor;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

/**
 * Author: dedocibula
 * Created on: 16.2.2016.
 */
public final class InteractiveAdministrator {
    public static void main(String[] args) throws Exception {
        if (args.length != 5) {
            System.out.println("Please use parameters:");
            System.out.println("   <rabbitmq host> <rabbitmq username> <rabbitmq password> <remote username> <private key name>");
            System.exit(-1);
        }

        String host = args[0];
        if (host == null || host.isEmpty()) {
            System.out.println("Cannot use null/empty host");
            System.exit(-1);
        }

        String userName = args[1];
        if (userName == null || userName.isEmpty()) {
            System.out.println("Cannot use null/empty user_name");
            System.exit(-1);
        }

        String password = args[2];
        if (password == null || password.isEmpty()) {
            System.out.println("Cannot use null/empty password");
            System.exit(-1);
        }

        String remoteUserName = args[3];
        if (remoteUserName == null || remoteUserName.isEmpty()) {
            System.out.println("Cannot use null/empty remote user name");
            System.exit(-1);
        }

        String privateKeyName = args[4];
        if (privateKeyName == null || privateKeyName.isEmpty()) {
            System.out.println("Cannot use null/empty private key name");
            System.exit(-1);
        }

        try (RabbitMQProducer producer = new RabbitMQProducer(host, userName, password)) {
            Map<AdministratorCommand, Component> mappings = createMappings(producer, remoteUserName, privateKeyName);

            try (Scanner scanner = new Scanner(System.in)) {
                try {
                    String line;
                    while (!(line = scanner.nextLine()).isEmpty()) {
                        printHeader(mappings);
                        handleInput(line, mappings);
                    }
                } catch (Exception e) {
                    System.out.println(e.getMessage());
                }
            }
        } catch (Exception e) {
            System.out.println(e.getMessage());
            System.exit(-1);
        }
    }

    private static Map<AdministratorCommand, Component> createMappings(RabbitMQProducer producer, String remoteUserName, String privateKeyName) throws Exception {
        Map<AdministratorCommand, Component> mappings = new HashMap<>();

        ExperimentOrchestrator orchestrator = new ExperimentOrchestrator(producer);
        mappings.put(AdministratorCommand.START_WORKERS, orchestrator);
        mappings.put(AdministratorCommand.RUN_EXPERIMENT1, orchestrator);
        mappings.put(AdministratorCommand.RUN_EXPERIMENT2, orchestrator);
        mappings.put(AdministratorCommand.RUN_EXPERIMENT3, orchestrator);
        mappings.put(AdministratorCommand.STOP_WORKERS, orchestrator);

        mappings.put(AdministratorCommand.FETCH_RESULTS, new RemoteFileFetcher(remoteUserName, privateKeyName));
        mappings.put(AdministratorCommand.PROCESS_RESULTS, new ResultParser(new SimpleDurationProcessor(),
                new EventComparisonProcessor(),
                new OverlapProcessor()));

        return mappings;
    }

    private static void printHeader(Map<AdministratorCommand, Component> mappings) {
        System.out.println("------------------------------------------------------------");
        System.out.println("Please enter your command (Empty command or CTRL+C to exit):");
        for (AdministratorCommand command : mappings.keySet())
            System.out.println(String.format("\t%s %s", command, mappings.get(command).showLabel(command)));
        System.out.println("------------------------------------------------------------");
    }

    private static void handleInput(String line, Map<AdministratorCommand, Component> mappings) throws Exception {
        String[] parts = line.trim().split(" ");
        if (parts.length < 1) {
            System.out.println("Too few arguments");
            return;
        }

        AdministratorCommand command;
        try {
            command = AdministratorCommand.valueOf(parts[0].toUpperCase());
        } catch (IllegalArgumentException e) {
            System.out.println(String.format("Unrecognized command: %s", parts[0]));
            return;
        }
        String[] arguments = Arrays.copyOfRange(parts, 1, parts.length);

        mappings.get(command).handleCommand(command, arguments);
        System.out.println(String.format("Command %s handled successfully\n", command));
    }
}
