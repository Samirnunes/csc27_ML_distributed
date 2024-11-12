import os
import argparse
from pydantic_settings import BaseSettings

def _parse_args():
    parser = argparse.ArgumentParser(description="Run the app with options.")
    parser.add_argument("--local", action="store_true", help="Run the app in local mode")
    return parser.parse_args()

if _parse_args().local:
    os.environ["HOST"] = "localhost"
    os.environ["PORT"] = "8080"
else:
    os.environ["HOST"]= "0:0:0:0"
    os.environ["PORT"]= "80"

class _RPCConfig(BaseSettings):
    HOST: str
    PORT: int
    
RPC_CONFIG = _RPCConfig()
