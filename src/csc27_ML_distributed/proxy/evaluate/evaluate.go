package evaluate

import (
	"encoding/base64"
	"encoding/json"
	"log"
	"proxy/connect"
	"sync"

	"github.com/kolo/xmlrpc"
)

type Metrics map[string]float64

var models [][]byte
var metrics []Metrics
var mutex sync.Mutex
var app_err error

func initVars() {
    models = make([][]byte, 0)
    metrics = make([]Metrics, 0)
    app_err = nil
}

func receiveModel(client *xmlrpc.Client, wg *sync.WaitGroup) {
    defer wg.Done() // Ensure the WaitGroup is decremented

    log.Println("Receiving models...")
    var base64Data string
    if err := client.Call("send_model", nil, &base64Data); err != nil {
        log.Println("error during sending model:", err)
        return // Log the error and continue
    }
    model, err := base64.StdEncoding.DecodeString(base64Data)
    if err != nil {
        log.Println("fit must be called first; error:", err)
        return // Log the error and continue
    }
    mutex.Lock()
    models = append(models, model)
    mutex.Unlock()
}

func evaluate(client *xmlrpc.Client, wg *sync.WaitGroup) {
    defer wg.Done() // Ensure the WaitGroup is decremented

    log.Println("Getting evaluation metrics...")
    var result string

    if err := client.Call("evaluate", models, &result); err != nil {
        log.Println("error during evaluation:", err)
        return // Log the error and continue
    }

    var metric Metrics
    if err := json.Unmarshal([]byte(result), &metric); err != nil {
        log.Println("error during metric unmarshaling:", err)
        return // Log the error and continue
    }

    log.Println("Here evaluate")

    mutex.Lock()
    metrics = append(metrics, metric)
    mutex.Unlock()
}

func aggregate(metrics []Metrics) Metrics {
    aggregated := make(Metrics)
    count := float64(len(metrics))

    for _, metric := range metrics {
        for name := range metric {
            aggregated[name] = 0
        }
    }

    for _, metric := range metrics {
        for name, value := range metric {
            aggregated[name] += value
        }
    }

    for metric := range aggregated {
        aggregated[metric] /= count
    }

    log.Println("Here aggregated")

    return aggregated
}

func Evaluate() (Metrics, error) {
    var wg sync.WaitGroup
    initVars()
    servers := connect.InitRPCConnections()

    for _, client := range servers.Clients {
        wg.Add(1)
        go func(c *xmlrpc.Client) {
            receiveModel(c, &wg)
        }(client)
    }

    wg.Wait()

    for _, client := range servers.Clients {
        wg.Add(1)
        go func(c *xmlrpc.Client) {
            evaluate(c, &wg)
        }(client)
    }

    wg.Wait()

    aggregated := aggregate(metrics)
    log.Printf("Aggregated metrics:\n%v\n\n", aggregated)

    return aggregated, nil
}