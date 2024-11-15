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

func initVars() {
	models = make([][]byte, 0)
	metrics = make([]Metrics, 0)
}

func receiveModel(client *xmlrpc.Client, wg *sync.WaitGroup) {
	log.Println("Receiving models...")
	var base64Data string
	if err := client.Call("send_model", nil, &base64Data); err != nil {
		log.Fatalf("Error during sending model: %v", err)
	}
	model, err := base64.StdEncoding.DecodeString(base64Data)
	if err != nil {
		log.Fatalf("Failed to decode base64 data: %v", err)
	}
	mutex.Lock()
	models = append(models, model)
	mutex.Unlock()
	wg.Done()
}

func evaluate(client *xmlrpc.Client, wg *sync.WaitGroup) {
	log.Println("Getting evaluation metrics...")
	var result string

	if err := client.Call("evaluate", models, &result); err != nil {
		log.Fatalf("Error during evaluation: %v", err)
	}

	var metric Metrics
	if err := json.Unmarshal([]byte(result), &metric); err != nil {
		log.Fatalf("Error during metric unmarshaling: %v", err)
	}
	mutex.Lock()
	metrics = append(metrics, metric)
	mutex.Unlock()
	wg.Done()
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

	return aggregated
}

func Evaluate() Metrics {
	var wg sync.WaitGroup
	initVars()
	servers := connect.InitRPCConnections()

	for _, client := range servers.Clients {
		defer client.Close()
		wg.Add(1)
		go receiveModel(client, &wg) 
	}

	wg.Wait()

	for _, client := range servers.Clients {
		wg.Add(1)
		go evaluate(client, &wg)
	}

	wg.Wait()

	aggregated := aggregate(metrics)
	log.Printf("Aggregated metrics:\n%v\n\n", aggregated)
	return aggregated
}