import json
import pickle
from pathlib import Path
from typing import Any, Dict, List, Union
from xmlrpc.client import Binary

import pandas as pd
from sklearn.model_selection import train_test_split

from csc27_ML_distributed.server.config import (
    ML_MODELS,
    ML_SERVER_CONFIG,
    MLClassificationMetrics,
    MLRegressionMetrics,
)
from csc27_ML_distributed.server.log import logger
from csc27_ML_distributed.server.models.base import BaseModel, BaseServer

FeatureType = Dict[str, List[Union[int, float, str]]]
LabelType = List[Union[int, float, str]]


class MLServer(BaseServer):
    """
    A class to manage a machine learning server that communicates using XML-RPC.

    The server allows initializing a machine learning model, fitting the model
    with training data, and making predictions with the trained model.
    """

    _CONFIG = ML_SERVER_CONFIG
    _ML_MODELS = ML_MODELS

    def __init__(self) -> None:
        """
        Initializes the MLServer instance with the specified host and port.
        """
        logger.info(f"**Serving with the following settings:\n{self._CONFIG}")
        self._model: BaseModel = self._ML_MODELS[self._CONFIG.MODEL]
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
        if not model in self._ML_MODELS:
            e = f"{model} isn't any of the values: {self._ML_MODELS.values()}"
            logger.error(e)
            raise ValueError

        new_model = self._ML_MODELS[model]
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
        features = pd.DataFrame(features, index=[0])
        return json.dumps(
            {
                "Prediction": self._model.predict(features).tolist(),
                "ProblemType": self._CONFIG.PROBLEM_TYPE,
            }
        )

    def send_model(self) -> bytes | str:
        if self._fitted:
            return pickle.dumps(self._model)
        e = "send_model failed. You must call the fit function first."
        logger.error(e)
        return json.dumps(f"error: {e}")

    def evaluate(self, models: List[bytes | Binary | List] | Any) -> Any:
        metric_objs = []

        if self._fitted:
            if not self._CONFIG.PROBLEM_TYPE in ["regression", "classification"]:
                e = "PROBLEM_TYPE must be either regression or classification."
                logger.error(e)
                raise ValueError

            if self._CONFIG.PROBLEM_TYPE == "regression":
                metrics_type = MLRegressionMetrics
            elif self._CONFIG.PROBLEM_TYPE == "classification":
                metrics_type = MLClassificationMetrics

            for model in models:
                model = self._parse_model(model)
                y_pred = model.predict(self._X_test)
                metric_objs.append(metrics_type.from_labels(self._y_test, y_pred))

            aggregate = dict.fromkeys(metrics_type().__dict__.keys(), 0)
            for metric_obj in metric_objs:
                for metric, value in metric_obj.__dict__.items():
                    aggregate[metric] += value

            for metric in aggregate.keys():
                aggregate[metric] = aggregate[metric] / len(models)

            return json.dumps(aggregate)
        e = "evaluate failed. You must call the fit function first."
        logger.error(e)
        return json.dumps(f"error: {e}")

    def _parse_model(self, model: bytes | Binary | List) -> Any:
        if isinstance(model, Binary):
            model = model.data
        if isinstance(model, List):
            model = bytes(model)
        return pickle.loads(model)
