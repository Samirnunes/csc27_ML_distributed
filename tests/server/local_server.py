from xmlrpc.client import ServerProxy

import pandas as pd

df_test = pd.read_csv("../../data/other/test.csv")

# Dados para previsão
features_test = df_test.to_dict(orient="list")

# Conecta-se ao servidor XML-RPC
server = ServerProxy("http://localhost:8080/")

server.set_model("tree-regressor")

# Treina o modelo com os dados de treino
print("Treinando o modelo com os dados de treino...")
server.fit()

# Faz previsões com os dados de teste
print("Fazendo previsões com novos dados...")
predictions = server.predict(features_test)

model_data = server.send_model()

print(server.evaluate([model_data]))

# 4. Exibe as previsões
# print("Previsões recebidas do servidor:", predictions)
