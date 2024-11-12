package mapreduce

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"time"
)

const (
	REDUCE_PATH = "reduce/"
	RESULT_PATH = "result/"

	OPEN_FILE_MAX_RETRY = 3
)

// Returns the name of files created after merge
func mergeReduceName(idReduce int) string {
	return fmt.Sprintf("reduce-%v", idReduce)
}

// Returns the name of files created after map
func reduceName(idMap int, idReduce int) string {
	return fmt.Sprintf("reduce-%v-%v", idMap, idReduce)
}

// Store result from map operation locally.
// This will store the result from all the map calls.
func storeLocal(task *Task, idMapTask int, data []KeyValue) {
	var (
		err         error
		file        *os.File
		fileEncoder *json.Encoder
	)

	for r := 0; r < task.NumReduceJobs; r++ {
		file, err = os.Create(filepath.Join(REDUCE_PATH, reduceName(idMapTask, r)))
		if err != nil {
			log.Fatal(err)
		}

		fileEncoder = json.NewEncoder(file)
		for _, kv := range data {
			if task.Shuffle(task, kv.Key) == r {
				err = fileEncoder.Encode(&kv)
				if err != nil {
					log.Fatal(err)
				}
			}
		}
		file.Sync()
		file.Close()
	}
}

// Merge the result from all the map operations by reduce job id.
func mergeMapLocal(task *Task, mapCounter int) {
	var (
		err              error
		file             *os.File
		fileDecoder      *json.Decoder
		mergeFile        *os.File
		mergeFileEncoder *json.Encoder
	)

	for r := 0; r < task.NumReduceJobs; r++ {
		if mergeFile, err = os.Create(filepath.Join(REDUCE_PATH, mergeReduceName(r))); err != nil {
			log.Fatal(err)
		}

		mergeFileEncoder = json.NewEncoder(mergeFile)

		for m := 0; m < mapCounter; m++ {
			for i := 0; i < OPEN_FILE_MAX_RETRY; i++ {
				if file, err = os.Open(filepath.Join(REDUCE_PATH, reduceName(m, r))); err == nil {
					break
				}
				log.Printf("(%v/%v) Failed to open file %v. Retrying in 1 second...", i+1, OPEN_FILE_MAX_RETRY, filepath.Join(REDUCE_PATH, reduceName(m, r)))
				time.Sleep(time.Second)
			}

			if err != nil {
				log.Fatal(err)
			}

			if file, err = os.Open(filepath.Join(REDUCE_PATH, reduceName(m, r))); err != nil {
				log.Fatal(err)
			}

			fileDecoder = json.NewDecoder(file)

			for {
				var kv KeyValue
				err = fileDecoder.Decode(&kv)
				if err != nil {
					break
				}

				mergeFileEncoder.Encode(&kv)
			}
			file.Sync()
			file.Close()
		}

		mergeFile.Sync()
		mergeFile.Close()
	}
}

// Merge the result from all the map operations by reduce job id.
func mergeReduceLocal(reduceCounter int) {
	var (
		err              error
		file             *os.File
		fileDecoder      *json.Decoder
		mergeFile        *os.File
		mergeFileEncoder *json.Encoder
	)

	if mergeFile, err = os.Create(filepath.Join(RESULT_PATH, "result-final.txt")); err != nil {
		log.Fatal(err)
	}

	defer mergeFile.Sync()
	defer mergeFile.Close()

	mergeFileEncoder = json.NewEncoder(mergeFile)

	for r := 0; r < reduceCounter; r++ {
		for i := 0; i < OPEN_FILE_MAX_RETRY; i++ {
			if file, err = os.Open(resultFileName(r)); err == nil {
				break
			}
			log.Printf("(%v/%v) Failed to open file %v. Retrying in 1 second...", i+1, OPEN_FILE_MAX_RETRY, resultFileName(r))
			time.Sleep(time.Second)
		}

		if err != nil {
			log.Fatal(err)
		}

		fileDecoder = json.NewDecoder(file)

		for {
			var kv KeyValue
			err = fileDecoder.Decode(&kv)
			if err != nil {
				break
			}

			mergeFileEncoder.Encode(&kv)
		}
		file.Sync()
		file.Close()
	}
}

// Load data for reduce jobs.
func loadLocal(idReduce int) (data []KeyValue) {
	var (
		err         error
		file        *os.File
		fileDecoder *json.Decoder
	)

	if file, err = os.Open(filepath.Join(REDUCE_PATH, mergeReduceName(idReduce))); err != nil {
		log.Fatal(err)
	}

	fileDecoder = json.NewDecoder(file)

	data = make([]KeyValue, 0)

	for {
		var kv KeyValue
		if err = fileDecoder.Decode(&kv); err != nil {
			break
		}

		data = append(data, kv)
	}

	file.Close()
	return data
}

func RemoveContents(dir string) error {
	d, err := os.Open(dir)
	if err != nil {
		return err
	}
	defer d.Close()
	names, err := d.Readdirnames(-1)
	if err != nil {
		return err
	}
	for _, name := range names {
		err = os.RemoveAll(filepath.Join(dir, name))
		if err != nil {
			return err
		}
	}
	return nil
}

// FanIn is a pattern that will return a channel in which the goroutines generated here will keep
// writing until the loop is done.
// This is used to generate the name of all the reduce files.
func fanReduceFilePath(numReduceJobs int) chan string {
	var (
		outputChan chan string
		filePath   string
	)

	outputChan = make(chan string)

	go func() {
		for i := 0; i < numReduceJobs; i++ {
			filePath = filepath.Join(REDUCE_PATH, mergeReduceName(i))

			outputChan <- filePath
		}

		close(outputChan)
	}()
	return outputChan
}

// Support function to generate the name of result files
func resultFileName(id int) string {
	return filepath.Join(RESULT_PATH, fmt.Sprintf("result-%v", id))
}
