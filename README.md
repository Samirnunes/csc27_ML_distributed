# [CSC-27 Exame] Distributed Machine Learning (ML)

## Descrição
O sistema de aprendizado em conjunto distribuído será desenvolvido em Golang, utilizando RPC para a comunicação entre os nós do cluster. Cada nó treinará um modelo fraco com uma porção dos dados disponíveis, de forma independente, e colaborará com os outros nós para realizar inferências e treinamentos de maneira distribuída e coordenada.

Existem duas formas principais de treinamento: global e local. No treinamento global, todos os nós do cluster treinam simultaneamente seus modelos fracos com os dados que possuem. No treinamento local, um nó pode, de forma autônoma, iniciar um novo treinamento caso identifique mudanças significativas em seus dados. Durante o treinamento, o nó ainda deve ser capaz de fornecer inferências utilizando o modelo anterior para não interromper a capacidade de resposta do sistema.

No que diz respeito à inferência, qualquer nó do cluster pode solicitar uma inferência global. Neste caso, todos os nós executam suas previsões localmente e enviam os resultados para o nó solicitante, que os combina para gerar a resposta final. A comunicação entre os nós será feita de forma assíncrona, utilizando RPC, o que garante eficiência e evita bloqueios durante as operações.

Além disso, o sistema será projetado para ser escalável, suportando a adição de novos nós sem degradar significativamente o desempenho. Também será tolerante a falhas, de modo que, se um nó falhar, os outros possam continuar operando normalmente.

Requisitos:

- Training + Validation: todos os servers/workers recebem os modelos treinados nos dados locais de cada um deles e então cada um tira a métrica no seu conjunto de validação e retornar para o central. Após o treino, cada nó fica apenas com o weak learner que foi treinado em seus dados locais.

- Prediction: broadcast das features para todos os servers e cada um retorna, via rpc, as predictions. As predictions são então agregadas pelo nó central, que retorna a resposta.


## [Temporário] Desenvolvimento

Criado o código inicial do projeto. Partindo do simples, foi feito a classe base e 2 modelos simples de ML a serem servidos por um servidor (RPC). Os modelos ficam em `./models`. O arquivo `./models/base.py` contem a classe abstrata base de implementação para os demais modelos (métodos *fit* e *predict*). Os demais arquivos são os rascunhos de modelo ao qual me referi. (`./models/dummy.py` e `./models/linearRegression.py`).

O modelo é servido localmente pelo server `./serverML.py` na porta `8000`. Um exemplo também funcional de como essa comunicação pode ser feita esta em `./example_client.py`.

- Para executar essa parte do projeto:

    Instale o Poetry: https://python-poetry.org/docs/ 
    
    No terminal:

    ```
    > poetry install
    ```

    Terminal 1:

    (Em produção)
    ```
    poetry run python src/csc27_ML_distributed/server/api/app.py
    ```

    ou

    (Rodando local para desenvolvimento)
    ```
    poetry run python src/csc27_ML_distributed/server/api/app.py --local
    ```


    Terminal 2:
    ```
    ### TODO (Golang client implementation)
    ```
    
Na pasta `dados` estão os dados do desafio *Kaggle* [House Prices](https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques) para serem usados na prototipação. Lá, os dados de treinamento foram divididos em A, B e C, já pensando em como nossa aplicação deve funcionar de forma distribuída, cada worker com uma parte dos dados. 

O makefile possui as diretivas `install`, `clean` e `help` e tem por finalidade configurar o ambiente com o *Python* e as dependências necessárias para o projeto listadas em `./requirements.txt`.

Os arquivos `Dockerfile` e `docker-compose.yml` não são funcionais, apenas rascunhos para o que pode ser feito no futuro. Da mesma forma, o que está na pasta `./scripts/` se relaciona ao que é feito na inicialização do container e portanto ainda é não funcional.

Em `./src` estão os códigos do Lab2 dessa disciplina que podem ser reaproveitados para a implementação do projeto.

## [Temporário] Próximos passos

- ### Quem for atacar a confecção dos modelos de ML
    - Criar um novo arquivo na pasta `./models` seguindo o exemplo do `./models/dummy.py` e `./models/linearRegression.py`, que naturalmente já implementam a classe abstrata `baseModel`.

    - Feito isso, incluir o novo modelo no dicionário `MLModel` em `./models/__init__.py` para que possa ser referenciado pelo servidor de modelo.

    - Respeite os tipos esperados de entrada e saída dos métodos `fit` e `predict` da classe base `baseModel`. Uma vez respeitado isso, o desenvolvimento do modelo é livre das outras partes do código.

- ### Quem for atacar o processamento distribuído
    - Criar um arquivo simples em go que faça o gerenciamento de qual modelo e fração de dados será utilizado, ainda pensando em máquina local.

- ### Quem for atacar a comunicação entre os workers e o master
    - Criar um arquivo simples em go que faça a comunicação entre o servidor de modelo e os workers. Caso queira, aproveite o código do laboratório 2 para isso.

    - Quando estiver avançado, dockerize o que puder.

- ### Integração
    - Acompanhar o desenvolvimento, saber de todos os códigos.

- ### Filosofias
    - A documentação é o código, mas *docstrings* fazem bem pro coração.
    - Só existe um *branch* e ela se chama `main`.
    - Para ser respeitado, use *Python* tipado.
    - Sacanagem kkkk esse foi só um pontapé incial, mude o que precisar ser mudado, ainda que tudo.
