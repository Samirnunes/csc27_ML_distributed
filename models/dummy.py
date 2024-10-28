import pandas as pd
import numpy as np
from sklearn.dummy import DummyRegressor
from models import BaseModel

class DummyModel(BaseModel):
    """
    Dummy model implementation that inherits from BaseModel.

    This model uses scikit-learn's DummyRegressor, which makes predictions 
    based on a simple strategy, such as always predicting the mean of the 
    target values.
    """

    def __init__(self, strategy: str = "mean") -> None:
        """
        Initializes the DummyModel with a specified strategy.

        Args:
            strategy (str): The strategy used by DummyRegressor for making predictions. 
                Default is "mean". Possible values include "mean", "median", "quantile", 
                and "constant".

        Attributes:
            model (DummyRegressor): The dummy regressor instance.
        """
        self.model = DummyRegressor(strategy=strategy)


    def fit(self, features: pd.DataFrame, labels: pd.Series) -> None:
        """
        Trains the DummyRegressor model using the provided features and labels.

        Args:
            features (pd.DataFrame): A DataFrame containing the input features.
            labels (pd.Series): A Series containing the target labels.
        """
        self.model.fit(features, labels)
        

    def predict(self, features: pd.DataFrame) -> np.ndarray:
        """
        Makes predictions based on the provided features using the trained model.

        Args:
            features (pd.DataFrame): A DataFrame containing the input features.

        Returns:
            np.ndarray: A numpy array containing the predicted values.
        """
        return self.model.predict(features)
