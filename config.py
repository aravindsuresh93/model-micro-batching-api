"""
Configuration for API, batcher
"""
class CONFIG:
    REDIS_IP = ""
    REDIS_PORT = 6379
    REDIS_DB_ID = 0

    IMAGE_QUEUE_ID = "IQ"
    CLIENT_SLEEP = 0.05
    SERVER_SLEEP = 0.05
    BATCH_SIZE = 5

    CLIENT_KEY_EXPIRY = 60
    SERVER_KEY_EXPIRY = 60

    TIMERSPAWN = 0.00001
