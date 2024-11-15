package main

import (
	"encoding/json"
	"log"
	"net/http"
	"proxy/evaluate"
	"proxy/fit"
	"proxy/predict"

	"github.com/gorilla/mux"
)

// Handlers for the endpoints

// Fit handler
func FitHandler(w http.ResponseWriter, r *http.Request) {
	fit.Fit()

	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Models trained successfully"))
}

// Evaluate handler
func EvaluateHandler(w http.ResponseWriter, r *http.Request) {
	metrics := evaluate.Evaluate()

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	if err := json.NewEncoder(w).Encode(metrics); err != nil {
		log.Fatalf("Error encoding response: %v", err)
	}
}

// Predict handler
func PredictHandler(w http.ResponseWriter, r *http.Request) {
	var features map[string]interface{}

	if err := json.NewDecoder(r.Body).Decode(&features); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	result := predict.Predict(features)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	if err := json.NewEncoder(w).Encode(result); err != nil {
		log.Fatalf("Error encoding response: %v", err)
	}
}

func main() {
	r := mux.NewRouter()

	r.HandleFunc("/v1/ml-distributed/fit", FitHandler).Methods("POST")
	r.HandleFunc("/v1/ml-distributed/evaluate", EvaluateHandler).Methods("POST")
	r.HandleFunc("/v1/ml-distributed/predict", PredictHandler).Methods("POST")

	log.Println("Server started at 0.0.0.0:80")
	log.Fatal(http.ListenAndServe("0.0.0.0:80", r))
}