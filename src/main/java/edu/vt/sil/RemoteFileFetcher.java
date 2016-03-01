package edu.vt.sil;

import net.schmizz.sshj.SSHClient;
import net.schmizz.sshj.common.IOUtils;
import net.schmizz.sshj.connection.channel.direct.Session;
import net.schmizz.sshj.transport.verification.PromiscuousVerifier;
import net.schmizz.sshj.userauth.keyprovider.KeyProvider;

import java.io.File;
import java.io.IOException;
import java.nio.file.*;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.Date;
import java.util.concurrent.TimeUnit;

/**
 * Author: dedocibula
 * Created on: 10.2.2016.
 */
public class RemoteFileFetcher {
    public static void main(String[] args) throws IOException {
        if (args.length != 4 && args.length != 5) {
            System.out.println("Please use parameters: <comma-separated remote ips> <private key> <results prefix> <destination> [<results suffix>]");
            return;
        }

        String[] hosts = args[0].split(",");
        for (String host : hosts) {
            if (host == null || host.isEmpty()) {
                System.out.println("Cannot use null/empty host");
                return;
            }
        }

        String keyName = args[1];
        if (keyName == null || keyName.isEmpty()) {
            System.out.println("Cannot use null/empty key");
            return;
        }

        String prefix = args[2];
        if (prefix == null || prefix.isEmpty()) {
            System.out.println("Cannot use null/empty prefix");
            return;
        }

        String destination = args[3];
        Path resultsDir = Paths.get(destination);
        if (Files.notExists(resultsDir, LinkOption.NOFOLLOW_LINKS) || !Files.isDirectory(resultsDir)) {
            System.out.println(String.format("No directory: %s", destination));
            return;
        }
        
        KeyProvider keys;
        try {
            keys = new SSHClient().loadKeys(System.getProperty("user.home") + File.separator + ".ssh" + File.separator + keyName);
        } catch (IOException e) {
            e.printStackTrace();
            System.out.println("Couldn't load public keys");
            return;
        }

        Path todayResultsDir = resultsDir.resolve(new SimpleDateFormat("yyyy-MM-dd").format(new Date()));
        if (Files.notExists(todayResultsDir))
            Files.createDirectory(todayResultsDir);

        Path tempDir = todayResultsDir.resolve("temp");
        if (Files.exists(tempDir)) {
            System.out.println(String.format("Please delete directory: %s", tempDir.toString()));
            return;
        }
        Files.createDirectory(tempDir);

        String suffix = args.length == 5 ? args[4] : ".csv";

        int successfulHosts = fetchFiles(hosts, keys, prefix, tempDir, suffix);

        Files.move(tempDir, todayResultsDir.resolve(String.valueOf(successfulHosts)), StandardCopyOption.REPLACE_EXISTING);
    }

    private static int fetchFiles(String[] hosts, KeyProvider keys, String prefix, Path resultsDir, String suffix) {
        int successfulHosts = 0;

        for (String host : hosts) {
            SSHClient client = new SSHClient();
            try {
                client.addHostKeyVerifier(new PromiscuousVerifier());
                client.connect(host);

                String[] files;
                client.authPublickey("cc", keys);
                try (Session session = client.startSession()) {
                    final Session.Command cmd = session.exec("ls /vt-sil/experiments");
                    files = IOUtils.readFully(cmd.getInputStream()).toString().split("\n");
                    System.out.println(Arrays.toString(files));
                    cmd.join(5, TimeUnit.SECONDS);
                    System.out.println("\n** exit status: " + cmd.getExitStatus());
                }

                boolean resultsFound = false;
                for (String file : files) {
                    if (file.startsWith(prefix) && file.endsWith(suffix)) {
                        client.newSCPFileTransfer().download("/vt-sil/experiments/" + file, resultsDir.resolve(host + "-" + file).toString());
                        System.out.println(file + " downloaded");
                        resultsFound = true;
                    }
                }

                if (resultsFound)
                    successfulHosts++;
            } catch (IOException e) {
                e.printStackTrace();
                System.out.println("Error occurred for host [ " + host + " ]");
            } finally {
                try {
                    if (client.isConnected())
                        client.disconnect();
                } catch (IOException ignored) {
                }
            }
        }

        return successfulHosts;
    }
}
