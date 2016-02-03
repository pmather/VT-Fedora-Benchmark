import datetime
import json
import pycurl
import requests
import sys,os
import time

from io import BytesIO
from socket import error as SocketError
from subprocess import call
from StringIO import StringIO    
from time import ctime

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

	return binaryres.text;


def getFedoraSha(input):
	json_data = json.loads( input )
	sha_data = json_data[0]['http://www.loc.gov/premis/rdf/v1#hasMessageDigest'][0]['@id']

	return sha_data.replace('urn:sha1:', "")

def sha1OfFile(filepath):
	import hashlib
	with open(filepath, 'rb') as f:
		return hashlib.sha1(f.read()).hexdigest()

def main():
	fedorurls = sys.argv[1]
	directory = os.path.dirname(fedorurls)

	outputfile = open(os.path.join(directory, "experiment2_{}_results.txt".format(datetime.date.today())), "a")

	outputfile.write(str(ctime()) + "\n")
	tic = time.time()

	with open(fedorurls) as f:
		lines = f.readlines()

	filePath = os.path.join(directory, "temp.h5")
	for line in lines:
		fedoraobjurl = line.strip()
		fedorah5url = fedoraobjurl + "/h5" 
	
		# read fedora object
		content = readFedoraObject(fedorah5url + "/fcr:metadata")

		# read fedora sha
		fedora_sha = getFedoraSha(content)

		# download h5 file 
		call("wget " + fedorah5url + " -O " + filePath, shell=True)

		# create sha-1
		file_sha = sha1OfFile(filePath)

		# compare sha-1 and update fedora object
		if fedora_sha == file_sha:
			sharesult = "digest check passed at " + datetime.datetime.utcnow().isoformat() + 'Z' 
		else:
			sharesult = "digest check failed at " + datetime.datetime.utcnow().isoformat() + 'Z'
		
		updatestr = "PREFIX dc: <http://purl.org/dc/elements/1.1/> INSERT { <> dc:provenance \"" + sharesult + "\" . } WHERE { } "

		updateFedoraBinary(updatestr, fedoraobjurl)
		os.remove(filePath)

	toc = time.time()
	print str(toc-tic)
	outputfile.write(str(toc-tic) + "\n")
	outputfile.write(str(ctime()) + "\n")
	outputfile.close()

if __name__ == "__main__": main()
