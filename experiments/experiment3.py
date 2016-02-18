import datetime
import h5py
import numpy as np
import pika
import sys, os
import time

from subprocess import call


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


def multiple_sum(array):
    rows = array.shape[0]
    cols = array.shape[1]

    out = np.zeros((rows, cols))

    for row in range(0, rows):
        out[row, :] = np.sum(array - array[row, :], 0)

    return out


def main(queuename, rabbitmqurl, username, password):
    outputfile = open("experiment3_{}_results.csv".format(datetime.date.today()), "a")

    progress = []
    rabbitMq = RabbitMQClient(rabbitmqurl, username, password, queuename)

    start = str(datetime.datetime.now())
    tic = time.time()

    fileName = "temp.h5"
    while True:
        line = rabbitMq.downloadWorkItem()
        if not line:
            break
        fedoraobjurl = line.strip()
        fedorah5url = fedoraobjurl + "/h5"

        # download h5 file
        download = time.time()
        call("wget " + fedorah5url + " -O " + fileName, shell=True)
        progress.append("Download," + fedoraobjurl + "," + str(download) + "," + str(time.time()))

        # read hdf5 file
        processing = time.time()
        f = h5py.File(fileName, 'r')

        if f.keys()[0] is not None:
            datasets = f[f.keys()[0]]
            for channel in datasets.keys():
                a = datasets[channel]
                np.fft.fft(a)
                multiple_sum(a)
        progress.append("Processing," + fedoraobjurl + "," + str(processing) + "," + str(time.time()))
        # print str(endtime - starttime)

        os.remove(fileName)

    duration = str(time.time() - tic)
    end = str(datetime.datetime.now())
    print duration
    progress.insert(0, "OVERALL EXECUTION," + start + "," + duration + "," + end)
    for line in progress:
        outputfile.write(line + "\n")
    outputfile.close()


if __name__ == "__main__": main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
