package predict

import (
	"encoding/json"
	"log"
	"proxy/connect"
	"sync"

	"github.com/kolo/xmlrpc"
)

type PredictResult struct {
	Prediction interface{}
	ProblemType string     
}

var predictions []PredictResult
var mutex sync.Mutex

func initVars() {
	predictions = make([]PredictResult, 0)
}

func getPrediction(client *xmlrpc.Client, features map[string]interface{}, wg *sync.WaitGroup) {
	var result string

	if err := client.Call("predict", features, &result); err != nil {
		log.Fatalf("Error during prediction: %v", err)
	}

	var prediction PredictResult
	if err := json.Unmarshal([]byte(result), &prediction); err != nil {
		log.Fatalf("Error unmarshaling prediction result: %v", err)
	}

	mutex.Lock()
	predictions = append(predictions, prediction)
	mutex.Unlock()
	wg.Done()
}

// Helper function to calculate the most frequent prediction (for classification problems)
func mostFrequentPrediction(predictions []PredictResult) interface{} {
	counts := make(map[interface{}]int)
	for _, pred := range predictions {
		counts[pred.Prediction.([]float64)[0]]++
	}

	var maxCount int
	var mostFrequent interface{}
	for pred, count := range counts {
		if count > maxCount {
			maxCount = count
			mostFrequent = pred
		}
	}

	return mostFrequent
}

func aggregate(allPredictions []PredictResult) PredictResult {
	var aggregated PredictResult
	if len(allPredictions) > 0 {
		problemType := allPredictions[0].ProblemType
		if problemType == "regression" {
			var sum float64 = 0.0
			for _, pred := range allPredictions {
				log.Println(pred.Prediction)
				sum += pred.Prediction.([]interface{})[0].(float64)
			}
			aggregated.Prediction = sum / float64(len(allPredictions))
		} else if problemType == "classification" {
			aggregated.Prediction = mostFrequentPrediction(allPredictions)
		}
		aggregated.ProblemType = problemType
		} else {
			log.Fatalf("Error: 'problem_type' not found in predictions")
		}

	return aggregated
}

func Predict(features map[string]interface{}) PredictResult {
	var wg sync.WaitGroup
	initVars()
	servers := connect.InitRPCConnections()

	log.Println("Getting predictions...")

	for _, client := range servers.Clients {
		wg.Add(1)
		defer client.Close()
		go getPrediction(client, features, &wg)
	}

	wg.Wait()

	log.Println(predictions)

	aggregated := aggregate(predictions)
	log.Printf("Aggregated prediction:\n%v\n\n", aggregated)
	return aggregated
}