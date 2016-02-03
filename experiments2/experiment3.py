import datetime
import h5py
import numpy as np
import pycurl
import sys,os
import time

from io import BytesIO
from socket import error as SocketError
from subprocess import call
from StringIO import StringIO
from time import ctime

def multiple_sum(array):
	rows = array.shape[0]
	cols = array.shape[1]

	out = np.zeros((rows, cols))

	for row in range(0, rows):
		out[row, :] = np.sum(array - array[row, :], 0)

	return out

def main():
	fedorurls = sys.argv[1]
	directory = os.path.dirname(fedorurls)
	
	outputfile = open(os.path.join(directory, "experiment3_{}_results.txt".format(datetime.date.today())), "a")

	outputfile.write(str(ctime()) + "\n")
	tic = time.time()

	filePath = os.path.join(directory, "temp.h5")
	with open(fedorurls) as f:
		lines = f.readlines()

	for line in lines:
		fedoraobjurl = line.strip()
		fedorah5url = fedoraobjurl + "/h5" 

		# download h5 file 
		call("wget " + fedorah5url + " -O " + filePath, shell=True)

		# read hdf5 file
		f = h5py.File(filePath, 'r')

		starttime = time.time()

		if f.keys()[0] is not None:
			datasets = f[f.keys()[0]]
			for channel in datasets.keys():
				a = datasets[channel]
				np.fft.fft(a)
				multiple_sum(a)
		endtime = time.time()
		# print str(endtime - starttime)

		os.remove(filePath)

	toc = time.time()
	print str(toc-tic)
	outputfile.write(str(toc-tic) + "\n")
	outputfile.write(str(ctime()) + "\n")
	outputfile.close()

if __name__ == "__main__": main()

