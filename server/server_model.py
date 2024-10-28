import pandas as pd
from xmlrpc.server import SimpleXMLRPCServer
from ..models import MLModel, BaseModel
from typing import List, Dict, Union

# Define the types for features and labels
FeatureType = Dict[str, List[Union[int, float, str]]]
LabelType = List[Union[int, float, str]]

class ServerML:
    """
    A class to manage a machine learning server that communicates using XML-RPC.

    The server allows initializing a machine learning model, fitting the model
    with training data, and making predictions with the trained model.
    """

    def __init__(self, host: str = "localhost", port: int = 8000) -> None:
        """
        Initializes the ServerML instance with the specified host and port.

        Args:
            host (str): The address where the server will be hosted. Default is "localhost".
            port (int): The port number on which the server will listen. Default is 8000.
        """
        self.host: str = host
        self.port: int = port
        self.model: BaseModel | None = None
        self.server: SimpleXMLRPCServer = SimpleXMLRPCServer((self.host, self.port))

        # Registers the functions for RPC
        self.server.register_function(self.predict, "predict")
        self.server.register_function(self.fit, "fit")
        self.server.register_function(self.initModel, "initModel")

    def initModel(self, algorithm: str = "dummy") -> None:
        """
        Initializes the machine learning model.

        Args:
            algorithm (str): The type of model to initialize. Default is "dummy".
        """
        self.model = MLModel(algorithm)

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
        self.model.fit(df_features, df_labels)

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

    def listen(self) -> None:
        """
        Starts the XML-RPC server and waits for client requests.
        """
        print(f"Server is running on {self.host}:{self.port}")
        self.server.serve_forever()

if __name__ == "__main__":
    features_train = {
        "feature1": [1.0, 2.0, 3.0, 4.0, 5.0],
        "feature2": [10.0, 20.0, 30.0, 40.0, 50.0]
    }

    labels_train = [100, 200, 300, 400, 500]

    features_test = {
        "feature1": [6.0, 7.0],
        "feature2": [60.0, 70.0]
    }

    serverML = ServerML()
    
    print("Inicializando o modelo Dummy...")
    serverML.initModel(model="dummy")
    serverML.listen()

    print("Treinando o modelo com os dados de treino...")
    serverML.fit(features_train, labels_train)

    print("Fazendo previsões com novos dados...")
    predictions = serverML.predict(features_test)

    print("Previsões recebidas do servidor:", predictions)
