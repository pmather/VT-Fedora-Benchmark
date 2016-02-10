package edu.vt.sil;

import net.schmizz.sshj.SSHClient;
import net.schmizz.sshj.common.IOUtils;
import net.schmizz.sshj.connection.channel.direct.Session;
import net.schmizz.sshj.userauth.keyprovider.KeyProvider;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.concurrent.TimeUnit;

/**
 * Author: dedocibula
 * Created on: 10.2.2016.
 */
public class RemoteFileFetcher {
    public static void main(String[] args) throws IOException {
        if (args.length != 4 && args.length != 5) {
            System.out.println("Please use parameters: <comma-separated remote ips> <private key> <results prefix> <destination> [<results suffix>]");
            System.exit(0);
        }

        String[] hosts = args[0].split(",");
        for (String host : hosts) {
            if (host == null || host.isEmpty()) {
                System.out.println("Cannot use null/empty host");
                System.exit(0);
            }
        }

        String keyName = args[1];
        if (keyName == null || keyName.isEmpty()) {
            System.out.println("Cannot use null/empty key");
            System.exit(0);
        }

        String prefix = args[2];
        if (prefix == null || prefix.isEmpty()) {
            System.out.println("Cannot use null/empty prefix");
            System.exit(0);
        }

        String destination = args[3];
        Path resultsDir = Paths.get(destination);
        if (Files.notExists(resultsDir, LinkOption.NOFOLLOW_LINKS) || !Files.isDirectory(resultsDir)) {
            System.out.println(String.format("No directory: %s", destination));
            System.exit(0);
        }

        Path dir = resultsDir.resolve(String.valueOf(hosts.length));
        if (Files.exists(dir)) {
            System.out.println(String.format("Please delete directory: %s", dir.toString()));
            System.exit(0);
        }
        Files.createDirectory(dir);

        String suffix = args.length == 5 ? args[4] : ".csv";

        fetchFiles(hosts, keyName, prefix, dir, suffix);
    }

    private static void fetchFiles(String[] hosts, String keyName, String prefix, Path resultsDir, String suffix) throws IOException {
        SSHClient client = new SSHClient();
        client.loadKnownHosts();

        KeyProvider keys = client.loadKeys(System.getProperty("user.home") + File.separator + ".ssh" + File.separator + keyName);

        for (String host : hosts) {
            client.connect(host);
            try {
                String[] files;
                client.authPublickey("cc", keys);
                try (Session session = client.startSession()) {
                    final Session.Command cmd = session.exec("ls /vt-sil/experiments");
                    files = IOUtils.readFully(cmd.getInputStream()).toString().split("\n");
                    System.out.println(Arrays.toString(files));
                    cmd.join(5, TimeUnit.SECONDS);
                    System.out.println("\n** exit status: " + cmd.getExitStatus());
                }

                for (String file : files) {
                    if (file.startsWith(prefix) && file.endsWith(suffix)) {
                        client.newSCPFileTransfer().download("/vt-sil/experiments/" + file, resultsDir.resolve(host + "-" + file).toString());
                        System.out.println(file + " downloaded");
                    }
                }
            } finally {
                client.disconnect();
            }
        }
    }
}
