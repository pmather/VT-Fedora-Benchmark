import datetime
import boto3
import h5py
import pycurl
import sys,os
import time
import xmltodict

from io import BytesIO
from socket import error as SocketError
from subprocess import call
from StringIO import StringIO    
from time import ctime

def downloadFromS3(filename):
	s3 = boto3.client('s3')
	s3.download_file('sebdata', filename, filename)

def downloadFromGDrive(gdrivedir, filename):
	url = "https://googledrive.com/host/{}/{}".format(gdrivedir, filename)
	call("wget " + url + " -O " + filename, shell=True)

def createFedoraObject(rdfdata, fedoraurl):	
	storage = StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL, fedoraurl)
	c.setopt(c.POST, 1)
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


def main():
	fedoraurl = sys.argv[1]
	datasetfilename = sys.argv[2]
	gdriveDir = sys.argv[3]

	outputfile = open("experiment1_{}_results.txt".format(datetime.date.today()), "a")
	urlfile = open("fedoraurls.txt", "a")

	outputfile.write(str(ctime()) + "\n")
	tic = time.time()

	with open(datasetfilename) as f:
		lines = f.readlines()
	
	for line in lines:
		fileName = line.strip()

		# downloadFromS3(fileName)
		downloadFromGDrive(gdriveDir, fileName)

		# read hdf5 file
		f = h5py.File(fileName, 'r')

		if f.keys()[0] is not None:
			datasets = f[f.keys()[0]]
			channel_str = ""
			c = 0
			for channel in datasets.keys():
				if c == len(datasets.keys()) - 1:
					channel_str = channel_str + '<> dc:coverage "'+ channel +'" '
				else:
					channel_str = channel_str + '<> dc:coverage "'+ channel +'" . '
				c += 1

			# run fits program 
			call("~/fits-0.9.0/fits.sh -i " + fileName + " > " + fileName + "_fits.xml", shell=True)

			# read fits xml
			fitsxml = open(fileName + "_fits.xml", 'r').read()
			result = xmltodict.parse( fitsxml )
			description = result['fits']['identification']['identity'][0]['@format']
			format = result['fits']['identification']['identity'][0]['@mimetype']

			fits_str = '<> dc:description "' + description + '" . ' + '<> dc:format "' + format + '" . '  		

			# Create Fedora object
			rdfdata = 'PREFIX dc: <http://purl.org/dc/elements/1.1/> <> dc:title "'+ fileName +'" . ' + \
				fits_str + channel_str

			objecturl = ""
			for x in xrange(0, 5):
				try:
					objecturl = createFedoraObject(rdfdata, fedoraurl)
					break
				except SocketError as e:
					if x == 4:
						raise SocketError("retry 5 times still failed in fedora" + str(e.errno))
					pass
			
			# Create Fedora binary
			if len(objecturl) > 0:
				fileurl = objecturl + "/h5"
				createFedoraBinary(fileName, fileurl)
				urlfile.write(objecturl+"\n")
				print fileurl

		os.remove(fileName)
		os.remove(fileName + "_fits.xml")

	toc = time.time()
	print str(toc-tic)
	outputfile.write(str(toc-tic) + "\n")
	outputfile.write(str(ctime()) + "\n")
	outputfile.close()
	urlfile.close()


if __name__ == "__main__": main()
