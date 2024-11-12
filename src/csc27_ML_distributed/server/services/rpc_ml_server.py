from csc27_ML_distributed.server.services.wrappers import RPC
from csc27_ML_distributed.server.services.wrappers import MLServer

class RPCMLServer:
    """Façade for MLServer + RPC classes"""

    def __init__(self):
        self._rpc = RPC(MLServer())

    def run(self):
        self._rpc.serve()