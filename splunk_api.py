#!/usr/bin/env python3
import urllib.parse
import httplib2
import time
from time import localtime,strftime
from xml.dom import minidom
import json
import http.client
import ssl
import base64
from http.client import HTTPSConnection
import pprint,sys
from mailsys import MailTool

host_port = 'some_server:8089'
baseurl = 'https://'+ host_port

username = sys.argv[1]
password = sys.argv[2]

#Step 1: Get a session key
myhttp  = httplib2.Http(".cache", disable_ssl_certificate_validation=True)

servercontent = myhttp.request(baseurl + '/services/auth/login', 'POST',
headers={}, body=urllib.parse.urlencode({'username':username, 'password':password}))[1]
sessionkey = minidom.parseString(servercontent).getElementsByTagName('sessionKey')[0].childNodes[0].nodeValue
print("====>sessionkey:  %s  <====" % sessionkey)

#Step 2: Create a search job
# here is where you actually put your query index=  or sourcetype etc
searchquery = 'source="/var/log/apt/history.log" host="bf1b3d8b459a" sourcetype="test_src_type"'


#searchquery = 'index="_internal" | head 100'
if not searchquery.startswith('search'):
    searchquery = 'search ' + searchquery

searchjob = myhttp.request(baseurl + '/services/search/jobs','POST',
headers={'Authorization': 'Splunk %s' % sessionkey},body=urllib.parse.urlencode({'search': searchquery}))[1]
sid = minidom.parseString(searchjob).getElementsByTagName('sid')[0].childNodes[0].nodeValue
print("====>sid:  %s  <====" % sid)


#common get method
def do_get(uri_path, jsonIn=False):
#Step 3: Get the search status
    raw_base_url = host_port
    conn = http.client.HTTPSConnection(raw_base_url ,context = ssl._create_unverified_context() )
    user_pass = username + ':' + password
    auth = base64.b64encode(user_pass.encode())
    headers = {"Authorization": "Basic " + auth.decode()}
    print("\n", raw_base_url)
    print("\n", uri_path)
    conn.request("GET",uri_path , headers=headers)
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    print(data)
    if jsonIn == True :
            print("----")
        data_ready = json.loads(data)
        with open("/tmp/report.txt", "w") as out_file:
            out_file.write(str(data_ready['results']))
        out_file.close()
    else:
        data = response.read().decode('utf-8')
        print(response.status, response.reason)
        print(data)


#Step 4: Get the search results
servicessearchstatusstr = '/services/search/jobs/%s/' % sid
services_search_results_str = '/services/search/jobs/%s/results?output_mode=json&count=0' % sid
do_get(servicessearchstatusstr)
time.sleep(10)
do_get(services_search_results_str, True)
to = 'someemail@somewhere.com'
mailTool = MailTool(to)
mailTool.send()
