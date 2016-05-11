package edu.vt.sil.administrator;

import edu.vt.sil.components.Component;
import edu.vt.sil.components.ExperimentOrchestrator;
import edu.vt.sil.components.RemoteFileFetcher;
import edu.vt.sil.components.ResultParser;
import edu.vt.sil.messaging.RabbitMQProducer;
import edu.vt.sil.processor.EventComparisonProcessor;
import edu.vt.sil.processor.OverlapProcessor;
import edu.vt.sil.processor.SimpleDurationProcessor;

import java.util.Map;
import java.util.TreeMap;

/**
 * Author: dedocibula
 * Created on: 2.3.2016.
 */
final class CommandHandler {
    private Map<AdministratorCommand, Component> mappings;

    CommandHandler(RabbitMQProducer producer, String remoteUserName, String privateKeyName) throws Exception {
        mappings = new TreeMap<>();

        ExperimentOrchestrator orchestrator = new ExperimentOrchestrator(producer);
        mappings.put(AdministratorCommand.START_WORKERS, orchestrator);
        mappings.put(AdministratorCommand.RUN_FULL_INGESTION, orchestrator);
        mappings.put(AdministratorCommand.RUN_FULL_RETRIEVAL, orchestrator);
        mappings.put(AdministratorCommand.STOP_WORKERS, orchestrator);

        mappings.put(AdministratorCommand.FETCH_RESULTS, new RemoteFileFetcher(remoteUserName, privateKeyName));
        mappings.put(AdministratorCommand.PROCESS_RESULTS, new ResultParser(new SimpleDurationProcessor(),
                new EventComparisonProcessor(),
                new OverlapProcessor()));
    }

    void printCommandLabels() {
        for (AdministratorCommand command : mappings.keySet())
            System.out.println(String.format("\t%s %s", command, mappings.get(command).showLabel(command)));
    }

    void handleCommand(AdministratorCommand command, String... arguments) throws Exception {
        if (!mappings.containsKey(command))
            throw new IllegalArgumentException(String.format("Unrecognized command: %s", command));

        System.out.println(String.format("Executing command %s", command));
        mappings.get(command).handleCommand(command, arguments);
        System.out.println(String.format("Command %s handled successfully\n", command));
    }
}
