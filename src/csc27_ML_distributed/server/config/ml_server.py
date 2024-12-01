from typing import Literal

from pydantic_settings import BaseSettings


class _MLConfig(BaseSettings):
    PROBLEM_TYPE: Literal["regression", "classification"] = "regression"
    MODEL: str = ""
    LABEL: str = ""
    DATA_DIR: str = ""
    RANDOM_STATE: int = 0
    TEST_SIZE: float = 0.3


ML_SERVER_CONFIG = _MLConfig()
