from typing import List

from csc27_ML_distributed.server.models.base import BaseModel
from csc27_ML_distributed.server.models.ml_models import (
    DecisionTreeRegressorModel,
    LinearRegressorModel,
)
from csc27_ML_distributed.server.models.preprocessor import (
    HousePricingPreprocessor,
    MetroPreprocessor,
)


class _MLModels:
    _MODELS = {
        "house-pricing-linear-regressor": LinearRegressorModel(
            HousePricingPreprocessor()
        ),
        "house-pricing-tree-regressor": DecisionTreeRegressorModel(
            HousePricingPreprocessor(), 3, 10
        ),
        "metro-tree-regressor": DecisionTreeRegressorModel(MetroPreprocessor(), 3, 10),
    }

    def __getitem__(self, key: str) -> BaseModel:
        return self._MODELS[key]

    def __contains__(self, key: str) -> bool:
        return key in self._MODELS

    def __repr__(self) -> str:
        return repr(self._MODELS)

    def values(self) -> List[BaseModel]:
        return list(self._MODELS.values())

    def keys(self) -> List[str]:
        return list(self._MODELS.keys())


ML_MODELS = _MLModels()
