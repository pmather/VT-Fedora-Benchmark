import datetime
import json
import pycurl
import pika
import requests
import sys, os
import time

from subprocess import call
from StringIO import StringIO


class RabbitMQClient(object):
    def __init__(self, connection, queuename):
        super(RabbitMQClient, self).__init__()
        self.queuename = queuename
        self.connection = connection
        self.channel = self.connection.channel()
        self.delivery_tag = None

    def downloadWorkItem(self):
        if self.delivery_tag:
            self.channel.basic_ack(self.delivery_tag)
        while True:
            method_frame, header_frame, body = self.channel.basic_get(self.queuename)
            if method_frame:
                self.delivery_tag = method_frame.delivery_tag
                if not body:
                    self._disconnect()
                return body

    def _disconnect(self):
        self.channel.basic_ack(self.delivery_tag)
        self.channel.close()


def readFedoraObject(fedoraurl):
    storage = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, fedoraurl)
    c.setopt(pycurl.HTTPHEADER, ["Accept: application/ld+json"])
    c.setopt(c.WRITEFUNCTION, storage.write)
    c.perform()
    c.close()
    content = storage.getvalue()

    return content


def updateFedoraBinary(updatestr, fedoraurl):
    binaryres = requests.patch(url=fedoraurl,
                               data=updatestr,
                               headers={'Content-Type': 'application/sparql-update'})

    return binaryres.text


def getFedoraSha(input):
    json_data = json.loads(input)
    sha_data = json_data[0]['http://www.loc.gov/premis/rdf/v1#hasMessageDigest'][0]['@id']

    return sha_data.replace('urn:sha1:', "")


def sha1OfFile(filepath):
    import hashlib
    with open(filepath, 'rb') as f:
        return hashlib.sha1(f.read()).hexdigest()


def main(queuename, connection):
    outputfile = open("experiment2_{}_results.csv".format(datetime.date.today()), "a")

    progress = []
    rabbitMq = RabbitMQClient(connection, queuename)

    start = str(datetime.datetime.now())
    tic = time.time()

    fileName = "temp.h5"
    while True:
        line = rabbitMq.downloadWorkItem()
        if not line:
            break
        fedoraobjurl = line.strip()
        fedorah5url = fedoraobjurl + "/h5"

        # read fedora object
        processing = time.time()
        content = readFedoraObject(fedorah5url + "/fcr:metadata")

        # read fedora sha
        fedora_sha = getFedoraSha(content)

        # download h5 file
        download = time.time()
        call("wget " + fedorah5url + " -O " + fileName, shell=True)
        downloadelapsed = time.time() - download
        progress.append("Download," + fedoraobjurl + "," + str(download) + "," + str(download + downloadelapsed))

        # create sha-1
        file_sha = sha1OfFile(fileName)

        # compare sha-1 and update fedora object
        if fedora_sha == file_sha:
            sharesult = "digest check passed at " + datetime.datetime.utcnow().isoformat() + 'Z'
        else:
            sharesult = "digest check failed at " + datetime.datetime.utcnow().isoformat() + 'Z'

        updatestr = "PREFIX dc: <http://purl.org/dc/elements/1.1/> INSERT { <> dc:provenance \"" + sharesult + "\" . } WHERE { } "
        progress.append("Processing," + fedoraobjurl + "," + str(processing) + "," + str(time.time() - downloadelapsed))

        ingestion = time.time()
        updateFedoraBinary(updatestr, fedoraobjurl)
        progress.append("Ingestion," + fedoraobjurl + "," + str(ingestion) + "," + str(time.time()))
        os.remove(fileName)

    duration = str(time.time() - tic)
    end = str(datetime.datetime.now())
    print duration
    progress.insert(0, "OVERALL EXECUTION," + start + "," + duration + "," + end)
    for line in progress:
        outputfile.write(line + "\n")
    outputfile.close()


if __name__ == "__main__":
    credentials = pika.PlainCredentials(sys.argv[3], sys.argv[4])
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=sys.argv[2], credentials=credentials))
    main(sys.argv[1], connection)
