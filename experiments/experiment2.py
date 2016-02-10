import datetime
import json
import pycurl
import requests
import sys,os
import time

from subprocess import call
from StringIO import StringIO

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

	outputfile = open("experiment2_{}_results.csv".format(datetime.date.today()), "a")

	progress = []

	start = str(datetime.datetime.now())
	tic = time.time()

	with open(fedorurls) as f:
		lines = f.readlines()

	fileName = "temp.h5"
	for line in lines:
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

if __name__ == "__main__": main()
