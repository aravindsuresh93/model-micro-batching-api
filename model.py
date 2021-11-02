"""
Temporary model.
This can be used as actual model inference/  a gRPC service to TF-Serving
"""
import time

class ClassifyOddEven:
    @staticmethod
    def predict(datadict):
        datadict = {k: (True if float(v) % 2 == 0 else False) for k, v in datadict.items()}
        time.sleep(0.5)
        return datadict
