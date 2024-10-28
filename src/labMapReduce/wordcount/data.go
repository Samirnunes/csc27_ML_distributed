package main

import (
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"labMapReduce/mapreduce"
	"log"
	"os"
	"path/filepath"
	"unicode"
)

const (
	MAP_PATH           = "map/"
	RESULT_PATH        = "result/"
	MAP_BUFFER_SIZE    = 10
	REDUCE_BUFFER_SIZE = 10
)

// fanInData will run a goroutine that reads files crated by splitData and share them with
// the mapreduce framework through the one-way channel. It'll buffer data up to
// MAP_BUFFER_SIZE (files smaller than chunkSize) and resume loading them
// after they are read on the other side of the channle (in the mapreduce package)
func fanInData(numFiles int) chan []byte {
	var (
		err    error
		input  chan []byte
		buffer []byte
	)

	input = make(chan []byte, MAP_BUFFER_SIZE)

	go func() {
		for i := 0; i < numFiles; i++ {
			if buffer, err = ioutil.ReadFile(mapFileName(i)); err != nil {
				close(input)
				log.Fatal(err)
			}

			log.Println("Fanning in file", mapFileName(i))
			input <- buffer
		}
		close(input)
	}()
	return input
}

// fanInFilePath will run a goroutine that returns the path of files created during
// splitData. These paths will be sent to remote workers so they can access the data
// and run map operations on it.
func fanInFilePath(numFiles int, fileHostname string) chan string {
	var (
		inputChan chan string
		filePath  string
	)

	inputChan = make(chan string)

	go func() {
		for i := 0; i < numFiles; i++ {
			filePath = mapFileName(i)

			inputChan <- filePath
		}

		close(inputChan)
	}()
	return inputChan
}

// fanOutData will run a goroutine that receive data on the one-way channel and will
// proceed to store it in their final destination. The data will come out after the
// reduce phase of the mapreduce model.
func fanOutData() (chan []mapreduce.KeyValue, chan bool) {
	var (
		err           error
		file          *os.File
		fileEncoder   *json.Encoder
		reduceCounter int
		output        chan []mapreduce.KeyValue
		done          chan bool
	)

	output = make(chan []mapreduce.KeyValue, REDUCE_BUFFER_SIZE)
	done = make(chan bool)

	go func() {
		for v := range output {
			log.Println("Fanning out file", resultFileName(reduceCounter))
			if file, err = os.Create(resultFileName(reduceCounter)); err != nil {
				log.Fatal(err)
			}

			fileEncoder = json.NewEncoder(file)

			for _, value := range v {
				fileEncoder.Encode(value)
			}

			file.Close()
			reduceCounter++
		}

		done <- true
	}()

	return output, done
}

// Reads input file and split it into files smaller than chunkSize.
// CUTCUTCUTCUTCUT!
func splitData(fileName string, chunkSize int) (numMapFiles int, err error) {
	var (
		file         *os.File
		tempFile     *os.File
		chunkBuffer  []byte
		paddedBuffer []byte
		bytesRead    int
		pad          int
	)

	numMapFiles = 0

	if file, err = os.Open(fileName); err != nil {
		return numMapFiles, err
	}
	defer file.Close()

	chunkBuffer = make([]byte, chunkSize)
	paddedBuffer = chunkBuffer

	pad = 0
	for {
		if bytesRead, err = file.Read(paddedBuffer); err != nil {
			if err != io.EOF {
				return numMapFiles, err
			}
		}

		paddedBuffer = chunkBuffer
		bytesRead += pad

		if bytesRead > 0 {
			if bytesRead == chunkSize {
				pad = 0
				for r := rune(paddedBuffer[bytesRead-1-pad]); unicode.IsLetter(r) || unicode.IsNumber(r); r = rune(paddedBuffer[bytesRead-1-pad]) {
					pad++

					if pad == bytesRead {
						pad = 0
						break
					}
				}
			} else {
				pad = chunkSize - bytesRead
			}
			paddedBuffer = chunkBuffer[:chunkSize-pad]

			if tempFile, err = os.Create(mapFileName(numMapFiles)); err != nil {
				return numMapFiles, err
			}
			numMapFiles++
			if _, err = tempFile.Write(paddedBuffer); err != nil {
				tempFile.Close()
				return numMapFiles, err
			}

			tempFile.Close()

			_ = copy(chunkBuffer, chunkBuffer[chunkSize-pad:])
			paddedBuffer = chunkBuffer[pad:]
		}

		if bytesRead < chunkSize {
			break
		}
	}

	return numMapFiles, nil
}

func mapFileName(id int) string {
	return filepath.Join(MAP_PATH, fmt.Sprintf("map-%v", id))
}

func resultFileName(id int) string {
	return filepath.Join(RESULT_PATH, fmt.Sprintf("result-%v", id))
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
