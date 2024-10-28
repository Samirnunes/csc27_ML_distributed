package mapreduce

import (
	"log"
	"net"
	"net/rpc"
	"sync"
)

const (
	IDLE_WORKER_BUFFER     = 100
	RETRY_OPERATION_BUFFER = 100
)

type Master struct {
	// Task
	task *Task

	// Network
	address   string
	rpcServer *rpc.Server
	listener  net.Listener

	// Workers handling
	workersMutex sync.Mutex
	workers      map[int]*RemoteWorker
	totalWorkers int // Used to generate unique ids for new workers

	idleWorkerChan     chan *RemoteWorker
	failedWorkerChan   chan *RemoteWorker
	retryOperationChan chan *Operation
}

type Operation struct {
	proc     string
	id       int
	filePath string
}

// Construct a new Master struct
func newMaster(address string) (master *Master) {
	master = new(Master)
	master.address = address
	master.workers = make(map[int]*RemoteWorker, 0)
	master.idleWorkerChan = make(chan *RemoteWorker, IDLE_WORKER_BUFFER)
	master.failedWorkerChan = make(chan *RemoteWorker, IDLE_WORKER_BUFFER)
	master.retryOperationChan = make(chan *Operation, RETRY_OPERATION_BUFFER)
	master.totalWorkers = 0
	return
}

// acceptMultipleConnections will handle the connections from multiple workers.
func (master *Master) acceptMultipleConnections() {
	var (
		err     error
		newConn net.Conn
	)

	log.Printf("Accepting connections on %v\n", master.listener.Addr())

	for {
		newConn, err = master.listener.Accept()

		if err == nil {
			go master.handleConnection(&newConn)
		} else {
			log.Println("Failed to accept connection. Error: ", err)
			break
		}
	}

	log.Println("Stopped accepting connections.")
}

// handleFailingWorkers will handle workers that fail during an operation.
func (master *Master) handleFailingWorkers() {
	for failedWorker := range master.failedWorkerChan {
		master.workersMutex.Lock()
		delete(master.workers, failedWorker.id)
		master.workersMutex.Unlock()
		log.Printf("Worker %d has failed and has been removed from the workers list.\n", failedWorker.id)
	}
}

// Handle a single connection until it's done, then closes it.
func (master *Master) handleConnection(conn *net.Conn) error {
	master.rpcServer.ServeConn(*conn)
	(*conn).Close()
	return nil
}
