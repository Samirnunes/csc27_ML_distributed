import pandas as pd
from models import MLModel
from models.base import BaseModel
from typing import List, Dict, Union
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

# Define the types for features and labels
FeatureType = Dict[str, List[Union[int, float, str]]]
LabelType = List[Union[int, float, str]]

host = "localhost"
port = 8000

class ServerML:
    """
    A class to manage a machine learning server that communicates using XML-RPC.

    The server allows initializing a machine learning model, fitting the model
    with training data, and making predictions with the trained model.
    """

    def __init__(self) -> None:
        """
        Initializes the ServerML instance with the specified host and port.
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


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/')

server = SimpleXMLRPCServer(
    (host, port),
    requestHandler=RequestHandler,
    allow_none=True,
    logRequests=False
)

server.register_instance(ServerML())
print(f"\n\nServer is running on {host}:{port}")
server.serve_forever()