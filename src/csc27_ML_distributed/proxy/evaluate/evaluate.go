package evaluate

import (
	"encoding/base64"
	"encoding/json"
	"errors"
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

func receiveModel(client *xmlrpc.Client, wg *sync.WaitGroup) error {
	log.Println("Receiving models...")
	var base64Data string
	if err := client.Call("send_model", nil, &base64Data); err != nil {
		return errors.New("error during sending model: " + err.Error())
	}
	model, err := base64.StdEncoding.DecodeString(base64Data)
	if err != nil {
		return errors.New("fit must be called first; error: " + err.Error())
	}
	mutex.Lock()
	models = append(models, model)
	mutex.Unlock()
	wg.Done()
	return nil
}

func evaluate(client *xmlrpc.Client, wg *sync.WaitGroup) error {
	log.Println("Getting evaluation metrics...")
	var result string

	if err := client.Call("evaluate", models, &result); err != nil {
		return errors.New("error during evaluation: " + err.Error())
	}

	var metric Metrics
	if err := json.Unmarshal([]byte(result), &metric); err != nil {
		return errors.New("error during metric unmarshaling: " + err.Error())
	}
	mutex.Lock()
	metrics = append(metrics, metric)
	mutex.Unlock()
	wg.Done()
	return nil
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

func Evaluate() (Metrics, error) {
	var wg sync.WaitGroup
	initVars()
	servers := connect.InitRPCConnections()

	for _, client := range servers.Clients {
		defer client.Close()
		wg.Add(1)
		go func(c *xmlrpc.Client) {
			if err := receiveModel(c, &wg); err != nil {
				log.Println("error during receiveModel:", err)
				app_err = err
				wg.Done()
			}
		}(client)
	}

	wg.Wait()

	if app_err != nil {
		return make(Metrics), app_err
	}

	// Second phase: evaluate models
	for _, client := range servers.Clients {
		wg.Add(1)
		go func(c *xmlrpc.Client) {
			if err := evaluate(c, &wg); err != nil {
				log.Println("error during evaluate:", err)
				app_err = err
				wg.Done()
			}
		}(client)
	}

	wg.Wait()

	if app_err != nil {
		return make(Metrics), app_err
	}

	aggregated := aggregate(metrics)
	log.Printf("Aggregated metrics:\n%v\n\n", aggregated)

	return aggregated, nil
}