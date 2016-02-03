import datetime
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
	# use current dir if not specified
	h5dir = sys.argv[2] if len(sys.argv) > 2 else "."

	outputfile = open(os.path.join(h5dir, "experiment1_{}_results.txt".format(datetime.date.today())), "a")
	urlfile = open(os.path.join(h5dir, "fedoraurls.txt"), "a")

	outputfile.write(str(ctime()) + "\n")
	tic = time.time()

	lines = []
	for file in os.listdir(h5dir):
		if file.endswith(".h5"):
			lines.append(file)
	
	for line in lines:
		fileName = line.strip()
		filePath = os.path.join(h5dir, fileName)

		# read hdf5 file
		f = h5py.File(filePath, 'r')

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
			call("~/fits-0.9.0/fits.sh -i " + filePath + " > " + filePath + "_fits.xml", shell=True)

			# read fits xml
			fitsxml = open(filePath + "_fits.xml", 'r').read()
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
				createFedoraBinary(filePath, fileurl)
				urlfile.write(objecturl+"\n")
				print fileurl

		os.remove(filePath)
		os.remove(filePath + "_fits.xml")

	toc = time.time()
	print str(toc-tic)
	outputfile.write(str(toc-tic) + "\n")
	outputfile.write(str(ctime()) + "\n")
	outputfile.close()
	urlfile.close()


if __name__ == "__main__": main()
