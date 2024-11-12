package main

import (
	//"fmt"
	"hash/fnv"
	"labMapReduce/mapreduce"
	"strconv"
	"strings"
	"unicode"
)

// mapFunc is called for each array of bytes read from the splitted files. For wordcount
// it should convert it into an array and parses it into an array of KeyValue that have
// all the words in the input.

func mapFunc(input []byte) (result []mapreduce.KeyValue) {
	var (
		text          string
		delimiterFunc func(c rune) bool
		words         []string
	)

	text = string(input)

	delimiterFunc = func(c rune) bool {
		return !unicode.IsLetter(c) && !unicode.IsNumber(c)
	}

	words = strings.FieldsFunc(text, delimiterFunc)
	result = make([]mapreduce.KeyValue, 0)

	for _, word := range words {
		lowerWord := strings.ToLower(word)
		result = append(result, mapreduce.KeyValue{Key: lowerWord, Value: "1"})
	}

	return result
}

// reduceFunc is called for each merged array of KeyValue resulted from all map jobs.
// It should return a similar array that summarizes all similar keys in the input.
func reduceFunc(input []mapreduce.KeyValue) (result []mapreduce.KeyValue) {
	wordCount := make(map[string]int)

	for _, kv := range input {
		count, err := strconv.Atoi(kv.Value)
		if err != nil {
			continue
		}

		wordCount[kv.Key] += count
	}

	result = make([]mapreduce.KeyValue, 0, len(wordCount))
	for word, count := range wordCount {
		result = append(result, mapreduce.KeyValue{Key: word, Value: strconv.Itoa(count)})
	}

	return result
}

// shuffleFunc will shuffle map job results into different job tasks. It should assert that
// the related keys will be sent to the same job, thus it will hash the key (a word) and assert
// that the same hash always goes to the same reduce job.
// http://stackoverflow.com/questions/13582519/how-to-generate-hash-number-of-a-string-in-go
func shuffleFunc(task *mapreduce.Task, key string) (reduceJob int) {
	h := fnv.New32a()
	h.Write([]byte(key))
	return int(h.Sum32() % uint32(task.NumReduceJobs))
}
