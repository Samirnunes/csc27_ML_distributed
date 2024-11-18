import os
import json
from typing import Dict
from csc27_ML_distributed.server.log import logger
from xmlrpc.client import ServerProxy

# Conecta-se ao servidor XML-RPC

logger.info("Connecting to ML servers: A, B, C")
servers_names = ["a", "b", "c"]
server_a = ServerProxy("http://localhost:80/")
server_b = ServerProxy("http://localhost:81/")
server_c = ServerProxy("http://localhost:82/")

servers_names = list(map(lambda x: "server_" + x, servers_names))
servers = [server_a, server_b, server_c]
models = []
metrics = dict.fromkeys(servers_names)

logger.info("Fitting server's models...")
logger.info("Receiving models...")
for server in servers:
    server.fit()
    models.append(server.send_model())

logger.info("Getting evaluation metrics...")
for i, server in enumerate(servers):
    metrics[servers_names[i]] = json.loads(server.evaluate(models))

def aggregate(metrics: Dict[str, Dict[str, float]]):
    aggregated = dict.fromkeys(
        list(metrics.values())[0].keys(), 0
    )
    for metrics_dict in metrics.values():
        for metric, value in metrics_dict.items():
            aggregated[metric] += value
    for metric in metrics_dict.keys():
        aggregated[metric]= aggregated[metric] / len(metrics)

    return aggregated

logger.info(f"\nAggregated metrics:\n\n{aggregate(metrics)}")
