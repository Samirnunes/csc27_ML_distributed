from xmlrpc.server import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer

from csc27_ML_distributed.server.log import logger
from csc27_ML_distributed.server.models.base import BaseServer


class RPC:
    """A wrapper for a server meant to run with RPC"""

    class _RequestHandler(SimpleXMLRPCRequestHandler):
        rpc_paths = ""

    def __init__(self, server: BaseServer) -> None:
        self._rpc = SimpleXMLRPCServer(
            ("0.0.0.0", 80),
            requestHandler=RPC._RequestHandler,
            allow_none=True,
            logRequests=False,
        )
        self._rpc.register_instance(server)

    def serve(self) -> None:
        self._rpc.server_activate()
        logger.info(f"**Server is running on 0.0.0.0:80**")
        self._rpc.serve_forever()
