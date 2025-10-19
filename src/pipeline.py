

from abc import ABC 

class Pipeline(ABC):
    def __init__(self):
        super().__init__()

    def __call__(self, *args, **kwds):
        return super().__call__(*args, **kwds)