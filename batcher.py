"""
This script reads the redis queue, stacks the data into micro-batches and sends for model inferencing
The results are decoupled and pushed back to redis
"""
import redis
import time
import json

from clogger.clogger import CLogger
from config.config import CONFIG
from threading import Timer

"""Custom Model class"""
from model.model import ClassifyOddEven


class Batcher:
    def __init__(self):
        self.model = ClassifyOddEven()
        self.redisdb = redis.StrictRedis(host=CONFIG.REDIS_IP, port=CONFIG.REDIS_PORT, db=CONFIG.REDIS_DB_ID)
        self.logger = CLogger.getLogger('model-batcher')
        self.logger.info('Initialised Model Batcher')

    def set_keys(self, results):
        for uid, result in results.items():
            self.redisdb.setex(f"{uid}_pred", CONFIG.SERVER_KEY_EXPIRY, json.dumps({"predictions": result}))

    def run(self):
        while True:
            time.sleep(CONFIG.SERVER_SLEEP)

            # Pull data from redis queue
            queue = []
            for _ in range(CONFIG.BATCH_SIZE):
                val = self.redisdb.rpop(CONFIG.IMAGE_QUEUE_ID)
                if val: queue.append(val)

            if not len(queue): continue

            # Stack data for batch processing (add your custom code here)
            datadict = {}
            for q in queue:
                q = q.decode("utf-8")
                data = self.redisdb.get(f"{q}_data") # Get Actual Data
                if data:
                    data = data.decode("utf-8")
                    datadict[q] = data

            # Predict and push to redis
            if len(datadict) > 0:
                results = self.model.predict(datadict)
                Timer(CONFIG.TIMERSPAWN, self.set_keys, [results]).start()

            

batcher = Batcher()
batcher.run()
