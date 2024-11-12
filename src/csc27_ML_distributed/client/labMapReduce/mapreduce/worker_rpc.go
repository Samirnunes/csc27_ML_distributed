package mapreduce

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"os"
	"time"
)

// RPC - RunMap
// Run the map operation defined in the task and return when it's done.
func (worker *Worker) RunMap(args *RunArgs, _ *struct{}) error {
	var (
		err       error
		buffer    []byte
		mapResult []KeyValue
	)

	if worker.shouldFail(false) {
		mapResult = make([]KeyValue, 0)
		storeLocal(worker.task, args.Id, mapResult)
		// Allow descriptors to be closed.
		time.Sleep(time.Duration(100) * time.Millisecond)
		panic("Induced failure.")
	}

	log.Printf("Running map id: %v, path: %v\n", args.Id, args.FilePath)

	if buffer, err = ioutil.ReadFile(args.FilePath); err != nil {
		log.Fatal(err)
	}

	mapResult = worker.task.Map(buffer)
	storeLocal(worker.task, args.Id, mapResult)
	return nil
}

// RPC - RunMap
// Run the reduce operation defined in the task and return when it's done.
func (worker *Worker) RunReduce(args *RunArgs, _ *struct{}) error {
	log.Printf("Running reduce id: %v, path: %v\n", args.Id, args.FilePath)

	var (
		err          error
		reduceResult []KeyValue
		file         *os.File
		fileEncoder  *json.Encoder
	)

	if worker.shouldFail(false) {
		if file, err = os.Create(resultFileName(args.Id)); err != nil {
			log.Fatal(err)
		}
		file.Sync()
		file.Close()
		// Allow descriptors to be closed.
		time.Sleep(time.Duration(100) * time.Millisecond)
		panic("Induced failure.")
	}

	data := loadLocal(args.Id)

	reduceResult = worker.task.Reduce(data)

	if file, err = os.Create(resultFileName(args.Id)); err != nil {
		log.Fatal(err)
	}

	fileEncoder = json.NewEncoder(file)

	for _, value := range reduceResult {
		fileEncoder.Encode(value)
	}

	file.Close()
	return nil
}

// RPC - Done
// Will be called by Master when the task is done.
func (worker *Worker) Done(_ *struct{}, _ *struct{}) error {
	log.Println("Done.")
	defer func() {
		close(worker.done)
	}()
	return nil
}
