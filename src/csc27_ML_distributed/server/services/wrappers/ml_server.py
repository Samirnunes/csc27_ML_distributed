import pandas as pd
from typing import List, Dict, Union
from csc27_ML_distributed.server.models.base import BaseServer
from csc27_ML_distributed.server.models.base import BaseModel
from csc27_ML_distributed.server.models.ml_model import MLModel
from csc27_ML_distributed.server.models.config import ML_SERVER_CONFIG
from csc27_ML_distributed.server.log import logger

FeatureType = Dict[str, List[Union[int, float, str]]]
LabelType = List[Union[int, float, str]]


class MLServer(BaseServer):
    """
    A class to manage a machine learning server that communicates using XML-RPC.

    The server allows initializing a machine learning model, fitting the model
    with training data, and making predictions with the trained model.
    """

    CONFIG = ML_SERVER_CONFIG

    def __init__(self) -> None:
        """
        Initializes the MLServer instance with the specified host and port.
        """
        logger.info(f"**Serving with {self.CONFIG.MODEL} model**")
        self.model: BaseModel = MLModel()[self.CONFIG.MODEL]

    def fit(self, features: FeatureType, labels: LabelType) -> None:
        """
        Trains the machine learning model with the provided features and labels.

        Args:
            features (FeatureType): A dictionary containing the features as a list of numerical or string values.
            labels (LabelType): A list containing the labels (target values).
        """
        df_features = pd.DataFrame(features)
        df_labels = pd.Series(labels)
        print("\nModel training...")
        self.model.fit(features=df_features, labels=df_labels)
        print("\nModel trained successfully")

    def predict(self, features: FeatureType) -> LabelType:
        """
        Makes a prediction based on the provided features.

        Args:
            features (FeatureType): A dictionary containing the features for making predictions.

        Returns:
            LabelType: A list of predicted values.
        """
        df_features = pd.DataFrame(features)
        prediction = self.model.predict(df_features)
        prediction_dict: LabelType = prediction.tolist()

        return prediction_dict
