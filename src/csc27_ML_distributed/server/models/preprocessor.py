from typing import Self

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.exceptions import NotFittedError
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from csc27_ML_distributed.server.log import logger
from csc27_ML_distributed.server.models.base import BasePreprocessor


class HousePricingPreprocessor(BasePreprocessor):
    def __init__(self) -> None:
        self._fitted: bool = False
        self._preprocessor: ColumnTransformer

    def fit(self, features: pd.DataFrame) -> Self:
        numeric_features = features.select_dtypes(include=[np.number]).columns.tolist()
        categorical_features = features.select_dtypes(
            exclude=[np.number]
        ).columns.tolist()

        numeric_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="mean")),
                ("scaler", StandardScaler()),
            ]
        )

        categorical_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore")),
            ]
        )

        self._preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_transformer, numeric_features),
                ("cat", categorical_transformer, categorical_features),
            ]
        )
        self._preprocessor.fit(features)
        self._fitted = True
        return self

    def transform(self, features: pd.DataFrame) -> np.ndarray:
        if self._fitted:
            return self._preprocessor.transform(features)
        e = "Preprocessor must be fitted first."
        logger.error(e)
        raise NotFittedError(e)

    def fit_transform(self, features: pd.DataFrame) -> np.ndarray:
        self.fit(features)
        return self.transform(features)
