# Usa uma versão correta da imagem base do Golang
FROM golang:1.23.0-alpine3.20

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos necessários para o container
COPY ./data/train_A.csv ./data/train.csv
COPY ./models/ ./models/
COPY ./src/ ./src/
COPY ./Makefile ./Makefile
COPY ./requirements.txt ./requirements.txt
COPY ./serverML.py ./serverML.py
COPY ./scripts/start.sh ./start.sh

# Dá permissão de execução ao script start.sh
RUN chmod +x ./start.sh

# Instala make e Python com pip, já que você tem um requirements.txt
RUN apk add --no-cache bash make python3 py3-pip

# Instala o GCC e dependências para compilar pacotes Python como scikit-learn
RUN apk add --no-cache gcc g++ musl-dev libc-dev linux-headers python3-dev

# Executa o make install para instalar dependências do projeto Go
RUN make install

RUN source ./.venv/bin/activate

# Define o comando de inicialização
CMD ["./start.sh"]
