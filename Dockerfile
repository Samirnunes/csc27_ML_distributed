FROM --platform=linux/amd64 python:3.12-slim
FROM golang:1.23.0-alpine3.20

ENV PORT 80
ENV FASTAPI_APP_NAME csc27_ML_distributed/server

EXPOSE ${PORT}
WORKDIR /app

# System update
RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-openbsd curl git wget bash ssh git openssh-client && \
    rm -rf /var/lib/apt/lists/* /var/tmp/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* ./

ARG INSTALL_DEV=false
RUN poetry lock --no-update && \
    bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --only main ; fi"

COPY . ./

CMD ["/bin/bash", "-c", "poetry run python src/${FASTAPI_APP_NAME}/api/app.py"]

# Define o comando de inicialização
#CMD ["./start.sh"]
