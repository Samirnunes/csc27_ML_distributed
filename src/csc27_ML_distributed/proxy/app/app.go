package main

import (
	"encoding/csv"
	"log"
	"os"
	"proxy/evaluate"
	"proxy/fit"
	"proxy/predict"
)



func main(){
	file, err := os.Open("test.csv")
	if err != nil {
		log.Fatalf("Error opening file: %v", err)
	}
	defer file.Close()

	reader := csv.NewReader(file)

	headers, err := reader.Read()
	if err != nil {
		log.Fatalf("Error reading headers: %v", err)
	}

	dataRow, err := reader.Read()
	if err != nil {
		log.Fatalf("Error reading data row: %v", err)
	}

	result := make(map[string]interface{})
	for i, header := range headers {
		if i < len(dataRow) {
			result[header] = dataRow[i]
		} else {
			result[header] = nil
		}
	}
	log.Println("Connecting to ML servers: A, B, C")

	fit.Fit()
	predict.Predict(result)
	evaluate.Evaluate()
}