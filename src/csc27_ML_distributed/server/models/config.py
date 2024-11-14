import os
import argparse
from typing import Literal
from pydantic_settings import BaseSettings


def _verify_local_config() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the app with options.")
    parser.add_argument(
        "--local", action="store_true", help="Run the app in local mode"
    )

    args = parser.parse_args()
    if args.local:
        os.environ["PYTHONPATH"] = "src/"
        os.environ["HOST"] = "localhost"
        os.environ["PORT"] = "8080"
        os.environ["MODEL"] = "dummy"
        os.environ["DATA_DIR"] = "data/A"

_verify_local_config()

class _RPCConfig(BaseSettings):
    HOST: str = "localhost"
    PORT: int = "8080"


class _MLConfig(BaseSettings):
    PROBLEM_TYPE: Literal["regression", "classification"] = "regression"
    MODEL: str = "tree-regressor"
    LABEL: str = "SalePrice"
    DATA_DIR: str = "data/A"
    RANDOM_STATE: int = 0
    TEST_SIZE: float = 0.3


RPC_CONFIG = _RPCConfig()
ML_SERVER_CONFIG = _MLConfig()
