import pycurl
import os
import sys

def deleteFedoraObject(fedoraurl):
	c = pycurl.Curl()
	c.setopt(c.URL, fedoraurl)
	c.setopt(c.CUSTOMREQUEST, "DELETE")
	c.perform()
	c.close()

def main():
	fedoraurls = sys.argv[1]

	with open(fedoraurls) as f:
		lines = f.readlines()

	for line in lines:
		fileurl = line.strip()

		print "Deleting " + fileurl
		deleteFedoraObject(fileurl)
		print "Deletion successful"

	for file in os.listdir("."):
		if file.endswith(".csv"):
			os.remove(file)
	os.remove(fedoraurls)

if __name__ == "__main__": main()