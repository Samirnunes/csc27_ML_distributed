from csc27_ML_distributed.server.models.base import BaseModel
from csc27_ML_distributed.server.models.ml import DummyModel, LinearOrLogisticModel

class MLModel:
    _MODELS = {
        "dummy": DummyModel,
        "linear": LinearOrLogisticModel
    }
    
    def __getitem__(self, key: str) -> BaseModel:
        return self._MODELS[key]
    
    def __contains__(self, key: str) -> bool:
        return key in self._MODELS
    
    def __repr__(self):
        return repr(self._MODELS)