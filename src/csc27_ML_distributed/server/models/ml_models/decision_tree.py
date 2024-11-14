import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from csc27_ML_distributed.server.models.base import BaseModel


class DecisionTreeRegressorModel(BaseModel):
    def __init__(self) -> None:
        self._model = DecisionTreeRegressor(max_depth=3, max_leaf_nodes=10)
        self._label_encoder = None
        self._preprocessor = None

    def fit(self, features: pd.DataFrame, labels: pd.Series) -> None:
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

        features = self._preprocessor.fit_transform(features)
        self._model.fit(features, labels)

    def predict(self, features: pd.DataFrame) -> np.ndarray:
        features = self._preprocessor.transform(features)
        predictions = self._model.predict(features)
        return predictions


class DecisionTreeClassifierModel(BaseModel):
    def __init__(self) -> None:
        self._model = DecisionTreeClassifier(max_depth=3, max_leaf_nodes=10)
        self._label_encoder = None
        self._preprocessor = None

    def fit(self, features: pd.DataFrame, labels: pd.Series) -> None:
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

        features = self._preprocessor.fit_transform(features)
        self._model.fit(features, labels)

    def predict(self, features: pd.DataFrame) -> np.ndarray:
        features = self._preprocessor.transform(features)
        predictions = self._model.predict(features)
        return predictions
