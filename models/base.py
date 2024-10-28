import pandas as pd
import numpy as np
from sklearn.dummy import DummyRegressor
from abc import ABC, abstractmethod

class BaseModel(ABC):
    """
    Abstract base class for a machine learning model.

    This class defines the basic structure for any machine learning model,
    requiring the implementation of methods for fitting and predicting.
    """

    @abstractmethod
    def fit(self, features: pd.DataFrame, labels: pd.Series) -> None:
        """
        Trains the model using the provided features and labels.

        Args:
            features (pd.DataFrame): A DataFrame containing the input features.
            labels (pd.Series): A Series containing the target labels.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        pass
    

    @abstractmethod
    def predict(self, features: pd.DataFrame) -> np.ndarray:
        """
        Predicts labels for the provided features.

        Args:
            features (pd.DataFrame): A DataFrame containing the input features for prediction.

        Returns:
            np.ndarray: A numpy array containing the predicted labels.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        pass
