from typing import Self
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    r2_score,
    mean_absolute_error,
    mean_squared_error,
    mean_squared_log_error,
)
from pydantic.dataclasses import dataclass

@dataclass
class MLRegressionMetrics:
    r2_score: float = 0.0
    mean_absolute_error: float = 0.0
    mean_squared_error: float = 0.0
    mean_squared_log_error: float = 0.0
    
    @staticmethod
    def from_labels(y_true: pd.DataFrame, y_pred: pd.DataFrame) -> Self:
        return MLRegressionMetrics(
            r2_score(y_true, y_pred),
            mean_absolute_error(y_true, y_pred),
            mean_squared_error(y_true, y_pred),
            mean_squared_log_error(y_true, y_pred)
        )
    
@dataclass
class MLClassificationMetrics:
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    
    @staticmethod
    def from_labels(y_true: pd.DataFrame, y_pred: pd.DataFrame) -> Self:
        return MLClassificationMetrics(
            accuracy_score(y_true, y_pred),
            precision_score(y_true, y_pred),  
            recall_score(y_true, y_pred),  
            f1_score(y_true, y_pred),  
        )