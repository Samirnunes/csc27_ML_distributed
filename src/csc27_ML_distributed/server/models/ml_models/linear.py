import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from csc27_ML_distributed.server.models.base import BaseModel


class LinearRegressorModel(BaseModel):
    def __init__(self) -> None:
        self.model = LinearRegression()
        self.label_encoder = None
        self.preprocessor = None

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

        self.preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_transformer, numeric_features),
                ("cat", categorical_transformer, categorical_features),
            ]
        )

        features = self.preprocessor.fit_transform(features)
        self.model.fit(features, labels)

    def predict(self, features: pd.DataFrame) -> np.ndarray:
        features = self.preprocessor.transform(features)
        predictions = self.model.predict(features)
        return predictions

class LinearClassifierModel(BaseModel):
    def __init__(self) -> None:
        self.model = LogisticRegression()
        self.label_encoder = None
        self.preprocessor = None

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

        self.preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_transformer, numeric_features),
                ("cat", categorical_transformer, categorical_features),
            ]
        )

        features = self.preprocessor.fit_transform(features)
        self.model.fit(features, labels)

    def predict(self, features: pd.DataFrame) -> np.ndarray:
        features = self.preprocessor.transform(features)
        predictions = self.model.predict(features)
        return predictions