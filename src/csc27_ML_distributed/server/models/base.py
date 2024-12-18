from abc import ABC, abstractmethod
from typing import Any, Self

import numpy as np
import pandas as pd
from sklearn.exceptions import NotFittedError

from csc27_ML_distributed.server.log import logger


class BaseServer(ABC):
    pass


class BasePreprocessor(ABC):
    @abstractmethod
    def fit(self, features: pd.DataFrame, labels: pd.Series) -> Self:
        raise NotImplementedError

    @abstractmethod
    def transform(self, features: pd.DataFrame) -> np.ndarray:
        raise NotImplementedError

    def fit_transform(self, features: pd.DataFrame) -> np.ndarray:
        self.fit(features)
        return self.transform(features)


class BaseModel(ABC):
    """
    Abstract base class for a machine learning model.

    This class defines the basic structure for any machine learning model,
    requiring the implementation of methods for fitting and predicting.
    """

    def __init__(self, model: Any, preprocessor: BasePreprocessor) -> None:
        self._fitted = False
        self._model = model
        self._preprocessor: BasePreprocessor = preprocessor

    def __str__(self) -> str:
        return self.__class__.__name__

    def fit(self, features: pd.DataFrame, labels: pd.Series) -> Self:
        self._model.fit(self._preprocessor.fit_transform(features), labels)
        self._fitted = True
        return self

    def predict(self, features: pd.DataFrame) -> np.ndarray:
        if self._fitted:
            return self._model.predict(self._preprocessor.transform(features))
        e = "Model must be fitted first."
        logger.error(e)
        raise NotFittedError(e)
