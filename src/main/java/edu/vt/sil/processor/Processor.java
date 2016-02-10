package edu.vt.sil.processor;

import edu.vt.sil.entities.ExperimentResult;

import java.util.List;
import java.util.Map;

/**
 * Author: dedocibula
 * Created on: 9.2.2016.
 */
public interface Processor {
    String getDescription();

    String getHeaders();

    List<String> process(Map<String, Map<String, ExperimentResult>> results);
}
