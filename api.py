"""
FastAPI based API service
Collects the request, creates a uuid for request and pushes to redis.
The function polls redis db every X seconds to check if results are published
once results are available they are sent back to client
"""

from pydantic import BaseModel
from typing import Optional
from fastapi import FastAPI
import redis
import uuid
import json
import time

from config import CONFIG

app = FastAPI()
redisdb = redis.StrictRedis(host=CONFIG.REDIS_IP, port=CONFIG.REDIS_PORT, db=CONFIG.REDIS_DB_ID)


class Item(BaseModel):
    name: Optional[str] = None
    number: float


@app.post("/predict")
def predict(item: Item):
    number = item.number
    uid = str(uuid.uuid1())
    print(uid)
    redisdb.setex(f"{uid}_data", CONFIG.CLIENT_KEY_EXPIRY, number)
    time.sleep(0.5) #Image Decode Delay
    redisdb.rpush(CONFIG.IMAGE_QUEUE_ID, uid)

    ret = {}
    while True:
        output = redisdb.get(f"{uid}_pred")
        if output:
            ret["predictions"] = json.loads(output)["predictions"]
            redisdb.delete(f"{uid}_pred")
            break
        time.sleep(CONFIG.CLIENT_SLEEP)

    ret["es"] = 0
    return ret
