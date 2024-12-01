from pathlib import Path
from time import time

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

from csc27_ML_distributed.server.config import MLRegressionMetrics
from csc27_ML_distributed.server.log import logger
from csc27_ML_distributed.server.models.preprocessor import MetroPreprocessor

begin = time()

preprocessor = MetroPreprocessor()

model: RandomForestRegressor = RandomForestRegressor(
    n_estimators=4, max_depth=3, max_leaf_nodes=10, bootstrap=False
)

A: pd.DataFrame = pd.read_csv(
    Path("../../data/metro_reduced/A") / Path("data.csv"), index_col=[0]
)
B: pd.DataFrame = pd.read_csv(
    Path("../../data/metro_reduced/B") / Path("data.csv"), index_col=[0]
)
C: pd.DataFrame = pd.read_csv(
    Path("../../data/metro_reduced/C") / Path("data.csv"), index_col=[0]
)
D: pd.DataFrame = pd.read_csv(
    Path("../../data/metro_reduced/D") / Path("data.csv"), index_col=[0]
)

data = pd.concat([A, B, C, D], axis=0)

metric_objs = []

features: pd.DataFrame = data.drop("Oil_temperature", axis=1)
labels: pd.DataFrame = data["Oil_temperature"]
X_train, X_test, y_train, y_test = train_test_split(
    features,
    labels,
    test_size=0.3,
    random_state=0,
)
y_train = pd.Series(y_train)
y_test = pd.Series(y_test)
model.fit(preprocessor.fit_transform(X_train), y_train)
y_pred = model.predict(preprocessor.transform(X_test))
metric_objs.append(MLRegressionMetrics.from_labels(y_test, y_pred))

end = time()

logger.info(f"Sequential time: {end - begin}")
