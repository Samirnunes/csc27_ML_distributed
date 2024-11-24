from typing import Literal

from pydantic_settings import BaseSettings


class _MLConfig(BaseSettings):
    PROBLEM_TYPE: Literal["regression", "classification"]
    MODEL: str
    LABEL: str
    DATA_DIR: str
    RANDOM_STATE: int
    TEST_SIZE: float


ML_SERVER_CONFIG = _MLConfig()
