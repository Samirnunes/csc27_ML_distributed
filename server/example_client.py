import xmlrpc.client

# Conecta-se ao servidor XML-RPC
server = xmlrpc.client.ServerProxy("http://localhost:8000/")

# 1. Inicializa o modelo Dummy no servidor
print("Inicializando o modelo Dummy...")
server.initModel("dummy")

# 2. Dados de treino
features_train = {
    "feature1": [1.0, 2.0, 3.0, 4.0, 5.0],
    "feature2": [10.0, 20.0, 30.0, 40.0, 50.0]
}

labels_train = [100, 200, 300, 400, 500]

print("Treinando o modelo com os dados de treino...")
server.fit(features_train, labels_train)

# 3. Dados para previsão
features_test = {
    "feature1": [6.0, 7.0],
    "feature2": [60.0, 70.0]
}

print("Fazendo previsões com novos dados...")
predictions = server.predict(features_test)

# 4. Exibe as previsões
print("Previsões recebidas do servidor:", predictions)
