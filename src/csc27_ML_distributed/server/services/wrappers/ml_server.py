import json
import pickle
from pathlib import Path
from typing import Dict, List, Union
from xmlrpc.client import Binary

import pandas as pd
from sklearn.model_selection import train_test_split

from csc27_ML_distributed.server.log import logger
from csc27_ML_distributed.server.models.base import BaseModel, BaseServer
from csc27_ML_distributed.server.config import ML_SERVER_CONFIG
from csc27_ML_distributed.server.models.ml_metric import (
    MLClassificationMetrics,
    MLRegressionMetrics,
)
from csc27_ML_distributed.server.models.ml_model import MLModelsDict

FeatureType = Dict[str, List[Union[int, float, str]]]
LabelType = List[Union[int, float, str]]


class MLServer(BaseServer):
    """
    A class to manage a machine learning server that communicates using XML-RPC.

    The server allows initializing a machine learning model, fitting the model
    with training data, and making predictions with the trained model.
    """

    _CONFIG = ML_SERVER_CONFIG
    _MODEL_DICT = MLModelsDict()

    def __init__(self) -> None:
        """
        Initializes the MLServer instance with the specified host and port.
        """
        logger.info(f"**Serving with the following settings:\n{self._CONFIG}")
        self._model: BaseModel = self._MODEL_DICT[self._CONFIG.MODEL]
        self._fitted = False

        data: pd.DataFrame = pd.read_csv(
            Path(self._CONFIG.DATA_DIR) / Path("data.csv"), index_col=[0]
        )
        features: pd.DataFrame = data.drop(self._CONFIG.LABEL, axis=1)
        labels: pd.DataFrame = data[self._CONFIG.LABEL]

        self._X_train, self._X_test, self._y_train, self._y_test = train_test_split(
            features,
            labels,
            test_size=self._CONFIG.TEST_SIZE,
            random_state=self._CONFIG.RANDOM_STATE,
        )
        self._y_train = pd.Series(self._y_train)
        self._y_test = pd.Series(self._y_test)

    def set_model(self, model: str) -> str:
        if not model in self._MODEL_DICT:
            e = f"{model} isn't any of the values: {self._MODEL_DICT.values()}"
            logger.error(e)
            raise ValueError

        new_model = self._MODEL_DICT[model]
        logger.info(f"**Changing model from {self._model} to {new_model}")
        self._model = new_model
        return json.dumps("ok")

    def fit(self) -> str:
        """
        Trains the machine learning model with the provided features and labels.
        """
        logger.info("Training model...")
        self._model.fit(features=self._X_train, labels=self._y_train)
        logger.info("Model trained successfully")
        self._fitted = True
        return json.dumps("ok")

    def predict(self, features: FeatureType) -> str:
        """
        Makes a prediction based on the provided features using the node's weak learner.

        Args:
            features (FeatureType): A dictionary containing the features for making predictions.

        Returns:
            LabelType: A list of predicted values.
        """
        df_features = pd.DataFrame(features)
        prediction = self._model.predict(df_features)
        return json.dumps(prediction.tolist())

    def send_model(self) -> bytes:
        if self._fitted:
            return pickle.dumps(self._model)
        logger.warning("send_model failed. You must call the fit function first.")

    def evaluate(self, models: List[bytes | Binary]) -> str:
        metric_objs = []

        if not self._CONFIG.PROBLEM_TYPE in ["regression", "classification"]:
            e = "PROBLEM_TYPE must be either regression or classification."
            logger.error(e)
            raise ValueError

        if self._CONFIG.PROBLEM_TYPE == "regression":
            metrics_type = MLRegressionMetrics
        elif self._CONFIG.PROBLEM_TYPE == "classification":
            metrics_type = MLClassificationMetrics

        for model in models:
            if isinstance(model, Binary):
                model = model.data
            model = pickle.loads(model)
            y_pred = model.predict(self._X_test)
            metric_objs.append(metrics_type.from_labels(self._y_test, y_pred))

        aggregate = dict.fromkeys(metrics_type().__dict__.keys(), 0)
        for metric_obj in metric_objs:
            for metric, value in metric_obj.__dict__.items():
                aggregate[metric] += value

        for metric in aggregate.keys():
            aggregate[metric] = aggregate[metric] / len(models)

        return json.dumps(aggregate)
