from typing import List

from csc27_ML_distributed.server.models.base import BaseModel
from csc27_ML_distributed.server.models.ml_models import (
    DecisionTreeClassifierModel,
    DecisionTreeRegressorModel,
    DummyModel,
    LinearClassifierModel,
    LinearRegressorModel,
)


class MLModelsDict:
    _MODELS = {
        "dummy": DummyModel(),
        "linear-classifier": LinearClassifierModel(),
        "linear-regressor": LinearRegressorModel(),
        "tree-classifier": DecisionTreeClassifierModel(),
        "tree-regressor": DecisionTreeRegressorModel(),
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
