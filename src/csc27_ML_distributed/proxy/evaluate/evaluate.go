package evaluate

import (
	"encoding/base64"
	"encoding/json"
	"log"
	"proxy/connect"
)

type Metrics map[string]float64

func Aggregate(metrics map[string]Metrics) Metrics {
	aggregated := make(Metrics)
	count := float64(len(metrics))

	for _, metricValues := range metrics {
		for metric := range metricValues {
			aggregated[metric] = 0
		}
		break
	}

	for _, metricValues := range metrics {
		for metric, value := range metricValues {
			aggregated[metric] += value
		}
	}

	for metric := range aggregated {
		aggregated[metric] /= count
	}

	return aggregated
}

func Evaluate() Metrics {
	servers := connect.InitRPCConnections()

	metrics := make(map[string]Metrics)
	var models [][]byte

	log.Println("Receiving models...")
	for _, client := range servers.Clients {
		defer client.Close()
		var base64Data string
		if err := client.Call("send_model", nil, &base64Data); err != nil {
			log.Fatalf("Error during sending model: %v", err)
		}
		modelData, err := base64.StdEncoding.DecodeString(base64Data)
		if err != nil {
			log.Fatalf("Failed to decode base64 data: %v", err)
		}

		models = append(models, modelData)
	}

	log.Println("Getting evaluation metrics...")
	for i, client := range servers.Clients {
		var result string

		if err := client.Call("evaluate", models, &result); err != nil {
			log.Fatalf("Error during evaluation: %v", err)
		}

		var metric Metrics
		if err := json.Unmarshal([]byte(result), &metric); err != nil {
			log.Fatalf("Error during metric unmarshaling: %v", err)
		}
		metrics[servers.ServerNames[i]] = metric
	}

	aggregated := Aggregate(metrics)
	log.Printf("Aggregated metrics:\n%v\n\n", aggregated)
	return aggregated
}