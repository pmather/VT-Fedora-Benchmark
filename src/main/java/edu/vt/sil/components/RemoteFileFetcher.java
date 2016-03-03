package edu.vt.sil.components;

import edu.vt.sil.administrator.AdministratorCommand;
import net.schmizz.sshj.SSHClient;
import net.schmizz.sshj.common.IOUtils;
import net.schmizz.sshj.connection.channel.direct.Session;
import net.schmizz.sshj.transport.verification.PromiscuousVerifier;
import net.schmizz.sshj.userauth.keyprovider.KeyProvider;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.Arrays;
import java.util.Objects;
import java.util.concurrent.TimeUnit;

/**
 * Author: dedocibula
 * Created on: 10.2.2016.
 */
public final class RemoteFileFetcher extends AbstractComponent {
    private static final String[] DEFAULT_SUFFIXES = new String[]{".csv", ".out"};

    private String userName;
    private KeyProvider keyProvider;

    private String[] hosts;
    private String remoteDir;
    private Path localDir;
    private Path tempDir;
    private String prefix;
    private String[] suffixes;

    public RemoteFileFetcher(String userName, String keyName) throws IOException {
        Objects.requireNonNull(userName);
        Objects.requireNonNull(keyName);

        this.userName = userName;
        try (SSHClient client = new SSHClient()) {
            keyProvider = client.loadKeys(Paths.get(System.getProperty("user.home")).resolve(".ssh").resolve(keyName).toString());
        }
    }

    @Override
    protected void prepare(AdministratorCommand command, String[] arguments) throws Exception {
        if (arguments.length != 4 && arguments.length != 5)
            throw new IllegalArgumentException(String.format("Invalid number of parameters. Expected: 4(5) - Received: %s",
                    arguments.length));

        if (arguments[0] == null)
            throw new IllegalArgumentException("Cannot use null hosts");
        hosts = arguments[0].split(",");
        if (Arrays.stream(hosts).anyMatch(h -> h == null || h.isEmpty()))
            throw new IllegalArgumentException("Cannot use null/empty host");

        // validation
        Paths.get(arguments[1]);
        remoteDir = arguments[1].endsWith("/") || arguments[1].endsWith("\\") ? arguments[1] : arguments[1] + "/";

        localDir = Paths.get(arguments[2]);
        if (Files.notExists(localDir) || !Files.isDirectory(localDir))
            throw new IllegalArgumentException(String.format("No directory: %s", localDir));

        tempDir = localDir.resolve("temp");
        Files.deleteIfExists(tempDir);
        Files.createDirectory(tempDir);

        prefix = arguments[3];
        if (prefix == null || prefix.isEmpty())
            throw new IllegalArgumentException("Cannot use null/empty prefix");

        if (arguments.length == 5) {
            String[] parts = arguments[4].split(",");
            suffixes = Arrays.stream(parts).filter(s -> s != null && !s.isEmpty()).toArray(String[]::new);
        } else {
            suffixes = DEFAULT_SUFFIXES;
        }
    }

    @Override
    protected void execute() throws Exception {
        int successfulHosts = 0;

        for (String host : hosts) {
            try (SSHClient client = new SSHClient()) {
                client.addHostKeyVerifier(new PromiscuousVerifier());
                client.connect(host);

                String[] files;
                client.authPublickey(userName, keyProvider);
                try (Session session = client.startSession()) {
                    final Session.Command cmd = session.exec(String.format("ls %s", remoteDir));
                    files = IOUtils.readFully(cmd.getInputStream()).toString().split("\n");
                    System.out.println(String.format("Host: %s, found: %s", host, Arrays.toString(files)));
                    cmd.join(5, TimeUnit.SECONDS);
                }

                String[] filteredFiles = Arrays.stream(files)
                        .filter(file -> file.startsWith(prefix) && Arrays.stream(suffixes).anyMatch(file::endsWith))
                        .toArray(String[]::new);

                if (!Arrays.equals(suffixes, DEFAULT_SUFFIXES) || Arrays.stream(filteredFiles).anyMatch(file -> file.endsWith(DEFAULT_SUFFIXES[0]))) {
                    for (String file : filteredFiles) {
                        client.newSCPFileTransfer().download(remoteDir + file, tempDir.resolve(host + "-" + file).toString());
                        System.out.println(String.format("%s downloaded", file));
                    }
                    successfulHosts++;
                }
            } catch (IOException e) {
                throw new Exception(String.format("Error occurred for host %s: %s", host, e));
            }
        }

        Files.move(tempDir, localDir.resolve(String.valueOf(successfulHosts)), StandardCopyOption.REPLACE_EXISTING);
    }

    @Override
    public String showLabel(AdministratorCommand command) {
        return "<comma-separated remote ips> <remote directory> <local destination> <files prefix> [<comma-separated files extensions>]";
    }
}
