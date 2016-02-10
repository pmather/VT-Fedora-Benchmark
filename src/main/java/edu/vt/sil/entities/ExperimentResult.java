package edu.vt.sil.entities;

import java.util.List;

/**
 * Author: dedocibula
 * Created on: 9.2.2016.
 */
public class ExperimentResult {
    public final String start;
    public final String end;
    public final double duration;
    public final List<Event> events;

    public ExperimentResult(String start, String end, double duration, List<Event> events) {
        this.start = start;
        this.end = end;
        this.duration = duration;
        this.events = events;
    }
}
