import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from csc27_ML_distributed.server.models.base import BaseModel

class LinearOrLogisticModel(BaseModel):
    """
    A model that automatically handles preprocessing steps, including imputing missing values,
    encoding categorical variables, and scaling numerical data. It detects whether the task
    is regression or classification based on the nature of the labels.
    """

    def __init__(self) -> None:
        """
        Initializes the LinearOrLogisticModel. The appropriate model (LinearRegression or LogisticRegression)
        will be instantiated in the fit method.
        """
        self.model = LinearRegression()
        self.label_encoder = None
        self.preprocessor = None

        
    def fit(self, features: pd.DataFrame, labels: pd.Series) -> None:
        """
        Automatically detects feature types (numeric or categorical) and trains either a LinearRegression
        model (for numeric labels) or LogisticRegression model (for categorical labels) using the provided
        features and labels, applying necessary preprocessing.

        Args:
            features (pd.DataFrame): A DataFrame containing the input features.
            labels (pd.Series): A Series containing the target labels.
        """
        # Detecta colunas numéricas e categóricas automaticamente
        numeric_features = features.select_dtypes(include=[np.number]).columns.tolist()
        categorical_features = features.select_dtypes(exclude=[np.number]).columns.tolist()

        # Preprocessing for numeric features
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler())
        ])

        # Preprocessing for categorical features
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])

        # Column transformer que aplica as transformações às colunas numéricas e categóricas
        self.preprocessor = ColumnTransformer(transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

        # Aplica o pré-processamento nos dados de entrada
        features = self.preprocessor.fit_transform(features)

        # Verifica se o problema é de regressão ou classificação com base nos labels
        if not pd.api.types.is_numeric_dtype(labels):
            self.label_encoder = LabelEncoder()
            labels = self.label_encoder.fit_transform(labels)

        self.model.fit(features, labels)


    def predict(self, features: pd.DataFrame) -> np.ndarray:
        """
        Faz previsões com base nos recursos fornecidos, utilizando o modelo treinado.

        Args:
            features (pd.DataFrame): Um DataFrame contendo os recursos de entrada.

        Returns:
            np.ndarray: Um array numpy contendo os valores previstos. Se for classificação, os labels são decodificados.
        """
        # Aplica o pré-processamento nos dados de entrada antes de realizar a previsão
        features = self.preprocessor.transform(features)

        # Faz as previsões
        predictions = self.model.predict(features)

        # Se for classificação, decodifica os labels de volta para o formato original
        if self.label_encoder is not None:
            predictions = self.label_encoder.inverse_transform(predictions)

        return predictions
