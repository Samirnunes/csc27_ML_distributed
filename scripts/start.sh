#!/bin/bash

# Inicia o primeiro processo
echo "Starting the local inference server ..."
python ./serverML.py &

# Aguarda 3 segundos antes de iniciar o segundo processo
sleep 3

# Inicia o segundo processo
echo "Iniciando o segundo processo..."
python ./example_client.py &

# Aguardando os processos para que o container continue rodando
wait
