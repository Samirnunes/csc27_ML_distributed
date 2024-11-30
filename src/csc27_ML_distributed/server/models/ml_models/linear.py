from sklearn.linear_model import LinearRegression, LogisticRegression

from csc27_ML_distributed.server.models.base import BaseModel, BasePreprocessor


class LinearRegressorModel(BaseModel):
    def __init__(self, preprocessor: BasePreprocessor) -> None:
        super().__init__(LinearRegression(), preprocessor)


class LinearClassifierModel(BaseModel):
    def __init__(self, preprocessor: BasePreprocessor) -> None:
        super().__init__(LogisticRegression(), preprocessor)
