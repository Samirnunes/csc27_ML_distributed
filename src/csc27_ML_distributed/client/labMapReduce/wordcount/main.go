package main

import (
	"flag"
	"labMapReduce/mapreduce"
	"log"
	"os"
	"strconv"
)

var (
	// Run mode settings
	mode       = flag.String("mode", "distributed", "Run mode: distributed or sequential")
	nodeType   = flag.String("type", "worker", "Node type: master or worker")
	reduceJobs = flag.Int("reducejobs", 5, "Number of reduce jobs that should be run")

	// Input data settings
	file      = flag.String("file", "files/pg1342.txt", "File to use as input")
	chunkSize = flag.Int("chunksize", 100*1024, "Size of data chunks that should be passed to map jobs(in bytes)")

	// Network settings
	addr   = flag.String("addr", "localhost", "IP address to listen on")
	port   = flag.Int("port", 5000, "TCP port to listen on")
	master = flag.String("master", "localhost:5000", "Master address")

	// Induced failure on Worker
	nOps = flag.Int("fail", 0, "Number of operations to run before failure")
)

// Code Entry Point
func main() {
	var (
		err      error
		task     *mapreduce.Task
		numFiles int
		hostname string
	)

	flag.Parse()

	_ = os.Mkdir(MAP_PATH, os.ModePerm)
	_ = os.Mkdir(RESULT_PATH, os.ModePerm)

	// Initialize mapreduce.Task object with the channels created above and functions
	// mapFunc, shufflerFunc and reduceFunc defined in wordcount.go
	task = &mapreduce.Task{
		Map:           mapFunc,
		Shuffle:       shuffleFunc,
		Reduce:        reduceFunc,
		NumReduceJobs: *reduceJobs,
	}

	log.Println("Running in", *mode, "mode.")

	switch *mode {
	case "sequential":
		// Sequential runs all map and reduce operations in a single core
		// in order. Its used to test Map and Reduce implementations.
		var (
			waitForIt chan bool
			fanIn     chan []byte
			fanOut    chan []mapreduce.KeyValue
		)

		_ = RemoveContents(MAP_PATH)
		_ = RemoveContents(RESULT_PATH)

		// Splits data into chunks with size up to chunkSize
		if numFiles, err = splitData(*file, *chunkSize); err != nil {
			log.Fatal(err)
		}

		fanIn = fanInData(numFiles)
		fanOut, waitForIt = fanOutData()

		task.InputChan = fanIn
		task.OutputChan = fanOut

		mapreduce.RunSequential(task)

		// Wait for fanOut to finish writing data to storage.
		// Legen..
		<-waitForIt
		// ..dary!

	case "distributed":
		// Distributed runs the map and reduce operations in remote workers
		// that are registered with a master.
		switch *nodeType {
		case "master":
			var (
				fanIn chan string
			)

			log.Println("NodeType:", *nodeType)
			log.Println("Reduce Jobs:", *reduceJobs)
			log.Println("Address:", *addr)
			log.Println("Port:", *port)
			log.Println("File:", *file)
			log.Println("Chunk Size:", *chunkSize)

			_ = RemoveContents(MAP_PATH)
			_ = RemoveContents(RESULT_PATH)

			hostname = *addr + ":" + strconv.Itoa(*port)

			// Splits data into chunks with size up to chunkSize
			if numFiles, err = splitData(*file, *chunkSize); err != nil {
				log.Fatal(err)
			}

			// Create fan in and out channels for mapreduce.Task
			fanIn = fanInFilePath(numFiles, hostname)
			task.InputFilePathChan = fanIn

			mapreduce.RunMaster(task, hostname)

		case "worker":
			log.Println("NodeType:", *nodeType)
			log.Println("Address:", *addr)
			log.Println("Port:", *port)
			log.Println("Master:", *master)

			if *nOps > 0 {
				log.Println("Induced failure")
				log.Printf("After %v operations\n", *nOps)
			}

			hostname = *addr + ":" + strconv.Itoa(*port)

			mapreduce.RunWorker(task, hostname, *master, *nOps)
		}
	}
}
