import datetime
import pycurl
import sys, os
import time

from socket import error as SocketError
from StringIO import StringIO


# create fedora object
def create_fedora_object(rdf_data, fedora_url, filename):
    storage = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, "{}/{}".format(fedora_url, filename[:-3]))
    c.setopt(pycurl.CUSTOMREQUEST, "PUT")
    c.setopt(pycurl.HTTPHEADER, ["Content-type: text/turtle"])
    c.setopt(c.POSTFIELDS, rdf_data)
    c.setopt(c.WRITEFUNCTION, storage.write)
    c.perform()
    c.close()
    content = storage.getvalue()

    return content


# create fedora binary
def create_fedora_binary(file_path, fedora_url):
    storage = StringIO()
    f = open(file_path, "rb")
    fs = os.path.getsize(file_path)
    c = pycurl.Curl()
    c.setopt(c.URL, fedora_url)
    c.setopt(c.PUT, 1)
    c.setopt(c.READDATA, f)
    c.setopt(c.INFILESIZE, int(fs))
    c.setopt(pycurl.HTTPHEADER, ["Content-type: text/xml"])
    c.setopt(c.WRITEFUNCTION, storage.write)
    c.perform()
    c.close()
    content = storage.getvalue()

    return content


def run(fedora_url, remote_file_downloader, work_item_client):
    output_file = open("experiment_full_ingestion_{}_results.csv".format(datetime.date.today()), "a")
    url_file = open("fedoraurls.txt", "a")

    progress = []

    start = str(datetime.datetime.now())
    tic = time.time()

    while True:
        # obtain work item from work_item_client (see commons.py for implementations)
        work_item = work_item_client.get_work_item()
        if not work_item:
            break
        file_name = work_item.strip()

        # download remote file from remote storage (see commons.py for implementations)
        download = time.time()
        remote_file_downloader.download_from_storage(file_name, file_name)
        progress.append("Download," + file_name + "," + str(download) + "," + str(time.time()))

        # create Fedora object
        rdf_data = 'PREFIX dc: <http://purl.org/dc/elements/1.1/> <> dc:title "' + file_name + '" . ' + \
                   '<> dc:source "' + remote_file_downloader.get_remote_url(file_name) + '"'

        ingestion = time.time()
        object_url = ""
        for x in xrange(0, 5):
            try:
                object_url = create_fedora_object(rdf_data, fedora_url, file_name)
                break
            except SocketError as e:
                if x == 4:
                    raise SocketError("retry 5 times still failed in fedora" + str(e.errno))
                pass

        # create Fedora binary
        if len(object_url) > 0:
            file_url = object_url + "/h5"
            create_fedora_binary(file_name, file_url)
            progress.append("Ingestion," + file_name + "," + str(ingestion) + "," + str(time.time()))
            url_file.write(object_url + "\n")
            print file_url

        # cleanup
        os.remove(file_name)

    duration = str(time.time() - tic)
    end = str(datetime.datetime.now())
    print duration
    progress.insert(0, "OVERALL EXECUTION," + start + "," + duration + "," + end)
    for line in progress:
        output_file.write(line + "\n")
    output_file.close()
    url_file.close()


if __name__ == "__main__":
    fedoraurl = sys.argv[1]
    google_drive_dir = sys.argv[2]
    data_set_filename = sys.argv[3]

    from commons import GoogleDriveDownloader, FileSystemClient

    run(fedoraurl, GoogleDriveDownloader(google_drive_dir), FileSystemClient(data_set_filename))
