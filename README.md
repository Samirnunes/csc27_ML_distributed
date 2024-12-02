# [CSC-27 Exam] Distributed Machine Learning (ML)

## Schema

<p align="center">
    <img width="600" src="./docs/schema.png" alt="schema">
<p>

## Running

Firstly, execute Docker (on Windows, you must open Docker Desktop).

Then, go to project's root directory (where the `docker-compose.yml` file is) and run the following command on terminal:

- `docker compose up --build`

This will setup ML `servers` and a `proxy`, which will be used to call the app.

Finally, you can test the endpoints:

- (POST) `localhost:80/v1/ml-distributed/fit`

- (POST) `localhost:80/v1/ml-distributed/evaluate`

- (POST) `localhost:80/v1/ml-distributed/predict`

`fit` must be run first so `evaluate` and `predict` can work. Besides, for `predict` you must pass the features' values as parameters to the request.

### Notes on Testing

Testing commands using `curl`:

- Fit test: `curl -X POST http://localhost:80/v1/ml-distributed/fit`

- Evaluate test: `curl -X POST http://localhost:80/v1/ml-distributed/evaluate`

- Predict test: `curl -X POST http://localhost:80/v1/ml-distributed/predict -H "Content-Type: application/json" -d @./data/house_pricing/other/one_prediction_house_pricing_test.json`

## Fault Tolerance

The fault tolerance handling is done in two separate steps with the objective of making the system robust and resilient to failures.

### Step 1: Fault Tolerance in the ML Servers

If a ML server fails, the proxy will detect, log the error, and continue without stopping the entire process. With this procedure, the system will be able to handle the failure of one or more ML servers with the consequence of having a lower number of weak learners, which could affect the model's performance. Nonetheless, the system will still be able to make predictions and evaluate the model. The error can occur in each step of the process, such as fitting, evaluating, and predicting. Here's the summary of the fault tolerance handling in the ML servers:

1. The proxy sends the request to the ML server;
2. If the ML server fails, the proxy identifies the error via the client.Call method;
3. The error is logged and informed to the user;
4. The proxy continues to the next steps, if any, without crashing or stopping the entire process.

### Step 2: Fault Tolerance in the Proxy Server

The failure of the proxy server is handled by redundancy. A load-balancing mechanism is implemented using nginx, which will redirect the requests to the available servers. If one server fails, the load balancer will redirect the requests to the other servers. The failure identification is via timeout. This ensures that, if the proxy server fails, regardless of the stage of the process (fitting, evaluating, or predicting), the system will still be able to handle the requests. Here's the summary of the fault tolerance handling in the proxy server:

1. The client sends a request to the proxy server;
2. The nginx load balancer redirects the request to the available proxy server;
3. If the proxy server is not reached within the timeout, the request is redirected to the other proxy server and the failure is logged;
4. The process is executed as expected, and the response is sent back to the client.

It is important to notice that the fault tolerance handling is done in two separate and **independent** steps, which ensures that the system is robust and resilient to failures. Both of the failure handling mechanisms are implemented in the code and can be tested by stopping the ML servers and the proxy server.

## References

- In `docs` folder.
