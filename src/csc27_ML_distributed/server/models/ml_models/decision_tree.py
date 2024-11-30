from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from csc27_ML_distributed.server.models.base import BaseModel, BasePreprocessor


class DecisionTreeRegressorModel(BaseModel):
    def __init__(
        self, preprocessor: BasePreprocessor, max_depth: int, max_leaf_nodes: int
    ) -> None:
        super().__init__(
            DecisionTreeRegressor(max_depth=max_depth, max_leaf_nodes=max_leaf_nodes),
            preprocessor,
        )


class DecisionTreeClassifierModel(BaseModel):
    def __init__(
        self, preprocessor: BasePreprocessor, max_depth: int, max_leaf_nodes: int
    ) -> None:
        super().__init__(
            DecisionTreeClassifier(max_depth=max_depth, max_leaf_nodes=max_leaf_nodes),
            preprocessor,
        )
