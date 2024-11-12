import pandas as pd
from xmlrpc.client import ServerProxy
 

modelName = "dummy"

df_train = pd.read_csv("./data/train_A.csv")
df_test = pd.read_csv("./data/test.csv")

# Dados de treino
features_train = df_train.drop(columns=['SalePrice']).to_dict(orient='list')
labels_train = df_train['SalePrice'].tolist()

# Dados para previsão
features_test = df_test.to_dict(orient='list')

# Conecta-se ao servidor XML-RPC
server = ServerProxy("http://localhost:8000/")

# Inicializa o modelo Dummy no servidor
print(f"Inicializando o modelo {modelName} ...")
server.initModel(modelName)

# Treina o modelo com os dados de treino
print("Treinando o modelo com os dados de treino...")
server.fit(features_train, labels_train)

# Faz previsões com os dados de teste
print("Fazendo previsões com novos dados...")
predictions = server.predict(features_test)

# 4. Exibe as previsões
print("Previsões recebidas do servidor:", predictions)
