from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

from csc27_ML_distributed.server.log import logger
from csc27_ML_distributed.server.models.base import BaseServer
from csc27_ML_distributed.server.models.config import RPC_CONFIG

class RPC:
    """A wrapper for a server meant to run with RPC"""
    
    CONFIG = RPC_CONFIG
    
    class _RequestHandler(SimpleXMLRPCRequestHandler):
        rpc_paths = ('/')
    
    def __init__(self, server: BaseServer):
        self._rpc = SimpleXMLRPCServer(
            (self.CONFIG.HOST, self.CONFIG.PORT),
            requestHandler=RPC._RequestHandler,
            allow_none=True,
            logRequests=False
        )
        self._rpc.register_instance(server)
        
    def serve(self):
        self._rpc.server_activate()
        logger.info(f"**Server is running on {self.CONFIG.HOST}:{self.CONFIG.PORT}")
        self._rpc.serve_forever()