package edu.vt.sil.components;

import edu.vt.sil.administrator.Command;

/**
 * Author: dedocibula
 * Created on: 29.2.2016.
 */
public interface Component {
    String showLabel();

    void handleCommand(Command command, String[] arguments) throws Exception;
}
