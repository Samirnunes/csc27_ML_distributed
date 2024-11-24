from typing import List

from csc27_ML_distributed.server.models.base import BaseModel
from csc27_ML_distributed.server.models.ml_models import (
    DecisionTreeClassifierModel,
    DecisionTreeRegressorModel,
    LinearClassifierModel,
    LinearRegressorModel,
)
from csc27_ML_distributed.server.models.preprocessor import HousePricingPreprocessor


class _MLModels:
    _MODELS = {
        "house-pricing-linear-classifier": LinearClassifierModel(
            HousePricingPreprocessor()
        ),
        "house-pricing-linear-regressor": LinearRegressorModel(
            HousePricingPreprocessor()
        ),
        "house-pricing-tree-classifier": DecisionTreeClassifierModel(
            HousePricingPreprocessor(), 3, 10
        ),
        "house-pricing-tree-regressor": DecisionTreeRegressorModel(
            HousePricingPreprocessor(), 3, 10
        ),
    }

    def __getitem__(self, key: str) -> BaseModel:
        return self._MODELS[key]

    def __contains__(self, key: str) -> bool:
        return key in self._MODELS

    def __repr__(self):
        return repr(self._MODELS)

    def values(self) -> List[BaseModel]:
        return list(self._MODELS.values())

    def keys(self) -> List[str]:
        return list(self._MODELS.keys())


ML_MODELS = _MLModels()
