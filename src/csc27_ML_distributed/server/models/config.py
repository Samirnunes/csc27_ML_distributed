import os
import argparse
from pydantic_settings import BaseSettings


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the app with options.")
    parser.add_argument(
        "--local", action="store_true", help="Run the app in local mode"
    )
    return parser.parse_args()


if _parse_args().local:
    os.environ["HOST"] = "localhost"
    os.environ["PORT"] = "8080"
    os.environ["MODEL"] = "dummy"
else:
    # In production, this should not exist,
    # these variables must be injected in the env
    os.environ["HOST"] = "0:0:0:0"
    os.environ["PORT"] = "80"
    os.environ["MODEL"] = "linear"


class _RPCConfig(BaseSettings):
    HOST: str
    PORT: int


class _MLConfig(BaseSettings):
    MODEL: str


RPC_CONFIG = _RPCConfig()
ML_SERVER_CONFIG = _MLConfig()
