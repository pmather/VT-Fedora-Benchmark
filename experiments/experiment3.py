import datetime
import h5py
import numpy as np
import sys,os
import time

from subprocess import call

def multiple_sum(array):
	rows = array.shape[0]
	cols = array.shape[1]

	out = np.zeros((rows, cols))

	for row in range(0, rows):
		out[row, :] = np.sum(array - array[row, :], 0)

	return out

def main():
	fedorurls = sys.argv[1]
	
	outputfile = open("experiment3_{}_results.csv".format(datetime.date.today()), "a")

	progress = []

	start = str(datetime.datetime.now())
	tic = time.time()

	fileName = "temp.h5"
	with open(fedorurls) as f:
		lines = f.readlines()

	for line in lines:
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

if __name__ == "__main__": main()

