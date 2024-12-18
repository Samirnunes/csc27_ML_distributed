package predict

import (
	"encoding/json"
	"errors"
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
var app_err error

func initVars() {
	predictions = make([]PredictResult, 0)
	app_err = nil
}

func getPrediction(client *xmlrpc.Client, features map[string]interface{}, wg *sync.WaitGroup) error {
    defer wg.Done() // Ensure the WaitGroup is decremented

    var result string

    if err := client.Call("predict", features, &result); err != nil {
        log.Println("error during prediction:", err)
        return nil // Log the error and continue
    }

    var prediction PredictResult
    if err := json.Unmarshal([]byte(result), &prediction); err != nil {
        log.Println("fit must be called first; error:", err)
        return nil // Log the error and continue
    }

    mutex.Lock()
    predictions = append(predictions, prediction)
    mutex.Unlock()
    return nil
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

func aggregate(allPredictions []PredictResult) (PredictResult, error) {
	var aggregated PredictResult
	if len(allPredictions) == 0 {
		return aggregated, errors.New("error: no predictions found")
	}

	problemType := allPredictions[0].ProblemType
	if problemType == "regression" {
		var sum float64 = 0.0
		for _, pred := range allPredictions {
			if predictionValues, ok := pred.Prediction.([]interface{}); ok {
				sum += predictionValues[0].(float64)
			} else {
				return aggregated, errors.New("error: invalid prediction format in regression")
			}
		}
		aggregated.Prediction = sum / float64(len(allPredictions))
	} else if problemType == "classification" {
		aggregated.Prediction = mostFrequentPrediction(allPredictions)
	} else {
		return aggregated, errors.New("error: unknown problem type")
	}
	aggregated.ProblemType = problemType
	return aggregated, nil
}

func Predict(features map[string]interface{}) (PredictResult, error) {
	var wg sync.WaitGroup
	initVars()
	servers := connect.InitRPCConnections()

	log.Println("Getting predictions...")

	for _, client := range servers.Clients {
		wg.Add(1)
		defer client.Close()
		go func(c *xmlrpc.Client) {
			if err := getPrediction(c, features, &wg); err != nil {
				log.Println("error during getPrediction:", err)
				app_err = err
				wg.Done()
			}
		}(client)
	}

	wg.Wait()

	if app_err != nil {
		return PredictResult{}, app_err
	}

	log.Println(predictions)

	aggregated, err := aggregate(predictions)
	if err != nil {
		return PredictResult{}, err
	}

	log.Printf("Aggregated prediction:\n%v\n\n", aggregated)
	return aggregated, nil
}
