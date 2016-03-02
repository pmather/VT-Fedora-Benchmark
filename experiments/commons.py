from urllib import urlretrieve

class RemoteFileDownloader(object):
    def __init__(self):
        super(RemoteFileDownloader, self).__init__()

    def download_from_storage(self, filename):
        raise NotImplementedError

class GoogleDriveDownloader(RemoteFileDownloader):
    def __init__(self, google_drive_dir):
        super(GoogleDriveDownloader, self).__init__()
        self.url = "https://googledrive.com/host/{}/".format(google_drive_dir)

    def download_from_storage(self, filename):
        urlretrieve(self.url + filename, filename)


class WorkItemClient(object):
    def __init__(self):
        super(WorkItemClient, self).__init__()

    def get_work_item(self):
        raise NotImplementedError


class FileSystemClient(WorkItemClient):
    def __init__(self, input_file):
        super(FileSystemClient, self).__init__()
        with open(input_file) as f:
            self.lines = f.readlines()

    def get_work_item(self):
        for line in self.lines:
            yield line


class RabbitMQClient(WorkItemClient):
    def __init__(self, connection, queue_name):
        super(RabbitMQClient, self).__init__()
        self.queue_name = queue_name
        self.connection = connection
        self.channel = self.connection.channel()
        self.delivery_tag = None
        self.channel_open = True

    def get_work_item(self):
        if self.delivery_tag:
            self.channel.basic_ack(self.delivery_tag)
        while self.channel_open:
            method_frame, header_frame, body = self.channel.basic_get(self.queue_name)
            if method_frame:
                self.delivery_tag = method_frame.delivery_tag
                if not body:
                    self._disconnect()
                return body

    def _disconnect(self):
        self.channel.basic_ack(self.delivery_tag)
        self.channel.close()
        self.delivery_tag = None
        self.channel_open = False