import threading
import requests
import random
import json
import time

url = "http://0.0.0.0:8000/predict"

s = time.time()

def pollAPI():
    ret = requests.post(url, data=json.dumps({"name": "aa", "number": random.randint(1, 100)}))
    print(ret.content, time.time() -s)


for i in range(100):
    timer = threading.Timer(0.1, pollAPI)
    timer.start()



