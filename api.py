"""
FastAPI based API service
Collects the request, creates a uuid for request and pushes to redis.
The function polls redis db every X seconds to check if results are published
once results are available they are sent back to client
"""

from pydantic import BaseModel
from fastapi import FastAPI
from typing import Optional
import redis
import uuid
import json
import time

from config.config import CONFIG

app = FastAPI()
redisdb = redis.StrictRedis(host=CONFIG.REDIS_IP, port=CONFIG.REDIS_PORT, db=CONFIG.REDIS_DB_ID)


class Item(BaseModel):
    number: float


@app.post("/predict")
def predict(item: Item):
    # Get data
    number = item.number

    # Add code to validate input data here
    # Mimicing data Decode Delay (in case of images)
    time.sleep(0.5) 

    # Generate UUID | Push UUID to queue | Set data with key <uuid>_data with expriry
    uid = str(uuid.uuid4().hex)
    redisdb.setex(f"{uid}_data", CONFIG.CLIENT_KEY_EXPIRY, number)
    redisdb.rpush(CONFIG.IMAGE_QUEUE_ID, uid)

    # while loop to get 
    ret = {}
    while True:
        output = redisdb.get(f"{uid}_pred")
        if output:
            ret["predictions"] = json.loads(output)["predictions"]
            break
        time.sleep(CONFIG.CLIENT_SLEEP)

    return ret


# Command : `uvicorn api:app`