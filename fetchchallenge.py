'''
Coding Challenge for Fetch
Author: Holly Liu
12/17/23

Implementation Note
    There is a scalability issue where servers with a large number of endpoints
    can cause delays that pass the 15s timeout threshold. To accommodate, this
    implementation may need to include asynchronity. 
    For example, if the number of endpoints is greater than 100, then the timeout
    value of 0.5s could result in a delay of above 10s. Increasing this number
    may cause the delay to pass 15s. 
    The solution for this may be multiplexing the I/O. 
    (Note: I/O is different from CPU in that it writes, reads, and copies,
    while CPU does computations and operations. I/O can be more easily 
    parallelized.)
    The current simple solution will likely work if the number of endpoints in YAML
    is less than 100.         
    
'''

import yaml
import time 
import requests
from urllib.parse import urlparse
import collections
import logging 
import sys

logging.basicConfig(filename='fetchchallenge.log', level=logging.INFO)

def run(file_name):
    targets = [] 
    with open(file_name, "r") as fh:
        targets = yaml.safe_load(fh)
            
    reqs_per_domain = collections.Counter()
    UPs_per_domain = collections.Counter()
    
    while(True):         
        for req in targets:
            name = req["name"]
            url = req["url"]
            method = req.get('method', 'GET')
            headers = req.get('headers')
            body = req.get('body')
            domain = urlparse(url).netloc
            
            try:
                response = requests.request(method, url, headers=headers, 
                                            json=body, timeout=0.5)
                if (200 <= response.status_code <= 299):
                    UPs_per_domain[domain] += 1
            except requests.exceptions.Timeout:
                logging.info(f'{method} at {url} request timed out')
                
            reqs_per_domain[domain] += 1
                
        #assume total number of requests per domain is nonzero
        for key in reqs_per_domain: 
            print(f'{key} has '
                  f'{round((UPs_per_domain[key] / reqs_per_domain[key]) * 100)}'
                  ' availability percentage')
            
        time.sleep(15)
    
if __name__ == '__main__':
    run(sys.argv[1])