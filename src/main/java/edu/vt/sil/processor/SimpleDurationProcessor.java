package edu.vt.sil.processor;

import edu.vt.sil.entities.ExperimentResult;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

/**
 * Author: dedocibula
 * Created on: 9.2.2016.
 */
public class SimpleDurationProcessor implements Processor {
    @Override
    public String getDescription() {
        return "Experiment Duration (sec)";
    }

    @Override
    public String getHeaders() {
        return "Machines,Min,Average,Max";
    }

    @Override
    public List<String> process(Map<String, Map<String, ExperimentResult>> results) {
        List<String> processed = new ArrayList<>();
        for (String machine : results.keySet()) {
            double min = Double.MAX_VALUE;
            double max = Double.MIN_VALUE;
            double average = 0;
            for (ExperimentResult result : results.get(machine).values()) {
                min = Math.min(min, result.duration);
                max = Math.max(min, result.duration);
                average += result.duration;
            }
            average /= results.get(machine).size();
            processed.add(String.format("%s,%s,%s,%s", machine, min, average, max));
        }
        Collections.sort(processed);
        return processed;
    }
}
