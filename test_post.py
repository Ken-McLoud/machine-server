#!flask/bin/python
import requests
r=requests.post('http://localhost:5000/submit_data', data={'timestamp':'2016-02-01 01:01:01','source':'dev_machine','datatype':'tool life','payload':'t1 50,100 t2 20,200'})

