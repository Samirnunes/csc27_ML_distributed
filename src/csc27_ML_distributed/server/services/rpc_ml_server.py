from csc27_ML_distributed.server.services.wrappers import RPC, MLServer


class RPCMLServer:
    """Façade for MLServer + RPC classes"""

    def __init__(self) -> None:
        self._rpc = RPC(MLServer())

    def run(self) -> None:
        self._rpc.serve()
