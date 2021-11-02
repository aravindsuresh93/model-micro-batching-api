"""
This script reads the redis queue, stacks the data into micro-batches and sends for model inferencing
The results are decoupled and pushed back to redis
"""
import redis
import time
import json


from config.config import CONFIG
from threading import Timer

"""Custom Model class"""
from model.model import ClassifyOddEven


class Batcher:
    def __init__(self):
        self.model = ClassifyOddEven()
        self.redisdb = redis.StrictRedis(host=CONFIG.REDIS_IP, port=CONFIG.REDIS_PORT, db=CONFIG.REDIS_DB_ID)

    def set_keys(self, results):
        for uid, result in results.items():
            self.redisdb.set(f"{uid}_pred", json.dumps({"predictions": result}))

    def run(self):
        while True:
            """Pull data from redis queue"""
            queue = []
            for _ in range(CONFIG.BATCH_SIZE):
                val = self.redisdb.rpop(CONFIG.IMAGE_QUEUE_ID)
                if val: queue.append(val)

            if not len(queue):
                continue

            """Below section is used to stack the data according to model """
            datadict = {}
            for q in queue:
                q = q.decode("utf-8")
                data = self.redisdb.get(f"{q}_data")
                if data:
                    data = data.decode("utf-8")
                    datadict[q] = data

            """Prediction"""
            if len(datadict) > 0:
                results = self.model.predict(datadict)
                """push inference to redis"""
                Timer(CONFIG.TIMERSPAWN, self.set_keys, [results]).start()

            time.sleep(CONFIG.SERVER_SLEEP)


print("Model Server Starting")
batcher = Batcher()
batcher.run()
