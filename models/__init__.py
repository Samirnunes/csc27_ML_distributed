from .base import BaseModel
from .dummy import DummyModel
from .linearRegression import LinearOrLogisticModel

MLModel = {
    "dummy": DummyModel,
    "linearRegression": LinearOrLogisticModel
}