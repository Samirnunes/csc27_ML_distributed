package main

import (
	"encoding/json"
	"log"
	"net/http"
	"proxy/connect"
	"proxy/evaluate"
	"proxy/fit"
	"proxy/predict"

	"github.com/gorilla/mux"
)

var Servers = connect.InitRPCConnections()

// Handlers for the endpoints

// Fit handler
func FitHandler(w http.ResponseWriter, r *http.Request) {
	fit.Fit()

	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Models trained successfully"))
}

// Evaluate handler
func EvaluateHandler(w http.ResponseWriter, r *http.Request) {
	aggregated, err := evaluate.Evaluate()
	if err != nil {
		http.Error(w, "Failed to evaluate models: "+err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	if err := json.NewEncoder(w).Encode(aggregated); err != nil {
		http.Error(w, "Failed to encode response: "+err.Error(), http.StatusInternalServerError)
	}
}

// Predict handler
func PredictHandler(w http.ResponseWriter, r *http.Request) {
	var features map[string]interface{}
	if err := json.NewDecoder(r.Body).Decode(&features); err != nil {
		http.Error(w, "Failed to decode request body: "+err.Error(), http.StatusBadRequest)
		return
	}

	aggregated, err := predict.Predict(features)
	if err != nil {
		http.Error(w, "Failed to get prediction: "+err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	if err := json.NewEncoder(w).Encode(aggregated); err != nil {
		http.Error(w, "Failed to encode response: "+err.Error(), http.StatusInternalServerError)
	}
}

func main() {
	r := mux.NewRouter()

	r.HandleFunc("/v1/ml-distributed/fit", FitHandler).Methods("POST")
	r.HandleFunc("/v1/ml-distributed/evaluate", EvaluateHandler).Methods("POST")
	r.HandleFunc("/v1/ml-distributed/predict", PredictHandler).Methods("POST")

	log.Println("Proxy started at proxy:80")
	log.Fatal(http.ListenAndServe("proxy:80", r))
}
