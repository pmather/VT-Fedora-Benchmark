import datetime
import h5py
import numpy as np
import sys, os
import time

from subprocess import call


def multiple_sum(array):
    rows = array.shape[0]
    cols = array.shape[1]

    out = np.zeros((rows, cols))

    for row in range(0, rows):
        out[row, :] = np.sum(array - array[row, :], 0)

    return out


def run(work_item_client):
    output_file = open("experiment3_{}_results.csv".format(datetime.date.today()), "a")

    progress = []

    start = str(datetime.datetime.now())
    tic = time.time()

    file_name = "temp.h5"
    # obtain work items from work_item_client (see commons.py for implementations)
    for work_item in work_item_client.get_work_item():
        fedora_obj_url = work_item.strip()
        fedora_h5_url = fedora_obj_url + "/h5"

        # download h5 file
        download = time.time()
        call("wget -nv " + fedora_h5_url + " -O " + file_name, shell=True)
        progress.append("Download," + fedora_obj_url + "," + str(download) + "," + str(time.time()))

        # read hdf5 file
        processing = time.time()
        f = h5py.File(file_name, 'r')

        if f.keys()[0] is not None:
            data_sets = f[f.keys()[0]]
            for channel in data_sets.keys():
                a = data_sets[channel]
                np.fft.fft(a)
                multiple_sum(a)
        progress.append("Processing," + fedora_obj_url + "," + str(processing) + "," + str(time.time()))

        os.remove(file_name)

    duration = str(time.time() - tic)
    end = str(datetime.datetime.now())
    print duration
    progress.insert(0, "OVERALL EXECUTION," + start + "," + duration + "," + end)
    for line in progress:
        output_file.write(line + "\n")
    output_file.close()


if __name__ == "__main__":
    fedora_urls_filename = sys.argv[1]

    from commons import FileSystemClient

    run(FileSystemClient(fedora_urls_filename))
