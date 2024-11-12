import pandas as pd
from typing import List, Dict, Union
from csc27_ML_distributed.server.models.base import BaseServer
from csc27_ML_distributed.server.models.base import BaseModel
from csc27_ML_distributed.server.models.ml_model import MLModel
from csc27_ML_distributed.server.services.wrappers import RPC

FeatureType = Dict[str, List[Union[int, float, str]]]
LabelType = List[Union[int, float, str]]

class _MLServer(BaseServer):
    """
    A class to manage a machine learning server that communicates using XML-RPC.

    The server allows initializing a machine learning model, fitting the model
    with training data, and making predictions with the trained model.
    """

    def __init__(self) -> None:
        """
        Initializes the MLServer instance with the specified host and port.
        """
        self.model: BaseModel | None = None


    def initModel(self, algorithm: str = "dummy") -> None:
        """
        Initializes the machine learning model.

        Args:
            algorithm (str): The type of model to initialize. Default is "dummy".
        """
        self.model = MLModel[algorithm]()
        print(f"\nInitialized the model {algorithm}")


    def fit(self, features: FeatureType, labels: LabelType) -> None:
        """
        Trains the machine learning model with the provided features and labels.

        Args:
            features (FeatureType): A dictionary containing the features as a list of numerical or string values.
            labels (LabelType): A list containing the labels (target values).
        
        Raises:
            Exception: If the model has not been initialized using `initModel()`.
        """
        if self.model is None:
            raise Exception("Uninitialized model. Call initModel() first.")
        
        df_features = pd.DataFrame(features)
        df_labels = pd.Series(labels)
        print("\nModel training...")
        self.model.fit(df_features, df_labels)
        print("\nModel trained successfully")


    def predict(self, features: FeatureType) -> LabelType:
        """
        Makes a prediction based on the provided features.

        Args:
            features (FeatureType): A dictionary containing the features for making predictions.

        Returns:
            LabelType: A list of predicted values.

        Raises:
            Exception: If the model has not been initialized using `initModel()`.
        """
        if self.model is None:
            raise Exception("Uninitialized model. Call initModel() first.")
        
        df_features = pd.DataFrame(features)
        prediction = self.model.predict(df_features)
        prediction_dict: LabelType = prediction.tolist()

        return prediction_dict
    
class RPCMLServer:
    """Façade for MLServer + RPC classes"""
    
    def __init__(self):
        self._server = RPC(_MLServer())
    
    def run(self):
        self._server.serve()