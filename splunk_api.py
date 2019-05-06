#!/usr/bin/env python3

import urllib3
import httplib2
import time
from time import localtime,strftime
from xml.dom import minidom
import json
import http.client
import ssl
import base64
from http.client import HTTPSConnection
import pprint


#you need to update this to point to your url notice the port is very import
main ="localhost:32779"
baseurl = 'https://'+main

username = 'your_user_name'
password = 'you_password'


#Step 1: Get a session key
myhttp  = httplib2.Http(".cache", disable_ssl_certificate_validation=True)
#resp, content = h.request("https://site/whose/certificate/is/bad/", "GET")

servercontent = myhttp.request(baseurl + '/services/auth/login', 'POST',
headers={}, body=urllib3.request.urlencode({'username':username, 'password':password}))[1]
sessionkey = minidom.parseString(servercontent).getElementsByTagName('sessionKey')[0].childNodes[0].nodeValue
print("====>sessionkey:  %s  <====" % sessionkey)

#Step 2: Create a search job

# here is where you actually put your query index=  or sourcetype etc
searchquery = 'source="/var/log/apt/history.log" host="bf1b3d8b459a" sourcetype="test_src_type"'

#searchquery = 'index="_internal" | head 100'
if not searchquery.startswith('search'):
    searchquery = 'search ' + searchquery

searchjob = myhttp.request(baseurl + '/services/search/jobs','POST',
headers={'Authorization': 'Splunk %s' % sessionkey},body=urllib3.request.urlencode({'search': searchquery}))[1]
sid = minidom.parseString(searchjob).getElementsByTagName('sid')[0].childNodes[0].nodeValue
print("====>sid:  %s  <====" % sid)


#common get method
def do_get(uri_path, jsonIn=False):
#Step 3: Get the search status
#myhttp.add_credentials(username, password)
    raw_base_url =main
    conn = http.client.HTTPSConnection(raw_base_url ,context = ssl._create_unverified_context() )
    user_pass = username + ':' + password
    auth = base64.b64encode(user_pass.encode())
    headers = {"Authorization": "Basic " + auth.decode()}
    print("\n", raw_base_url)
    print("\n", uri_path)
    conn.request("GET",uri_path , headers=headers)
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    
    #print(data)
    if jsonIn == True :
        print("------")
        data_ready = json.loads(data)
        print(data_ready['preview'])
   

    else:
        data = response.read().decode('utf-8')
        print(response.status, response.reason)
        print(data)


#Step 4: Get the search results
#Step 4: Get the search results

servicessearchstatusstr = '/services/search/jobs/%s/' % sid
services_search_results_str = '/services/search/jobs/%s/results?output_mode=json&count=0' % sid
do_get(servicessearchstatusstr)
time.sleep(5)
do_get(services_search_results_str, True)

