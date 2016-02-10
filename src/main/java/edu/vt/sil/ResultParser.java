package edu.vt.sil;

import edu.vt.sil.entities.Event;
import edu.vt.sil.entities.ExperimentResult;
import edu.vt.sil.processor.EventComparisonProcessor;
import edu.vt.sil.processor.OverlapProcessor;
import edu.vt.sil.processor.Processor;
import edu.vt.sil.processor.SimpleDurationProcessor;

import java.io.IOException;
import java.nio.file.*;
import java.util.*;

/**
 * Author: dedocibula
 * Created on: 9.2.2016.
 */
public class ResultParser {
    public static void main(String[] args) throws IOException {
        if (args.length != 2) {
            System.out.println("Please use parameters: <results directory> <results prefix>");
            System.exit(0);
        }

        String directory = args[0];
        Path resultsDir = Paths.get(directory);
        if (Files.notExists(resultsDir, LinkOption.NOFOLLOW_LINKS) || !Files.isDirectory(resultsDir)) {
            System.out.println(String.format("No directory: %s", directory));
            System.exit(0);
        }

        String prefix = args[1];
        if (prefix == null || prefix.isEmpty()) {
            System.out.println("Cannot use null/empty prefix");
            System.exit(0);
        }

        Map<String, List<ExperimentResult>> results = extractExperimentResults(resultsDir, prefix);

        Path output = Paths.get(directory, String.format("%s_processed.csv", prefix));
        processResults(output, results,
                new SimpleDurationProcessor(),
                new EventComparisonProcessor(),
                new OverlapProcessor());
    }

    private static void processResults(Path output, Map<String, List<ExperimentResult>> results, Processor... processors) throws IOException {
        if (processors == null)
            return;

        for (Processor processor : processors) {
            String description = processor.getDescription();
            String headers = processor.getHeaders(results);
            List<String> content = processor.process(results);
            if (description != null)
                content.add(0, description);
            if (headers != null)
                content.add(1, headers);
            content.add("");
            Files.write(output, content, StandardOpenOption.APPEND, StandardOpenOption.CREATE);
        }
    }

    private static Map<String, List<ExperimentResult>> extractExperimentResults(Path resultsDir, String prefix) throws IOException {
        Map<String, List<ExperimentResult>> results = new TreeMap<>();
        Files.list(resultsDir).filter(dir -> Files.isDirectory(dir)).forEach(dir -> {
            String dirName = dir.getFileName().toString();
            results.put(dirName, new ArrayList<>());
            try {
                Files.list(dir).filter(f -> f.getFileName().toString().startsWith(prefix)).forEach(f -> {
                    try {
                        results.get(dirName).add(processContent(f.getFileName().toString(), Files.readAllLines(f)));
                    } catch (IOException ignored) {
                    }
                });
            } catch (IOException ignored) {
            }
        });
        return results;
    }

    private static ExperimentResult processContent(String resultName, List<String> content) {
        String[] parts = content.get(0).split(",");
        ExperimentResult result = new ExperimentResult(resultName, parts[1], parts[3], Double.parseDouble(parts[2]), new ArrayList<>());
        content.stream().skip(1).forEach(l -> {
            try {
                String[] smallParts = l.split(",");
                Event event = new Event(smallParts[1], smallParts[0], Double.parseDouble(smallParts[2]), Double.parseDouble(smallParts[3]));
                result.events.add(event);
            } catch (Exception e) {
                System.out.println("Error occurred while reading file [ " + resultName + " ] line [ " + l + " ]");
                throw e;
            }
        });
        return result;
    }
}
