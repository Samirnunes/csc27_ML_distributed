package mapreduce

// KeyValue is the type used to hold elements of maps and reduces results.
type KeyValue struct {
	Key   string
	Value string
}

// Task is the exposed struct of the Framework that the calling code should initialize
// with the specific implementation of the operation.
type Task struct {
	// MapReduce functions
	Map     MapFunc
	Shuffle ShuffleFunc
	Reduce  ReduceFunc

	// Jobs
	NumReduceJobs int
	NumMapFiles   int

	// Channels for data
	InputChan  chan []byte
	OutputChan chan []KeyValue

	// Channels for filepaths
	InputFilePathChan  chan string
	OutputFilePathChan chan string
}

type (
	MapFunc     func([]byte) []KeyValue
	ReduceFunc  func([]KeyValue) []KeyValue
	ShuffleFunc func(*Task, string) int
)
