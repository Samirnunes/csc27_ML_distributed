import pandas as pd
from typing import List, Literal, Self

from pydantic_settings import BaseSettings

from csc27_ML_distributed.server.models.base import BaseModel
from csc27_ML_distributed.server.models.preprocessor import HousePricingPreprocessor
from csc27_ML_distributed.server.models.ml_models import (
    DecisionTreeClassifierModel,
    DecisionTreeRegressorModel,
    LinearClassifierModel,
    LinearRegressorModel,
)

from pydantic.dataclasses import dataclass
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    mean_squared_log_error,
    precision_score,
    r2_score,
    recall_score,
)


class _RPCConfig(BaseSettings):
    HOST: str
    PORT: int


class _MLConfig(BaseSettings):
    PROBLEM_TYPE: Literal["regression", "classification"]
    MODEL: str
    LABEL: str
    DATA_DIR: str
    RANDOM_STATE: int
    TEST_SIZE: float


class _MLModels:
    _MODELS = {
        "house-pricing-linear-classifier": LinearClassifierModel(
            HousePricingPreprocessor()
        ),
        "house-pricing-linear-regressor": LinearRegressorModel(
            HousePricingPreprocessor()
        ),
        "house-pricing-tree-classifier": DecisionTreeClassifierModel(
            HousePricingPreprocessor(), 3, 10
        ),
        "house-pricing-tree-regressor": DecisionTreeRegressorModel(
            HousePricingPreprocessor(), 3, 10
        ),
    }

    def __getitem__(self, key: str) -> BaseModel:
        return self._MODELS[key]

    def __contains__(self, key: str) -> bool:
        return key in self._MODELS

    def __repr__(self):
        return repr(self._MODELS)

    def values(self) -> List[BaseModel]:
        return list(self._MODELS.values())

    def keys(self) -> List[str]:
        return list(self._MODELS.keys())


@dataclass
class MLRegressionMetrics:
    r2_score: float = 0.0
    mean_absolute_error: float = 0.0
    mean_squared_error: float = 0.0
    mean_squared_log_error: float = 0.0

    @staticmethod
    def from_labels(y_true: pd.DataFrame, y_pred: pd.DataFrame) -> Self:
        return MLRegressionMetrics(
            r2_score(y_true, y_pred),
            mean_absolute_error(y_true, y_pred),
            mean_squared_error(y_true, y_pred),
            mean_squared_log_error(y_true, y_pred),
        )


@dataclass
class MLClassificationMetrics:
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0

    @staticmethod
    def from_labels(y_true: pd.DataFrame, y_pred: pd.DataFrame) -> Self:
        return MLClassificationMetrics(
            accuracy_score(y_true, y_pred),
            precision_score(y_true, y_pred),
            recall_score(y_true, y_pred),
            f1_score(y_true, y_pred),
        )

ML_MODELS = _MLModels()
RPC_CONFIG = _RPCConfig()
ML_SERVER_CONFIG = _MLConfig()
