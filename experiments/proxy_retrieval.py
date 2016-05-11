import datetime
import sys, os
import time

from subprocess import call


def run(work_item_client):
    output_file = open("experiment_proxy_retrieval_{}_results.csv".format(datetime.date.today()), "a")

    progress = []

    start = str(datetime.datetime.now())
    tic = time.time()

    file_name = "temp.h5"
    while True:
        # obtain work item from work_item_client (see commons.py for implementations)
        work_item = work_item_client.get_work_item()
        if not work_item:
            break
        fedora_obj_url = work_item.strip()
        fedora_h5_url = fedora_obj_url + "/h5"

        # download hdf5 file
        download = time.time()

        # TODO retrieval logic here

        download_elapsed = time.time() - download
        progress.append("Download," + fedora_obj_url + "," + str(download) + "," + str(download + download_elapsed))

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
