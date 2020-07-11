#!/usr/bin/env python3
''' 
Do something faster.
'''

import os
import sys

import urllib3

brewery_id = 0

# Defaults:
URL = "https://www.beeradvocate.com/beer/profile/{}/"

url = URL.format(brewery_id)
http = urllib3.PoolManager()
r = http.request('GET', url)
r.status
r.data

from urllib3 import PoolManager

manager = PoolManager(num_pools=2)
r = manager.request('GET', 'http://google.com/')
r = manager.request('GET', 'http://google.com/mail')
r = manager.request('GET', 'http://yahoo.com/')
len(manager.pools)

from pylib import queue # local import
from threading import Thread


concurrent = 200

def doWork():
    while True:
        url = q.get()
        status, url = getStatus(url)
        doSomethingWithResult(status, url)
        q.task_done()

def getStatus(ourl):
    try:
        url = urlparse(ourl)
        conn = httplib.HTTPConnection(url.netloc)   
        conn.request("HEAD", url.path)
        res = conn.getresponse()
        return res.status, ourl
    except:
        return "error", ourl

def doSomethingWithResult(status, url):
    print status, url

def doWork():
    print("foobar")

concurrent = 200
q = queue.Queue(concurrent * 2)

for i in range(concurrent):
    t = Thread(target=doWork)
    t.daemon = True
    t.start()
try:

    for url in open('urls.txt'):
        print(url.strip())
    # End

        q.put(url.strip())
    q.join()

except KeyboardInterrupt:
    sys.exit(1)
