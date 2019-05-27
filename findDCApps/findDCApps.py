#https://github.com/atlasadwivedi/scripts/tree/master/findDCApps

#Script to find if an app installed on local atlassian host product has any Data-center app available in atlassian marketplace

import os, sys
sys.path.append(os.path.dirname("./requests"))
import requests,json
import argparse

parser = argparse.ArgumentParser()
# add long and short argument
parser.add_argument("--user", "-u", help="Admin user name")
parser.add_argument("--password", "-p", help="Admin password")
parser.add_argument("--host", "-host", help="Host")
parser.add_argument("--port", "-port", help="Port")
args = parser.parse_args()
nDash = 80
#localhost url for the rest API for fetching installed plugins
url = "http://{}:{}/upm/rest/plugins/1.0/"
user = "admin"
password = "admin"
host = "localhost"
port = 3990


if args.user:  
    user = args.user
if args.password:
	password = args.password
if args.host:
	host = args.host
if args.port:
	port = args.port

url = url.format(host,port)
print "url == "+ url

#query local host product for installed apps

try:
	response = requests.get(url, auth=(user,password))
except Exception as e:
	print e 
	print "ERROR : Unable to connect to host ptoduct... exiting... please check command line paremeters"
	exit()
if response.status_code == 200:
	installedApps = json.loads(response.content)
	print "loads"
else:
	print "ERROR : Unable to connect to host ptoduct... exiting... please check command line paremeters"
	exit()

plugins = []
count = 0
print "-"*nDash
print "Apps installed on this instance..."
print "-"*nDash

#filter user installed  and language plugins

for item in installedApps["plugins"]:
    if item["userInstalled"] and not item["key"].__contains__("tac.jira software.languages") :
        print "App Name : " + item["name"] + " \nApp Key  : " + item["key"]+"\n"
        plugins.append(item)
        count=count+1
print "-"*nDash
print "Total number of User installed apps = "+ str(count)
print "-"*nDash


#for every plugin query atlassian marketplace /versions API for available deployment options

url = "https://marketplace.atlassian.com/rest/2/addons/{}/versions?limit=50&includePrivate=false"
dcVersionAvailable = []
dcVersionNotAvailable = []
print "-"*nDash
print "Querying Atlassian marketplace for availability of DC versions of the {} apps...".format(count)
print "-"*nDash

for item in plugins:
	print url.format(item["key"])
	try:
		response = requests.get(url.format(item["key"]))
	except Exception as e:
		print e 
		print "\n ERROR : Unable to connect to atlassian marketplace ... exiting... please check if you have active intenet connection to reach to https://marketplace.atlassian.com/ "
		exit()
	if response:
		print "Apps is available on marketplace"
		response = response.json()
		available = False 
		for version in response["_embedded"]["versions"]:
			if "dataCenterStatus" in version["deployment"]:
				available = version["deployment"]["dataCenterStatus"] == "compatible"
				break
		if available:
			dcVersionAvailable.append("App Name : " + item["name"] + "\nApp Key  : " + item["key"])
		else:
			dcVersionNotAvailable.append("App Name : " + item["name"] + "\nApp Key  : " + item["key"])
	else:
		print "Apps not available on marketplace"
	print "\n"
print "-"*nDash

print "-"*nDash
print "Apps which doesn't have DC version available..."
print "-"*nDash
for item in dcVersionNotAvailable:
	print item + "\n"
print "-"*nDash

print "-"*nDash
print "Apps which have DC version available..."
print "-"*nDash
for item in dcVersionAvailable:
	print item+ "\n"
print "-"*nDash
