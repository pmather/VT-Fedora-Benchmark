import datetime
import boto3
import pika
import h5py
import pycurl
import sys, os
import time
import xmltodict

from socket import error as SocketError
from subprocess import call
from StringIO import StringIO


class RabbitMQClient(object):
    def __init__(self, rabbitmqurl, username, password, queuename):
        super(RabbitMQClient, self).__init__()
        self.queuename = queuename
        credentials = pika.PlainCredentials(username, password)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmqurl, credentials=credentials))
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
        self.connection.close()


def downloadFromS3(filename):
    s3 = boto3.client('s3')
    s3.download_file('sebdata', filename, filename)


def downloadFromGDrive(gdrivedir, filename):
    url = "https://googledrive.com/host/{}/{}".format(gdrivedir, filename)
    call("wget " + url + " -O " + filename, shell=True)


def createFedoraObject(rdfdata, fedoraurl, filename):
    storage = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, "{}/{}".format(fedoraurl, filename[:-3]))
    c.setopt(pycurl.CUSTOMREQUEST, "PUT")
    c.setopt(pycurl.HTTPHEADER, ["Content-type: text/turtle"])
    c.setopt(c.POSTFIELDS, rdfdata)
    c.setopt(c.WRITEFUNCTION, storage.write)
    c.perform()
    c.close()
    content = storage.getvalue()

    return content


# create fedora binary
def createFedoraBinary(filepath, fedoraurl):
    storage = StringIO()
    f = open(filepath, "rb")
    fs = os.path.getsize(filepath)
    c = pycurl.Curl()
    c.setopt(c.URL, fedoraurl)
    c.setopt(c.PUT, 1)
    c.setopt(c.READDATA, f)
    c.setopt(c.INFILESIZE, int(fs))
    c.setopt(pycurl.HTTPHEADER, ["Content-type: text/xml"])
    c.setopt(c.WRITEFUNCTION, storage.write)
    c.perform()
    c.close()
    content = storage.getvalue()

    return content


def main(fedoraurl, gdriveDir, queuename, rabbitmqurl, username, password):
    outputfile = open("experiment1_{}_results.csv".format(datetime.date.today()), "a")
    urlfile = open("fedoraurls.txt", "a")

    progress = []
    rabbitMq = RabbitMQClient(rabbitmqurl, username, password, queuename)

    start = str(datetime.datetime.now())
    tic = time.time()

    while True:
        line = rabbitMq.downloadWorkItem()
        if not line:
            break
        fileName = line.strip()

        # downloadFromS3(fileName)
        download = time.time()
        downloadFromGDrive(gdriveDir, fileName)
        progress.append("Download," + fileName + "," + str(download) + "," + str(time.time()))

        # read hdf5 file
        f = h5py.File(fileName, 'r')

        processing = time.time()
        if f.keys()[0] is not None:
            datasets = f[f.keys()[0]]
            channel_str = ""
            c = 0
            for channel in datasets.keys():
                if c == len(datasets.keys()) - 1:
                    channel_str = channel_str + '<> dc:coverage "' + channel + '" '
                else:
                    channel_str = channel_str + '<> dc:coverage "' + channel + '" . '
                c += 1

            # run fits program
            call("fits-0.9.0/fits.sh -i " + fileName + " > " + fileName + "_fits.xml", shell=True)

            # read fits xml
            fitsxml = open(fileName + "_fits.xml", 'r').read()
            result = xmltodict.parse(fitsxml)
            description = result['fits']['identification']['identity'][0]['@format']
            format = result['fits']['identification']['identity'][0]['@mimetype']

            fits_str = '<> dc:description "' + description + '" . ' + '<> dc:format "' + format + '" . '

            # Create Fedora object
            rdfdata = 'PREFIX dc: <http://purl.org/dc/elements/1.1/> <> dc:title "' + fileName + '" . ' + \
                      fits_str + channel_str
            progress.append("Processing," + fileName + "," + str(processing) + "," + str(time.time()))

            ingestion = time.time()
            objecturl = ""
            for x in xrange(0, 5):
                try:
                    objecturl = createFedoraObject(rdfdata, fedoraurl, fileName)
                    break
                except SocketError as e:
                    if x == 4:
                        raise SocketError("retry 5 times still failed in fedora" + str(e.errno))
                    pass

            # Create Fedora binary
            if len(objecturl) > 0:
                fileurl = objecturl + "/h5"
                createFedoraBinary(fileName, fileurl)
                progress.append("Ingestion," + fileName + "," + str(ingestion) + "," + str(time.time()))
                urlfile.write(objecturl + "\n")
                print fileurl

        os.remove(fileName)
        os.remove(fileName + "_fits.xml")

    duration = str(time.time() - tic)
    end = str(datetime.datetime.now())
    print duration
    progress.insert(0, "OVERALL EXECUTION," + start + "," + duration + "," + end)
    for line in progress:
        outputfile.write(line + "\n")
    outputfile.close()
    urlfile.close()


if __name__ == "__main__": main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
