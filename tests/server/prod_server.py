import json
from typing import Dict
from csc27_ML_distributed.server.log import logger
from xmlrpc.client import ServerProxy

# Conecta-se ao servidor XML-RPC

logger.info("Connecting to ML servers: A, B, C")
server_a = ServerProxy("http://localhost:80/")
server_b = ServerProxy("http://localhost:81/")
server_c = ServerProxy("http://localhost:82/")

logger.info("Fitting server's models...")
server_a.fit()
server_b.fit()
server_c.fit()

logger.info("Receiving models...")
model_a = server_a.send_model()
model_b = server_b.send_model()
model_c = server_c.send_model()

models = [model_a, model_b, model_c]

logger.info("Getting evaluation metrics...")
metrics_a = server_a.evaluate(models)
metrics_b = server_b.evaluate(models)
metrics_c = server_c.evaluate(models)

logger.info("Evaluating metrics...")
metrics = {
    "Server A": json.loads(metrics_a),
    "Server B": json.loads(metrics_b),
    "Server C": json.loads(metrics_c),
}


def aggregate(metrics: Dict[str, Dict[str, float]]):
    aggregated = dict.fromkeys(
        metrics.keys(), dict.fromkeys(list(metrics.values())[0].keys(), 0)
    )
    for server, metrics_dict in metrics.items():
        for metric, value in metrics_dict.items():
            aggregated[server][metric] += value
    for server in metrics.keys():
        for metric in metrics_dict.keys():
            aggregated[server][metric] = aggregated[server][metric] / len(metrics)

    return aggregated

logger.info(f"\nAggregated metrics:\n\n{aggregate(metrics)}")
